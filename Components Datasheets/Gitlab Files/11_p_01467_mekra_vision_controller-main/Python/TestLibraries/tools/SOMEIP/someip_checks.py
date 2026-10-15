#******************************************************************************
# -*- coding: utf-8 -*-
# File : someip_checks.py
# Task : Shared steps and checks for the SOME/IP test cases
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 09.09.2026 | Martin Oeder  | initial
#******************************************************************************
"""
What the SOME/IP test cases share, on top of camera_steps.

camera_steps covers the bench and the well-formed requests. This module adds the
parts every SOME/IP test case wrote out for itself so far:

  * build_request()           one request builder, every header field settable
  * check_error_response()    the five verdicts a rejected request gets
  * getCamStatus / lockedBy   the payload evaluation the lock test cases share
  * foreign_client()          a second client on another source address

The module only writes verdicts into the test result, it never decides how long a
test waits or which values it sends: that stays in the test case.

Import from the test libraries:  from tools.SOMEIP import someip_checks as sc
Import next to the test case:    import someip_checks as sc

The import path has to match where the file actually is. Keep one copy only,
otherwise the two drift apart.
"""
from time import sleep

from tools.SOMEIP.someip_client import SomeipClient
from tools.SOMEIP.someip_packet import SomeipPacket
from tools.helpFunctions import camera_steps as cs
from tools.helpFunctions import helperModule


# #############################################################################
# SOME/IP return codes
# #############################################################################
RC_E_OK = 0x00
RC_E_NOT_OK = 0x01
RC_E_UNKNOWN_SERVICE = 0x02
RC_E_UNKNOWN_METHOD = 0x03
RC_E_WRONG_PROTOCOL_VERSION = 0x07
RC_E_WRONG_INTERFACE_VERSION = 0x08
RC_E_MALFORMED_MESSAGE = 0x09
RC_E_WRONG_MESSAGE_TYPE = 0x0A
RC_E_LOCKED_BY_FOREIGN_INSTANCE = 0x20
RC_E_LOCK_EXPIRED = 0x21
RC_E_NOT_LOCKED = 0x22
RC_E_INVALID_CONTROL_INDEX = 0x35
RC_E_INVALID_BLOCK_DEFINITION = 0x51


# #############################################################################
# Expectations for a rejected request
# #############################################################################
MSG_TYPE_ERROR = 0x81
MSG_TYPE_RESPONSE = 0x80
ERROR_RESPONSE_LENGTH = 0x08        # error response carries no payload
MAX_ERROR_RESPONSE_MS = 100         # max response delay for an error response
MAX_RESPONSE_MS = 100               # max response delay for a positive response


# #############################################################################
# Addresses
# #############################################################################
def ip_to_hex(ip):
    """Dotted IPv4 address as the 8-character hex string of the lockedBy field."""
    return "".join("%02x" % int(octet) for octet in ip.split("."))


# #############################################################################
# getCamStatus payload
# #############################################################################
# The payload is 7 bytes, so the response carries a length field of 0x0F:
#   lockedBy (4 bytes) | power status (1 byte) | imager temperature (2 bytes)
LOCKED_BY_NONE = "00000000"                 # nobody holds the exclusive lock
LOCKED_BY_CLIENT = ip_to_hex(cs.CLIENT_IP)  # this test PC holds it
POWER_STATUS_WILDCARD = "yy"        # power status byte, not evaluated
TEMP_PLACEHOLDER = "0000"           # imager temperature, not evaluated either,
                                    # it only pads the mask to the right length
WILDCARD_CHARS = "yz"               # mask characters that mean "not evaluated"


def locked_by_mask(locked_by):
    """The getCamStatus payload mask for one lockedBy value."""
    return locked_by + POWER_STATUS_WILDCARD + TEMP_PLACEHOLDER


# #############################################################################
# Requests
# #############################################################################
def build_request(method_id, length, payload=None, service_id=None,
                  request_id=None, protocol_version=0x01, interface_version=0x01,
                  message_type=0x00, return_code=0x00):
    """Build a SOME/IP request with every header field settable.

    cs.build_request() always sends a well-formed header, the negative test cases
    need single fields corrupted, which is what the keyword arguments are for.
    Length and payload are taken as given even when they contradict each other,
    so a framing error can be provoked on purpose.
    """
    return SomeipPacket(
        service_id=cs.SERVICE_ID if service_id is None else service_id,
        method_id=method_id,
        length=length,
        request_id=cs.REQUEST_ID if request_id is None else request_id,
        protocol_version=protocol_version,
        interface_version=interface_version,
        message_type=message_type,
        return_code=return_code,
        payload=payload)


def header_echo(packet):
    """Header fields the camera has to mirror back, as one comparable string.

    Reads a request the same way as a response, so the expectation does not have
    to be written out a second time: header_echo(request) is what the response
    has to answer with, whatever the test case put into those fields.
    """
    return "%s %s %s %s %s" % (packet.get_service_id(), packet.get_method_id(),
                               packet.get_request_id(),
                               packet.get_protocol_version(),
                               packet.get_interface_version())


# #############################################################################
# Rejected requests
# #############################################################################
def check_error_response(testresult, request, rx, delay_ms, expected_rc, descr,
                         max_delay_ms=MAX_ERROR_RESPONSE_MS):
    """Verdicts on one rejected request: message type, return code, length
    without payload, echoed header and response delay."""
    if rx is None:
        testresult.append(["%s: no response from camera" % descr, "FAILED"])
        return False

    msg_type = rx.get_message_type()
    ret_code = rx.get_return_code()
    resp_length = rx.get_length()
    payload = rx.get_payload()

    testresult.addInfo("Response: %s | payload %s | %.1f ms"
                       % (" ".join(SomeipPacket.get_packet_stream(rx)),
                          payload, delay_ms))

    passed = []

    passed.append(msg_type == "%02x" % MSG_TYPE_ERROR)
    testresult.append(["Message type is 0x%02X (ERROR), received 0x%s"
                       % (MSG_TYPE_ERROR, msg_type),
                       "PASSED" if passed[-1] else "FAILED"])

    passed.append(ret_code == "%02x" % expected_rc)
    testresult.append(["Return code is 0x%02X (%s), received 0x%s (%s)"
                       % (expected_rc,
                          helperModule.get_human_readable_return_code(expected_rc),
                          ret_code,
                          helperModule.get_human_readable_return_code(ret_code)),
                       "PASSED" if passed[-1] else "FAILED"])

    passed.append(resp_length == "%08x" % ERROR_RESPONSE_LENGTH and payload is None)
    testresult.append(["Length field is 0x%08X and no payload is attached, "
                       "received 0x%s / payload %s"
                       % (ERROR_RESPONSE_LENGTH, resp_length, payload),
                       "PASSED" if passed[-1] else "FAILED"])

    expected_echo = header_echo(request)
    actual_echo = header_echo(rx)
    passed.append(actual_echo == expected_echo)
    testresult.append(["Header echoed unchanged (service, method, request id, "
                       "protocol and interface version): %s (expected %s)"
                       % (actual_echo, expected_echo),
                       "PASSED" if passed[-1] else "FAILED"])

    passed.append(delay_ms <= max_delay_ms)
    testresult.append(["Error response delay %.1f ms is within %d ms"
                       % (delay_ms, max_delay_ms),
                       "PASSED" if passed[-1] else "FAILED"])

    return all(passed)


def send_and_check_error(testresult, client, request, expected_rc, descr):
    """Send one malformed request and verify its error response."""
    testresult.addSubHeader(descr)
    rx, delay_ms = cs.send_timed(client, request)
    return check_error_response(testresult, request, rx, delay_ms, expected_rc,
                                descr)


def send_and_check_negative(testresult, client, request, method_id, expected_rc,
                            descr):
    """Send a request that has to be rejected, verdict on method, message type
    and return code only.

    The exclusive lock test cases specify no length, echo or delay for their
    negative responses, so they use this instead of check_error_response().
    Tolerates client=None, so a missing second client is reported as such.
    """
    if client is None:
        testresult.append(["%s not sent, client is not available" % descr,
                           "FAILED"])
        return False

    rx = cs.send(client, request)
    return cs.negative_response(testresult, rx, method_id, expected_rc, descr)


def check_no_payload(testresult, rx, descr,
                     expected_length=ERROR_RESPONSE_LENGTH):
    """Verdict on a response that carries no payload.

    The length field is back to the 8 bytes of the header and no payload is
    attached. Some test steps state "no Payload" next to a longer length field,
    which contradicts itself: 8 bytes is what a response without payload has.
    """
    if rx is None:
        testresult.append(["%s: no response to check the length of" % descr,
                           "FAILED"])
        return False

    length = rx.get_length()
    payload = rx.get_payload()
    passed = (length == "%08x" % expected_length and payload is None)
    testresult.append(["Length field is 0x%08X and no payload is attached (%s): "
                       "received 0x%s / payload %s"
                       % (expected_length, descr, length, payload),
                       "PASSED" if passed else "FAILED"])
    return passed


# #############################################################################
# Response delay
# #############################################################################
def send_and_check_delay(testresult, client, request, method_id, descr,
                         max_delay_ms=MAX_RESPONSE_MS):
    """Send one request, verdict on the positive response and on its delay.

    cs.send_timed() times every attempt on its own, so a first request lost
    while the address resolution settles does not inflate the reported delay.

    Returns the response packet, so the caller can evaluate its payload too, or
    None when the camera did not answer at all.
    """
    rx, delay_ms = cs.send_timed(client, request)
    if rx is None:
        cs.positive_response(testresult, rx, method_id, descr)
        return None

    testresult.addInfo("Response: %s | payload %s | %.1f ms"
                       % (" ".join(SomeipPacket.get_packet_stream(rx)),
                          rx.get_payload(), delay_ms))
    cs.positive_response(testresult, rx, method_id, descr)
    testresult.append(["Response delay %.1f ms is within %d ms"
                       % (delay_ms, max_delay_ms),
                       "PASSED" if delay_ms <= max_delay_ms else "FAILED"])
    return rx


# #############################################################################
# getCamStatus and the exclusive lock
# #############################################################################
def get_cam_status(testresult, client, descr):
    """getCamStatus: return the response packet, verdict on message type and
    return code only, the payload content is evaluated separately."""
    rx = cs.send(client, cs.build_request(cs.M_GET_CAM_STATUS, 0x08))
    cs.positive_response(testresult, rx, cs.M_GET_CAM_STATUS, descr)
    return rx


def check_payload_mask(testresult, rx, expected_mask, descr, ignore_last_bytes=2):
    """Compare a response payload against a hex mask.

    Mask characters in WILDCARD_CHARS mean "not evaluated" (the power status
    byte). The last ignore_last_bytes bytes are excluded from the comparison as
    well, only their presence is checked through the payload length: that is the
    imager temperature, which none of these test cases evaluates.
    """
    payload = rx.get_payload() if rx is not None else None
    if payload is None:
        testresult.append(["%s: no payload to evaluate (expected 0x%s)"
                           % (descr, expected_mask), "FAILED"])
        return False

    ignore_chars = ignore_last_bytes * 2
    checked_payload = payload[:-ignore_chars] if ignore_chars else payload
    checked_mask = expected_mask[:-ignore_chars] if ignore_chars else expected_mask

    passed = (len(payload) == len(expected_mask)
              and all(m in WILDCARD_CHARS or a == m
                      for a, m in zip(checked_payload, checked_mask)))
    testresult.append(["Payload shall match 0x%s ('%s' = ignored, last %d byte(s) "
                       "excluded from evaluation): received 0x%s (%s)"
                       % (expected_mask, "'/'".join(WILDCARD_CHARS),
                          ignore_last_bytes, payload, descr),
                       "PASSED" if passed else "FAILED"])
    return passed


def check_lock_state(testresult, client, locked_by, descr):
    """getCamStatus and verify which address holds the exclusive lock.

    locked_by is the expected lockedBy field, LOCKED_BY_NONE or the hex form of
    an address, e.g. LOCKED_BY_CLIENT or ip_to_hex(CLIENT_IP_2).
    """
    rx = get_cam_status(testresult, client, "getCamStatus (%s)" % descr)
    return check_payload_mask(testresult, rx, locked_by_mask(locked_by),
                              "lockedBy 0x%s (%s), power status and imager "
                              "temperature ignored" % (locked_by, descr))


def foreign_client(testresult, client_ip, reference_client):
    """Open a further SOME/IP client on another source address.

    The camera identifies the holder of the exclusive lock by its IP address, so
    a client that has to appear as a foreign instance needs its own address.

    Returns None when the address is not configured on the test PC, so the test
    case reports the missing bench prerequisite instead of an opaque ValueError.
    """
    try:
        client = SomeipClient(
            client_ip=client_ip,
            server_ip=reference_client.serverIP,
            client_source_port="0",
            client_destination_port=reference_client.destinationPort)
    except Exception as ex:
        testresult.append(["Client on %s cannot be opened (%s) -> the address has "
                           "to exist as a secondary address on the test PC"
                           % (client_ip, ex), "FAILED"])
        return None

    cs.log_endpoint(testresult, client)
    return client


# #############################################################################
# Timeline
# #############################################################################
def wait(testresult, seconds, descr):
    """Sleep for the given time and log why, so the report shows the timeline."""
    if seconds >= 3600:
        testresult.addInfo("Waiting %.1f s (%.2f h): %s"
                           % (seconds, seconds / 3600.0, descr))
    else:
        testresult.addInfo("Waiting %.1f s: %s" % (seconds, descr))
    sleep(seconds)


# def close_clients(*clients):
#     """Close every client that was opened, ignoring the ones that never were."""
#     for client in clients:
#         if client is not None:
#             client.close_socket()

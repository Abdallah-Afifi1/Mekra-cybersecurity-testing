#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92898-SOMEIP_message_header-validation_service_id.py
# Task : Validation of Service ID
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 08.09.2026 | Martin Oeder  | initial
# 1.1.0  | 10.09.2026 | Martin Oeder  | shared steps moved to someip_checks
#******************************************************************************
#******************************************************************************
# """Deviations from the test steps, so the report states them."""
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92898"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Every request uses this invalid Service ID, combined with one further defect.
INVALID_SERVICE_ID = 0x433E

# All cases expect E_UNKNOWN_SERVICE, since the Service ID is validated before
# Protocol Version, Interface Version, Message Type, Return Code and Method ID.
# The last case is the exception: a Length that does not match the actual number
# of bytes on the wire outranks even the Service ID check (raw framing comes
# first), so it alone expects E_MALFORMED_MESSAGE. "request" holds the header
# fields as they go on the wire, the Service ID is added in the loop below.
MALFORMED_REQUESTS = [
    {
        "descr": "All fields invalid except length",
        "request": dict(method_id=0x1001, length=0x00000008, payload=None,
                        protocol_version=0x11, interface_version=0x11,
                        message_type=0xA0, return_code=0xA0),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Service ID invalid and payload longer than expected for the "
                 "method",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000009,
                        payload=bytes([0x12]), protocol_version=0x01,
                        interface_version=0x01, message_type=0x00,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Service ID and protocol version invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=None, protocol_version=0x11,
                        interface_version=0x01, message_type=0x00,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Service ID and interface version invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=None, protocol_version=0x01,
                        interface_version=0x21, message_type=0x00,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Service ID and message type invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=None, protocol_version=0x01,
                        interface_version=0x01, message_type=0xFF,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Service ID and return code invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=None, protocol_version=0x01,
                        interface_version=0x01, message_type=0x00,
                        return_code=0xED),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Service ID and method ID invalid",
        "request": dict(method_id=0xF002, length=0x00000008, payload=None,
                        protocol_version=0x01, interface_version=0x01,
                        message_type=0x00, return_code=0x00),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Service ID invalid and length for the method invalid, with no "
                 "payload actually attached (framing outranks the Service ID "
                 "check)",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x0000000A,
                        payload=None, protocol_version=0x01,
                        interface_version=0x01, message_type=0x00,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
]


# #############################################################################
# Test
# #############################################################################
with TestEnv(testcase_id=TESTCASE_ID) as testenv:

    testresult = testenv.getResults()
    psu = testenv.getPSU()
    client = None

    try:
        # #####################################################################
        testresult.addHeader("Preconditions")
        # #####################################################################
        cs.log_dut_config(testresult)
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        # The first request of a session can be lost, so warm up before measuring.
        cs.service_answers(testresult, client, cs.M_GET_CAM_STATUS)

        # #####################################################################
        testresult.addHeader("Malformed requests are rejected with the expected "
                             "return code")
        # #####################################################################
        for case in MALFORMED_REQUESTS:
            someipcheck.send_and_check_error(testresult, client,
                                    someipcheck.build_request(service_id=INVALID_SERVICE_ID,
                                                     **case["request"]),
                                    case["expected_return_code"], case["descr"])

        # #####################################################################
        testresult.addHeader("Postcondition: a well-formed request still returns "
                             "E_OK")
        # #####################################################################
        rx = cs.send(client, cs.build_request(cs.M_GET_CAM_STATUS, 0x08))
        cs.positive_response(testresult, rx, cs.M_GET_CAM_STATUS,
                             "getCamStatus (0x%04X) with a valid header"
                             % cs.M_GET_CAM_STATUS)

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        SomeipClient.close_clients(client)

        if POWER_OFF_AT_END:
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

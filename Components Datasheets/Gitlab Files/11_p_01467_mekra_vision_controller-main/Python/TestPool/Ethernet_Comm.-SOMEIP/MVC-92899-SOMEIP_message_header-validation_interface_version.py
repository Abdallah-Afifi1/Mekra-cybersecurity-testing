#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92899-SOMEIP_message_header-validation_interface_version.py
# Task : Validation of Interface Version
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
# Test step 7 & 8: Protocol Version: Expected result should be 0x01 instead of 0xAD
# Test step 8: Message Type: Expected result should be 0x80 instead of 0x81
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92899"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Every request uses an invalid Interface Version, combined with one further
# defect. All cases expect E_WRONG_INTERFACE_VERSION, since Interface Version is
# validated before Message Type, Return Code and Method ID. The last case is the
# exception: a Length that does not match the actual number of bytes on the wire
# outranks even the Interface Version check (raw framing comes first), so it
# alone expects E_MALFORMED_MESSAGE. "request" holds the header fields as they go
# on the wire.
MALFORMED_REQUESTS = [
    {
        "descr": "All fields invalid except Service ID, Length and Protocol "
                 "version",
        "request": dict(method_id=0x1001, length=0x00000008, payload=None,
                        protocol_version=0x01, interface_version=0x11,
                        message_type=0xA0, return_code=0xA0),
        "expected_return_code": someipcheck.RC_E_WRONG_INTERFACE_VERSION,
    },
    {
        "descr": "Interface version and message type invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=None, protocol_version=0x01,
                        interface_version=0x38, message_type=0xE0,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_WRONG_INTERFACE_VERSION,
    },
    {
        "descr": "Interface version and return code invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=None, protocol_version=0x01,
                        interface_version=0x17, message_type=0x00,
                        return_code=0x09),
        "expected_return_code": someipcheck.RC_E_WRONG_INTERFACE_VERSION,
    },
    {
        "descr": "Interface version and Method ID invalid",
        "request": dict(method_id=0xA123, length=0x00000008, payload=None,
                        protocol_version=0x01, interface_version=0x02,
                        message_type=0x00, return_code=0x00),
        "expected_return_code": someipcheck.RC_E_WRONG_INTERFACE_VERSION,
    },
    {
        "descr": "Interface version invalid and length for Method ID invalid, "
                 "with no payload actually attached (framing outranks the "
                 "Interface Version check)",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000108,
                        payload=None, protocol_version=0x01,
                        interface_version=0x5A, message_type=0x00,
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
                                    someipcheck.build_request(**case["request"]),
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

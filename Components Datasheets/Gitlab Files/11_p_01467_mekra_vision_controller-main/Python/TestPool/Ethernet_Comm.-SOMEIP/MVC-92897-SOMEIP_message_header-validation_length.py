#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92897-SOMEIP_message_header-validation_length.py
# Task : Validation header length
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
# Test step 4: Protocol and Interface Version: Check expected result in all teststeps
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92897"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Every case except the first sends a declared Length field that does not match
# the number of bytes actually on the wire (too much or too little payload
# attached, or a Length below the mandatory 8-byte header), combined with a
# further defect elsewhere. A raw framing mismatch like this outranks every other
# header defect, including an invalid Protocol Version (case 1, where the framing
# is internally consistent, is rejected on the next check down: Protocol Version).
# "request" holds the header fields as they go on the wire.
MALFORMED_REQUESTS = [
    {
        "descr": "All fields invalid except Service ID (framing itself is "
                 "consistent)",
        "request": dict(method_id=0x1001, length=0x00000009,
                        payload=bytes([0x01]), protocol_version=0x11,
                        interface_version=0x11, message_type=0xA0,
                        return_code=0xA0),
        "expected_return_code": someipcheck.RC_E_WRONG_PROTOCOL_VERSION,
    },
    {
        "descr": "Payload longer than declared and protocol version invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=bytes.fromhex("1111"), protocol_version=0x02,
                        interface_version=0x01, message_type=0x00,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
    {
        "descr": "Payload longer than declared and interface version invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=bytes.fromhex("123456"), protocol_version=0x01,
                        interface_version=0x02, message_type=0x00,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
    {
        "descr": "Payload longer than declared and message type invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=bytes.fromhex("12345678"), protocol_version=0x01,
                        interface_version=0x01, message_type=0x81,
                        return_code=0x00),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
    {
        "descr": "Length below the mandatory header and return code invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000007,
                        payload=None, protocol_version=0x01,
                        interface_version=0x01, message_type=0x00,
                        return_code=0x09),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
    {
        "descr": "Payload shorter than declared and length for Method ID invalid",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x0000000A,
                        payload=bytes([0x77]), protocol_version=0x01,
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

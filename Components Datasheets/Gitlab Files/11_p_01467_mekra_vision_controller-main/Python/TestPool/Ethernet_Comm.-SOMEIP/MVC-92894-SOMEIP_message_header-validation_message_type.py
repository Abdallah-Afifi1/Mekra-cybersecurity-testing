#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92894-SOMEIP_message_header-validation_message_type.py
# Task : Validation message type
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
# Test step 6: Service ID should be 0x433e
# Test step 7: Protocol Version should be 0x01 and message type should be 0x80
# Test step 3-5: Defect: Response of Return Code should be 0x0A (Message Type Error)
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92894"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Each request sends an invalid Message Type (a REQUEST always has to carry 0x00),
# combined with a different additional defect. Method ID / length / return code are
# taken as-is even when they do not agree with each other, to see which defect the
# camera reports. Service ID, Request ID, Protocol and Interface Version are always
# valid and are expected to be echoed back unchanged. "request" holds the header
# fields as they go on the wire.
MALFORMED_REQUESTS = [
    {
        "descr": "All fields invalid except Service ID, Length, Protocol and "
                 "Interface version",
        "request": dict(method_id=0xBEEF, length=0x00000008, payload=None,
                        message_type=0x33, return_code=0x44),
        "expected_return_code": someipcheck.RC_E_WRONG_MESSAGE_TYPE,
    },
    {
        "descr": "Message type and return code invalid (Method ID valid)",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=None, message_type=0x55, return_code=0x77),
        "expected_return_code": someipcheck.RC_E_WRONG_MESSAGE_TYPE,
    },
    {
        "descr": "Message type and Method ID invalid",
        "request": dict(method_id=0xA123, length=0x00000008, payload=None,
                        message_type=0xFF, return_code=0x00),
        "expected_return_code": someipcheck.RC_E_WRONG_MESSAGE_TYPE,
    },
    {
        "descr": "Message type and length invalid (Method ID valid)",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000001,
                        payload=None, message_type=0x01, return_code=0x00),
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

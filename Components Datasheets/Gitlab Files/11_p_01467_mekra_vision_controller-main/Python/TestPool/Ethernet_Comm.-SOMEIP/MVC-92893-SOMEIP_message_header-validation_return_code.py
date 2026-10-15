#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92893-SOMEIP_message_header-validation_return_code.py
# Task : Validaton of return code
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
# Open Points:
# Test step 6: rework of test steps in Polarion: Length should be set to 0x...0A
#
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92893"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Each request sends an invalid Return Code (a REQUEST always has to carry 0x00),
# combined with a different additional defect. Method ID / length / payload are
# taken as-is even when they do not agree with each other, to see which defect the
# camera reports. "request" holds the header fields as they go on the wire.
MALFORMED_REQUESTS = [
    {
        "descr": "Method ID, length and return code invalid",
        "request": dict(method_id=0xDEAD, length=0x00000078, payload=None,
                        return_code=0x07),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
    {
        "descr": "Method ID and return code invalid",
        "request": dict(method_id=0xFFFF, length=0x00000008, payload=None,
                        return_code=0x01),
        "expected_return_code": someipcheck.RC_E_NOT_OK,
    },
    {
        "descr": "Length and return code invalid (Method ID valid)",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000000,
                        payload=None, return_code=0x07),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
    {
        "descr": "Payload and return code invalid (Method ID and length valid)",
        "request": dict(method_id=cs.M_GET_CAM_STATUS, length=0x00000008,
                        payload=bytes.fromhex("1234"), return_code=0x07),
        "expected_return_code": someipcheck.RC_E_NOT_OK,
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

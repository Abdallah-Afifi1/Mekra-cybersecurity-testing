#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92895-SOMEIP_message_header-validation_length_for_methode_id.py
# Task : Validation length for methode id
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
# Test step 5: Service ID: Expected result should be 0x433e instead of 0x433f
# Test step 6: Method ID: Expected result should be 0x0000 instead of 0x0002
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92895"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Every request sends a Length that does not match what getCamStatus expects
# (0x09 with a 1-byte payload instead of 0x08 with none), combined with at most one
# further defect. This shows the priority the camera gives each check: Service ID
# and Method ID are validated before Interface Version, which in turn is validated
# before the per-method Length check. "request" holds the header fields as they go
# on the wire.
MALFORMED_REQUESTS = [
    {
        "descr": "Length for Method ID invalid",
        "request": dict(service_id=cs.SERVICE_ID, method_id=cs.M_GET_CAM_STATUS,
                        length=0x00000009, interface_version=0x01,
                        payload=bytes([0x00])),
        "expected_return_code": someipcheck.RC_E_MALFORMED_MESSAGE,
    },
    {
        "descr": "Length for Method ID and interface version invalid",
        "request": dict(service_id=cs.SERVICE_ID, method_id=cs.M_GET_CAM_STATUS,
                        length=0x00000009, interface_version=0x02,
                        payload=bytes([0x00])),
        "expected_return_code": someipcheck.RC_E_WRONG_INTERFACE_VERSION,
    },
    {
        "descr": "Length for Method ID and service ID invalid",
        "request": dict(service_id=0x433E, method_id=cs.M_GET_CAM_STATUS,
                        length=0x00000009, interface_version=0x01,
                        payload=bytes([0x00])),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_SERVICE,
    },
    {
        "descr": "Length for Method ID and method ID invalid",
        "request": dict(service_id=cs.SERVICE_ID, method_id=0x0000,
                        length=0x00000009, interface_version=0x01,
                        payload=bytes([0x00])),
        "expected_return_code": someipcheck.RC_E_UNKNOWN_METHOD,
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

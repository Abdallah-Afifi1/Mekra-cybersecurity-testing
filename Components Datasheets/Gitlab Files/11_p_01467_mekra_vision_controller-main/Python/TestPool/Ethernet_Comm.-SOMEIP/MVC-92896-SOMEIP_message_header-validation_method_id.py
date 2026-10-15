#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92896-SOMEIP_message_header-validation_method_id.py
# Task : Validation methode id
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
# Test step 4: Protocol Version: Expected result should be 0x01 instead of 0xAD
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92896"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Unknown Method ID, combined with a Length/Payload that is also wrong for this
# (unknown) method. Method ID validation takes priority, per MVC-92895.
UNKNOWN_METHOD_ID = 0x0000
UNKNOWN_METHOD_LENGTH = 0x00000009
UNKNOWN_METHOD_PAYLOAD = bytes([0x11])


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
        testresult.addHeader("Unknown Method ID is rejected with E_UNKNOWN_METHOD")
        # #####################################################################
        someipcheck.send_and_check_error(testresult, client,
                                cs.build_request(UNKNOWN_METHOD_ID,
                                                 UNKNOWN_METHOD_LENGTH,
                                                 UNKNOWN_METHOD_PAYLOAD),
                                someipcheck.RC_E_UNKNOWN_METHOD,
                                "Unknown Method ID 0x%04X" % UNKNOWN_METHOD_ID)

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

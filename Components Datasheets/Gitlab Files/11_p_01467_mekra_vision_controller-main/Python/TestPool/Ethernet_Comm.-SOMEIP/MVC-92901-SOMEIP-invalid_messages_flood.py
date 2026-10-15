#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92901-SOMEIP-invalid_messages_flood.py
# Task : The camera still answers correctly after a flood of invalid requests
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 11.09.2026 | Martin Oeder  | initial
#******************************************************************************
#******************************************************************************
# """Deviations from the test steps, so the report states them."""
# Test step 4 only says "Repeat previous test step" without a number or a
# duration. FLOOD_DURATION_S below defines how long the flood runs; the value is
# a choice, not taken from the test steps, and has to be confirmed.
# The flood writes one summary verdict instead of one verdict per request,
# otherwise the report would grow by thousands of lines.
#
#******************************************************************************
"""
The flood uses cs.send_timed(): unlike cs.send() it does not sleep 0.3 s after
every request, so the camera really gets loaded.
"""
from time import perf_counter

from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as sc
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92901"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- The invalid request that is repeated ---
INVALID_SERVICE_ID = 0x433E         # neighbour of the camera's own 0x433F
REQUEST_LENGTH = 0x08

# How long the flood of test step 4 runs. The test steps give neither a count nor
# a duration, so this is the knob to turn.
FLOOD_DURATION_S = 14400.0          # 4 hours


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

        invalid_request = sc.build_request(cs.M_GET_CAM_STATUS, REQUEST_LENGTH,
                                           service_id=INVALID_SERVICE_ID)

        # #####################################################################
        testresult.addHeader("One invalid request is rejected with "
                             "E_UNKNOWN_SERVICE")
        # #####################################################################
        sc.send_and_check_error(testresult, client, invalid_request,
                                sc.RC_E_UNKNOWN_SERVICE,
                                "Unknown Service ID 0x%04X" % INVALID_SERVICE_ID)

        # #####################################################################
        testresult.addHeader("Flood of invalid requests for %.0f s"
                             % FLOOD_DURATION_S)
        # #####################################################################
        sent = 0
        rejected = 0
        unanswered = 0
        other = 0

        t_start = perf_counter()
        while perf_counter() - t_start < FLOOD_DURATION_S:
            rx, _ = cs.send_timed(client, invalid_request)
            sent += 1

            if rx is None:
                unanswered += 1
            elif (rx.get_message_type() == "%02x" % sc.MSG_TYPE_ERROR
                  and rx.get_return_code() == "%02x" % sc.RC_E_UNKNOWN_SERVICE):
                rejected += 1
            else:
                other += 1

        elapsed = perf_counter() - t_start
        testresult.addInfo("Flood: %d requests in %.1f s (%.1f requests/s), "
                           "%d rejected with E_UNKNOWN_SERVICE, %d unanswered, "
                           "%d answered differently"
                           % (sent, elapsed, sent / elapsed if elapsed else 0.0,
                              rejected, unanswered, other))

        testresult.append(["Every invalid request of the flood is rejected with "
                           "E_UNKNOWN_SERVICE: %d of %d" % (rejected, sent),
                           "PASSED" if sent > 0 and rejected == sent else "FAILED"])

        # #####################################################################
        testresult.addHeader("A valid request is still answered after the flood")
        # #####################################################################
        rx = cs.send(client, cs.build_request(cs.M_GET_CAM_STATUS, REQUEST_LENGTH))
        cs.positive_response(testresult, rx, cs.M_GET_CAM_STATUS,
                             "getCamStatus (0x%04X) on the valid service ID "
                             "0x%04X" % (cs.M_GET_CAM_STATUS, cs.SERVICE_ID))

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

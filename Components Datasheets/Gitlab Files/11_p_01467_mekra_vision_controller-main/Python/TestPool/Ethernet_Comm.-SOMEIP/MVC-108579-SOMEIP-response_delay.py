#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-108579-SOMEIP-response_delay.py
# Task : Every SOME/IP method answers within the allowed response delay
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 10.09.2026 | Martin Oeder  | initial
#******************************************************************************
#******************************************************************************
# """Deviations from the test steps, so the report states them."""
# The response lengths of the test steps (0x17 for getCamIdentification, 0x020D
# for getDataSheet) are logged but not asserted: this test case measures the
# response delay, and the data sheet size depends on the SW version.
#
#******************************************************************************
"""
Test steps 1 to 4 (DHCP server on the 192.168.120.10 pool, power cycle, wait for
the OPERATIONAL state) are what cs.start_camera() performs.

The warm-up request before the measurements is deliberate: the very first request
of a session can carry the address resolution, which would show up as an
inflated delay on the first measured method.
"""
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-108579"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 2-3
POWER_OFF_AT_END = True             # test step 15: U_in = 0.0 V

# --- Network ---
USE_DHCP = True                     # test step 1: DHCP pool 192.168.120.10

# --- Response delay under test ---
MAX_DELAY_MS = 100                  # "delay <= 100ms" per test steps 6, 8, 10,
                                    # 12 and 14

# --- Payloads and lengths of the measured requests ---
EXCL_TTL_S = 10                     # 0x0000000A, setCamExclusive
EXCL_REQUEST_LENGTH = 0x0C
CTRL_REQUEST_LENGTH = 0x09          # getCamControl carries the 1-byte index
HEATING_OFF = 0x0000


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

        # Keeps the address resolution out of the first measured delay.
        cs.service_answers(testresult, client, cs.M_GET_CAM_STATUS)

        # #####################################################################
        testresult.addHeader("getCamIdentification answers within %d ms"
                             % MAX_DELAY_MS)
        # #####################################################################
        someipcheck.send_and_check_delay(
            testresult, client,
            cs.build_request(cs.M_GET_CAM_IDENTIFICATION, 0x08),
            cs.M_GET_CAM_IDENTIFICATION, "getCamIdentification",
            max_delay_ms=MAX_DELAY_MS)

        # #####################################################################
        testresult.addHeader("getDataSheet answers within %d ms" % MAX_DELAY_MS)
        # #####################################################################
        someipcheck.send_and_check_delay(
            testresult, client,
            cs.build_request(cs.M_GET_DATA_SHEET, 0x08),
            cs.M_GET_DATA_SHEET, "getDataSheet", max_delay_ms=MAX_DELAY_MS)

        # #####################################################################
        testresult.addHeader("setCamExclusive answers within %d ms" % MAX_DELAY_MS)
        # #####################################################################
        someipcheck.send_and_check_delay(
            testresult, client,
            cs.build_request(cs.M_SET_CAM_EXCLUSIVE, EXCL_REQUEST_LENGTH,
                             EXCL_TTL_S.to_bytes(4, "big")),
            cs.M_SET_CAM_EXCLUSIVE, "setCamExclusive (%d s)" % EXCL_TTL_S,
            max_delay_ms=MAX_DELAY_MS)

        # #####################################################################
        testresult.addHeader("eraseCamExclusive answers within %d ms"
                             % MAX_DELAY_MS)
        # #####################################################################
        someipcheck.send_and_check_delay(
            testresult, client,
            cs.build_request(cs.M_ERASE_CAM_EXCLUSIVE, 0x08),
            cs.M_ERASE_CAM_EXCLUSIVE, "eraseCamExclusive",
            max_delay_ms=MAX_DELAY_MS)

        # #####################################################################
        testresult.addHeader("getCamControl answers within %d ms" % MAX_DELAY_MS)
        # #####################################################################
        rx = someipcheck.send_and_check_delay(
            testresult, client,
            cs.build_request(cs.M_GET_CAM_CONTROL, CTRL_REQUEST_LENGTH,
                             bytes([cs.CTRL_IDX_HEATER])),
            cs.M_GET_CAM_CONTROL,
            "getCamControl (control index 0x%02X, heater)" % cs.CTRL_IDX_HEATER,
            max_delay_ms=MAX_DELAY_MS)

        # The test step also states the heater has to be in automatic mode and
        # off, so the control block is evaluated on the same response.
        someipcheck.check_payload_mask(
            testresult, rx,
            "%02x%02x%04x" % (cs.SUPPORTED_MODES, cs.MODE_AUTOMATIC, HEATING_OFF),
            "heater in automatic mode and off", ignore_last_bytes=0)

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        SomeipClient.close_clients(client)

        if POWER_OFF_AT_END:
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

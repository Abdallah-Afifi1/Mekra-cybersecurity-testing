#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92937-setCamExclusive-24_hours.py
# Task : Validation of Exclusive lock of the camera
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
# Open Point 1: First test step of setCamExclusive (>=24h):
#               Due to runtime issue (0.3s) of the requests, the waiting time
#               should be set to 1.0s instead of 1.5s and
#               should be set to 1.0s instead of 0.5s
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92937"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- setCamExclusive TTLs under test ---
TTL_24H = 86400                     # 0x00015180, >= 24 h: expected to be clamped
                                     # to a short maximum lock duration (same
                                     # behaviour as the 0xFFFFFFFF case in MVC-92938)
TTL_JUST_UNDER_24H = 86399          # 0x0001517F, 23:59:59: expected to be honored
                                     # for its full requested duration


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

        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                            "camera not locked")

        # #####################################################################
        testresult.addHeader("setCamExclusive %d s (24 h): clamped to a short "
                             "maximum lock duration" % TTL_24H)
        # #####################################################################
        cs.lock(testresult, client, TTL_24H)
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked")
        someipcheck.wait(testresult, 8.0, "lock still needs to be active")
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked")
        someipcheck.wait(testresult, 1.0, "lock still needs to be active")
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked")
        someipcheck.wait(testresult, 1.0, "until lock time is over")
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                            "camera not locked")

        # #####################################################################
        testresult.addHeader("setCamExclusive %d s (23:59:59, just under 24 h): "
                             "honored for its full requested duration"
                             % TTL_JUST_UNDER_24H)
        # #####################################################################
        cs.lock(testresult, client, TTL_JUST_UNDER_24H)
        someipcheck.wait(testresult, 10 * 3600, "lock still needs to be active")
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked")
        someipcheck.wait(testresult, 10 * 3600, "lock still needs to be active")
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked")
        someipcheck.wait(testresult, 3 * 3600 + 59 * 60 + 59, "until lock is almost over")
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked")
        someipcheck.wait(testresult, 60, "until lock time is over")
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                            "camera not locked")

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

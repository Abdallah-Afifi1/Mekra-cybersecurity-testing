#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92941-eraseCamExclusiv-positive_response.py
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
TESTCASE_ID = "HIL_Test.MVC-92941"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- Exclusive lock ---
# The lock is released with eraseCamExclusive long before this TTL runs out, that
# is the point of the test.
LOCK_TTL_S = 40                     # 0x00000028


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
        testresult.addHeader("setCamExclusive %d s locks the camera" % LOCK_TTL_S)
        # #####################################################################
        cs.lock(testresult, client, LOCK_TTL_S)
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked")

        # #####################################################################
        testresult.addHeader("eraseCamExclusive releases the lock before the TTL "
                             "runs out")
        # #####################################################################
        cs.unlock(testresult, client)
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

#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-93345-getCamStatus-camera_locked.py
# Task : check getCamStatus concerning camera lock state
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 02.09.2026 | Martin Oeder  | initial
# 1.1.0  | 10.09.2026 | Martin Oeder  | shared steps moved to someip_checks
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-93345"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 24.0                     # U_nominal
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- RTP stream ---
RTP_STREAM = 1
RTP_TIMEOUT_S = 2.0

# --- Exclusive lock ---
LOCK_TTL_S = 60


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
        testresult.addHeader("RTP stream is inactive before the camera is locked")
        # #####################################################################
        cs.stream_active(testresult, False, "no video stream active",
                         stream=RTP_STREAM, timeout_s=RTP_TIMEOUT_S)

        # #####################################################################
        testresult.addHeader("getCamStatus while not locked")
        # #####################################################################
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                            "camera not locked")

        # #####################################################################
        testresult.addHeader("setCamExclusive locks the camera for %d s"
                             % LOCK_TTL_S)
        # #####################################################################
        cs.lock(testresult, client, LOCK_TTL_S)

        # #####################################################################
        testresult.addHeader("getCamStatus while locked by this client")
        # #####################################################################
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked by this client")

        # #####################################################################
        testresult.addHeader("eraseCamExclusive releases the lock")
        # #####################################################################
        cs.unlock(testresult, client)

        # #####################################################################
        testresult.addHeader("getCamStatus after the lock is released")
        # #####################################################################
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                            "camera not locked again")

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

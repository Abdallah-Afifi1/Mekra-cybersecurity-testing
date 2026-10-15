#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-93346-getCamStatus-after_camera_reset.py
# Task : The exclusive lock does not survive a camera reset
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
#
#
#******************************************************************************
"""
The reset in test steps 7 and 8 happens while the 60 s lock is still running, so
an unlocked camera afterwards really shows that the lock is volatile and not just
expired.

The client socket has to be closed before the camera is powered up again:
SomeipClient binds a fixed source port, so a second client cannot open it while
the first one still holds it.
"""
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-93346"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 24.0                     # U_in per test steps 2 and 8
POWER_OFF_TIME_S = 5.0              # dwell at 0.0 V, longer than the 2.0 s default
                                     # of cs.start_camera(), so the DUT really
                                     # cold-starts
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- RTP stream ---
RTP_STREAM = 1
RTP_TIMEOUT_S = 2.0

# --- Exclusive lock ---
LOCK_TTL_S = 60                     # 0x0000003C, still running when the reset hits


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
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP,
                                 off_time_s=POWER_OFF_TIME_S)

        # The first request of a session can be lost, so warm up before measuring.
        cs.service_answers(testresult, client, cs.M_GET_CAM_STATUS)

        # #####################################################################
        testresult.addHeader("RTP stream is inactive")
        # #####################################################################
        cs.stream_active(testresult, False, "no video stream active",
                         stream=RTP_STREAM, timeout_s=RTP_TIMEOUT_S)

        # #####################################################################
        testresult.addHeader("setCamExclusive %d s locks the camera" % LOCK_TTL_S)
        # #####################################################################
        cs.lock(testresult, client, LOCK_TTL_S)
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_CLIENT,
                            "camera locked by this client")

        # #####################################################################
        testresult.addHeader("Camera reset while the lock is still running")
        # #####################################################################
        # Free the fixed source port before the camera comes up again, otherwise
        # the new client cannot bind it.
        SomeipClient.close_clients(client)
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP,
                                 off_time_s=POWER_OFF_TIME_S)

        cs.service_answers(testresult, client, cs.M_GET_CAM_STATUS)

        # #####################################################################
        testresult.addHeader("getCamStatus after the reset: the lock is gone")
        # #####################################################################
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

#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-109556-SetCamControl-not_locked.py
# Task : SetCamControl rejected with E_LOCK_EXPIRED if not locked before
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 02.09.2026 | Martin Oeder  | initial
# 1.1.0  | 10.09.2026 | Martin Oeder  | shared steps moved to someip_checks
# 1.2.0  | 11.09.2026 | Martin Oeder  | set_chamber_temperature() plus a fixed
#                                  600 s sleep, as in the Heating_Control tests;
#                                  the 600 s were a timeout before
# 1.3.0  | 11.09.2026 | Martin Oeder  | step order per the test steps: power down,
#                                  then chamber, then power up
#******************************************************************************
#******************************************************************************
# """Deviations from the test steps, so the report states them."""
# cs.start_camera() of test step 3 powers the supply down once more before it
# powers up, so the report shows a second "U_in = 0.0 V" line between step 2
# and step 3.
#
#******************************************************************************
from time import sleep

from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-109556"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1 and 3
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- Climate chamber ---
T_TEST = 25.0                       # test step 2
CHAMBER_WAIT_S = 600                # "Waiting time: 600s" per test step 2

# --- Heater control under test ---
CTRL_IDX = cs.CTRL_IDX_HEATER               # 0x09
HEATING_MODE = cs.MODE_MANUAL_MODIFIED      # 0x03, Control Mode of the setCamControl payload
HEATING_ON = 0x0001
HEATING_OFF = 0x0000

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
        chamber = testenv.getCC()
    except Exception as ex:
        chamber = None
        testresult.addInfo("Climate chamber not available: %s" % ex)

    try:
        # #####################################################################
        testresult.addHeader("Preconditions")
        # #####################################################################
        cs.log_dut_config(testresult)

        # Test step 1: the DUT is powered down before the chamber warms up.
        testresult.addSubHeader("U_in = 0.0 V")
        cs.power_off(testresult, psu, SUPPLY_CH)

        # Test step 2: 25 degC is reached while the DUT is still off.
        testresult.addSubHeader("Temperature test chamber: %.0f degC" % T_TEST)
        cs.set_chamber_temperature(testresult, chamber, T_TEST)
        sleep(CHAMBER_WAIT_S)

        # Test step 3
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        # The first request of a session can be lost, so warm up before measuring.
        cs.service_answers(testresult, client, cs.M_GET_CAM_STATUS)

        # #####################################################################
        testresult.addHeader("getCamStatus while not locked")
        # #####################################################################
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                            "camera not locked")

        # #####################################################################
        testresult.addHeader("setCamControl while not locked is rejected")
        # #####################################################################
        cs.set_control(testresult, client, CTRL_IDX, HEATING_MODE, HEATING_ON,
                       "manual modified ON heating mode while not locked",
                       error_rc=someipcheck.RC_E_LOCK_EXPIRED)

        # #####################################################################
        testresult.addHeader("getCamControl confirms the heating is unchanged")
        # #####################################################################
        cs.check_control(testresult, client, CTRL_IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off")

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
        testresult.addHeader("setCamControl while locked is accepted")
        # #####################################################################
        cs.set_control(testresult, client, CTRL_IDX, HEATING_MODE, HEATING_ON,
                       "manual modified ON heating mode while locked")

        # #####################################################################
        testresult.addHeader("getCamControl confirms the heating change")
        # #####################################################################
        cs.check_control(testresult, client, CTRL_IDX, cs.MODE_MANUAL, HEATING_ON,
                         "in manual mode and on")

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        SomeipClient.close_clients(client)

        cs.release_chamber(chamber)

        if POWER_OFF_AT_END:
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

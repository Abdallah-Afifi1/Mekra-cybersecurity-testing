
#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92322-Check_default_heating_mode_after_startup.py
# Task : getCamControl reads the default (automatic mode) heating state right
#        after a cold start, for three different ambient temperatures
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 03.09.2026 | Martin Oeder  | initial
#******************************************************************************
#"Deviations from the test steps to test script."   
# Open point 1: test step 7's description says automatic mode and on for the"
#                "20 degC phase, but its Receive payload is 0x07040000 (off). The payload is"
#                "used here, since it is the value the DUT actually returns")
#
#******************************************************************************
"""
The test only reads back the default heating
state defaultHeaterMode = automatic establishes right after power-on, so no
control is written.
"""
from time import sleep

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92322"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 24.0                     # U_in per test steps 4, 10 and 16
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- Heating control under test ---
IDX = cs.CTRL_IDX_HEATER            # 0x09

# --- Climate chamber ---
CHAMBER_WAIT_S = 3600                # "Waiting time: 3600s" per test steps 3, 9 and 15

HEATING_OFF = 0x0000
HEATING_ON = 0x0001

# Chamber setpoint, expected default heating value read back after the cold
# start, and the precondition text (test steps 3-8, 9-14, 15-20).
PHASES = [
    (20.0, HEATING_OFF, "T_ambient <= 20.0 degC"),
    (-5.0, HEATING_ON,  "T_ambient < 0.0 degC"),
    (40.0, HEATING_OFF, "T_ambient > 40.0 degC"),
]
    

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

        for t_phase, exp_value, descr in PHASES:
            # #################################################################
            testresult.addHeader("Cold start at Tambient = %.1f degC (%s)"
                                 % (t_phase, descr))
            # #################################################################
            cs.power_off(testresult, psu, SUPPLY_CH)

            cs.set_chamber_temperature(testresult, chamber, t_phase)
            sleep(CHAMBER_WAIT_S)

            # The power cycle restores defaultHeaterMode, so no mode is written.
            client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

            cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, exp_value,
                             "default heating state after startup at %s" % descr)

            client.close_socket()
            client = None

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        if client is not None:
            client.close_socket()

        cs.release_chamber(chamber)

        if POWER_OFF_AT_END:
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

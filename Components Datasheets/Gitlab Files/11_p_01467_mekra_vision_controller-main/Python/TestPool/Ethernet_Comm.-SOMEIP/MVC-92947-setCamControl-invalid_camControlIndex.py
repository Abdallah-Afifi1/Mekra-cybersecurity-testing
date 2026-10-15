#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92947-setCamControl-invalid_camControlIndex.py
# Task : Invalid camControlIndex is rejected with E_INVALID_CONTROL_INDEX
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
setCamControl needs an active exclusive lock, so the camera is locked first and
released again in the last step. The two good cases leave the heater in automatic
and the shutter in manual modified ON; the power cycle of the next test restores
the defaults.
"""
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92947"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- Exclusive lock ---
LOCK_TTL_S = 120                    # 0x00000078, long enough for all 12 writes

# Control indices to reject, with the supported modes, control mode and control
# value each test step sends along. The camera implements 0x09 (heater) and 0x50
# (shutter), see cs.CTRL_IDX_HEATER / cs.CTRL_IDX_SHUTTER: 0x08 / 0x0A are the
# direct neighbours of the heater, 0x00 is the low boundary and 0xFF the high one.
#                    index, supported modes, mode, value
INVALID_CONTROL_CASES = [
    (0x00, 0x07, 0x03, 0x0000),
    (0x01, 0x07, 0x03, 0x0000),
    (0x03, 0x07, 0x03, 0x0000),
    (0x04, 0x06, 0x03, 0x0000),
    (0x07, 0x06, 0x03, 0x0000),
    (0x08, 0x06, 0x02, 0x0000),
    (0x0A, 0x05, 0x02, 0x0000),
    (0x1A, 0x00, 0x02, 0x0000),
    (0x10, 0x01, 0x04, 0x0000),
    (0xFF, 0x01, 0x04, 0x0000),
]

# --- Good cases: the two implemented control indices ---
HEATER_VALUE = 0x0000               # automatic mode carries no value
SHUTTER_VALUE = 0x0001


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
        testresult.addHeader("setCamExclusive %d s: setCamControl needs the lock"
                             % LOCK_TTL_S)
        # #####################################################################
        cs.lock(testresult, client, LOCK_TTL_S)

        # #####################################################################
        testresult.addHeader("Invalid control indices are rejected with "
                             "E_INVALID_CONTROL_INDEX")
        # #####################################################################
        for control_index, supported_modes, mode, value in INVALID_CONTROL_CASES:
            cs.set_control(testresult, client, control_index, mode, value,
                           "control index 0x%02X, supported modes 0x%02X, mode "
                           "0x%02X, value 0x%04X"
                           % (control_index, supported_modes, mode, value),
                           supported_modes=supported_modes,
                           error_rc=someipcheck.RC_E_INVALID_CONTROL_INDEX)

        # #####################################################################
        testresult.addHeader("Good case: control index 0x%02X (heater) is accepted"
                             % cs.CTRL_IDX_HEATER)
        # #####################################################################
        cs.set_control(testresult, client, cs.CTRL_IDX_HEATER, cs.MODE_AUTOMATIC,
                       HEATER_VALUE, "heater to automatic mode")

        # #####################################################################
        testresult.addHeader("Good case: control index 0x%02X (shutter) is accepted"
                             % cs.CTRL_IDX_SHUTTER)
        # #####################################################################
        cs.set_control(testresult, client, cs.CTRL_IDX_SHUTTER,
                       cs.MODE_MANUAL_MODIFIED, SHUTTER_VALUE,
                       "shutter to manual modified ON")

        # #####################################################################
        testresult.addHeader("eraseCamExclusive releases the lock")
        # #####################################################################
        cs.unlock(testresult, client)

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

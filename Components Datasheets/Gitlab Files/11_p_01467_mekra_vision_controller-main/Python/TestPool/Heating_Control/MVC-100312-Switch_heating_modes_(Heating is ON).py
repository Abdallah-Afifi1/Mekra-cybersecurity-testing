
#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-100312-Switch_heating_modes_(Heating is ON).py
# Task : Switch heating modes via setCamControl/getCamControl while Tambient
#        stays below Tauto_on, so the heating stays on throughout
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 03.09.2026 | Martin Oeder  | initial
#******************************************************************************
"""
Tambient stays below Tauto_on for the whole test (chamber at -20 degC), so
automatic mode keeps the heating on throughout and every setCamControl /
getCamControl mode transition is observed against a heater that runs the
whole time.
"""
from time import sleep, perf_counter

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-100312"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in 
POWER_OFF_AT_END = True             # U_in = 0.0 V

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- Heating control under test ---
IDX = cs.CTRL_IDX_HEATER            # 0x09
EXCLUSIVE_TTL_S = 30 * 60           # setCamExclusive payload 0x00000708
MIN_SWITCH_PERIOD_S = 1             # t_heater_min_switch_period between two switches
RC_E_INVALID_CONTROL_VALUE = 0x37

# --- Climate chamber ---
T_TEST = -20.0                      # below Tauto_on, so the heating stays on
T_END = 20.0                        # the steps warm up before powering off
CHAMBER_WAIT_S = 3600               # "Waiting time: 3600s"

# --- Imager temperature ---
TEMP_TIMEOUT_S = 2 * 60
TEMP_POLL_S = 1 * 60
SOAK_S = 0                          # fallback wait when Timager is unreadable

# Written mode and value, then the mode and value the readout has to show. The
# last entry is the expected return code, None for a positive response.
MODE_SEQUENCE = [
    (cs.MODE_AUTOMATIC,       0x0000, cs.MODE_AUTOMATIC, 0x0001, None),
    (cs.MODE_MANUAL,          0x0003, cs.MODE_MANUAL,    0x0001, None),
    (cs.MODE_AUTOMATIC,       0x0004, cs.MODE_AUTOMATIC, 0x0001, None),
    (cs.MODE_MANUAL_MODIFIED, 0x0000, cs.MODE_MANUAL,    0x0000, None),
    (cs.MODE_AUTOMATIC,       0x0000, cs.MODE_AUTOMATIC, 0x0001, None),
    (cs.MODE_MANUAL_MODIFIED, 0x0004, cs.MODE_AUTOMATIC, 0x0001,
     RC_E_INVALID_CONTROL_VALUE),
    (cs.MODE_MANUAL_MODIFIED, 0x0001, cs.MODE_MANUAL,    0x0001, None),
    (cs.MODE_AUTOMATIC,       0x0000, cs.MODE_AUTOMATIC, 0x0001, None),
    (cs.MODE_MANUAL,          0x0000, cs.MODE_MANUAL,    0x0001, None),
    (cs.MODE_AUTOMATIC,       0x0001, cs.MODE_AUTOMATIC, 0x0001, None),
]


# #############################################################################
# Helper functions
# #############################################################################
def wait_for_imager(testresult, client, chamber, operator, limit, descr,
                    soak_s=SOAK_S):
    """Poll Timager until it satisfies the criterion, then write the verdict.

    soak_s is waited out instead when Timager cannot be read at all.
    """
    t_start = perf_counter()

    while True:
        value, reason = cs.imager_temperature(client)
        elapsed = perf_counter() - t_start
        ambient = ("%.1f degC" % chamber.getCurrentTemp()) if chamber else "unknown"

        if value is None:
            testresult.append(["%s: imager temperature not readable (%s)"
                               % (descr, reason), "FAILED"])
            if soak_s:
                testresult.addInfo("Soaking %.0f min instead, the criterion stays "
                                   "unverified" % (soak_s / 60.0))
                sleep(soak_s)
            return None

        reached = value > limit if operator == ">" else value < limit
        if reached:
            testresult.append(["%s: Timager %.2f degC %s %.2f degC after %.0f s "
                               "(Tambient %s)"
                               % (descr, value, operator, limit, elapsed, ambient),
                               "PASSED"])
            return value

        if elapsed >= TEMP_TIMEOUT_S:
            testresult.append(["%s: Timager %.2f degC did not become %s %.2f degC "
                               "within %d s (Tambient %s)"
                               % (descr, value, operator, limit, TEMP_TIMEOUT_S,
                                  ambient), "FAILED"])
            return value

        testresult.addInfo("Timager %.2f degC, Tambient %s, waiting for %s %.2f degC "
                           "(%.0f s elapsed)"
                           % (value, ambient, operator, limit, elapsed))
        sleep(TEMP_POLL_S)


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

    t_auto_on = cs.sw_config().t_imager_auto_on_c

    try:
        # #####################################################################
        testresult.addHeader("Preconditions")
        # #####################################################################
        cs.log_dut_config(testresult)
       
        # chamber cools down to -20 degC before the camera is powered.
        cs.set_chamber_temperature(testresult, chamber, T_TEST)
        sleep(CHAMBER_WAIT_S)

        if chamber is not None:
            ambient = chamber.getCurrentTemp()
            testresult.append(["Precondition Tambient < Tauto_on: %.1f degC < %.1f degC"
                               % (ambient, t_auto_on),
                               "PASSED" if ambient < t_auto_on else "FAILED"])

        # Power on. The power cycle restores defaultHeaterMode
        # (automatic), so no mode is written here. start_camera() covers DHCP,
        # reaching the Operational State and the SD Offerservice monitoring
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        wait_for_imager(testresult, client, chamber, "<", t_auto_on,
                                "Imager colder than the switch-on limit")

        # #####################################################################
        testresult.addHeader("Heating mode transitions")
        # #####################################################################
        # setCamExclusive locks the camera for EXCLUSIVE_TTL_S.
        cs.lock(testresult, client, EXCLUSIVE_TTL_S)

        for mode, value, exp_mode, exp_value, error_rc in MODE_SEQUENCE:
            descr = "mode 0x%02X value 0x%04X" % (mode, value)
            testresult.addSubHeader("setCamControl %s" % descr)

            cs.set_control(testresult, client, IDX, mode, value, descr,
                           error_rc=error_rc,
                           settle_s=MIN_SWITCH_PERIOD_S)
            cs.check_control(testresult, client, IDX, exp_mode, exp_value,
                             "in mode 0x%02X with value 0x%04X" % (exp_mode, exp_value))

        # eraseCamExclusive releases the lock.
        cs.unlock(testresult, client)

        # #####################################################################
        testresult.addHeader("Postcondition: warm up")
        # #####################################################################
        # chamber warms up to 20 degC before powering off.
        cs.set_chamber_temperature(testresult, chamber, T_END)
        sleep(CHAMBER_WAIT_S)

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
            # U_in = 0.0 V.
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

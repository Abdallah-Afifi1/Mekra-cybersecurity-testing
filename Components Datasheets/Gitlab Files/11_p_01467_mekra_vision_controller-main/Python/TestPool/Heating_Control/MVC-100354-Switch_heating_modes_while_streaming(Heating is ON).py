#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-100354-Switch_heating_modes_while_streaming(Heating is ON).py
# Task : Switch through the heating modes while a stream runs and the heating is
#        active, including a rejected control value
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name           | Description
#------------------------------------------------------------------------------
# 1.0.0  | 03.08.2026 | Ehu Li         | initial  
# 1.0.1  | 08.09.2026 | Martin Oeder   | adapt waiting time (temperature setpoint) 
#******************************************************************************
    # """Deviations from the test steps, so the report states them."""
    # testresult.addInfo("Open point 1: subscribe payload 0xC000003 has seven digits, "
    #                    "used is 0x%08X." % ROI)
    # testresult.addInfo("Open point 2: Request ID 0x0000000F on the unsubscribe only, "
    #                    "used is 0x%08X." % cs.REQUEST_ID)
    # testresult.addInfo("Open point 3: the subscribe response is specified as length "
    #                    "0x0C without payload, that would be 0x08.")
    # testresult.addInfo("Open point 4: the steps require Tambient < Tauto_on. The "
    #                    "firmware switches on Timager, so Timager is checked as well.")
    # testresult.addInfo("Open point 5: 'check RTP stream' does not say how. The test "
    #                    "listens on the port the parameter set defines and treats one "
    #                    "received packet within %.1f s as an active stream."
    #                    % RTP_TIMEOUT_S)
    # testresult.addInfo("Open point 6: the fifth readout is described as 'automatic "
    #                    "mode and off' while its expected payload is 0x07040001, which "
    #                    "is on. The payload is used, it matches the cold condition.")
"""
Tambient is below Tauto_on for the whole test, so automatic mode keeps the heating
on and every mode change is observed against a running heater.
"""
from time import sleep, perf_counter

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-100354"

SUPPLY_CH = 1
SUPPLY_V = 28.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_HEATER
ROI = 0xC0000003                    # human vision, ROI 3, flipped and mirrored
EXCLUSIVE_TTL_S = 30 * 60           # the steps lock the camera for 30 min
MIN_SWITCH_PERIOD_S = 1             # t_heater_min_switch_period between two switches
RC_INVALID_CONTROL_VALUE = 0x37
RTP_TIMEOUT_S = 2.0                 # a running stream delivers well within this

# --- Climate chamber ---
T_TEST = -20.0                      # below Tauto_on, so the heating stays on
T_END = 20.0                        # the steps warm up before powering off
CHAMBER_WAIT_S = 3600               # "Waiting time: 3600s" (both chamber setpoints)

# --- Imager temperature ---
TEMP_TIMEOUT_S = 60 * 60
TEMP_POLL_S = 5 * 60
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
     RC_INVALID_CONTROL_VALUE),
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

        cs.set_chamber_temperature(testresult, chamber, T_TEST)
        sleep(CHAMBER_WAIT_S)

        if chamber is not None:
            ambient = chamber.getCurrentTemp()
            testresult.append(["Precondition Tambient < Tauto_on: %.1f degC < %.1f degC"
                               % (ambient, t_auto_on),
                               "PASSED" if ambient < t_auto_on else "FAILED"])

        # The power cycle restores defaultHeaterMode, so no mode is written here.
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        # #####################################################################
        testresult.addHeader("Video stream on")
        # #####################################################################
        cs.subscribe_roi(testresult, client, ROI)
        cs.stream_active(testresult, True, "active after subscribeROIVideo",
                         timeout_s=RTP_TIMEOUT_S)

        # wait_for_imager(testresult, client, chamber, "<", t_auto_on,
        #                 "Imager colder than the switch-on limit")

        # #####################################################################
        testresult.addHeader("Heating modes while the stream runs")
        # #####################################################################
        cs.lock(testresult, client, EXCLUSIVE_TTL_S)

        for mode, value, exp_mode, exp_value, error_rc in MODE_SEQUENCE:
            descr = "mode 0x%02X value 0x%04X" % (mode, value)
            testresult.addSubHeader("setCamControl %s" % descr)

            cs.set_control(testresult, client, IDX, mode, value, descr,
                           error_rc=error_rc,
                           settle_s=MIN_SWITCH_PERIOD_S)
            cs.check_control(testresult, client, IDX, exp_mode, exp_value,
                             "in mode 0x%02X with value 0x%04X" % (exp_mode, exp_value))

        # #####################################################################
        testresult.addHeader("Postcondition: stream off and camera unlocked")
        # #####################################################################
        cs.unlock(testresult, client)
        cs.unsubscribe_roi(testresult, client, ROI)
        cs.stream_active(testresult, False, "off after unSubscribeROIVideo",
                         timeout_s=RTP_TIMEOUT_S)

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
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

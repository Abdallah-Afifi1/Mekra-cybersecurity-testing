
#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-100349-Check_temperature_behavior_automatic_heating_mode_while_Streaming.py
# Task : Automatic heating mode follows Tauto_on/Tauto_off as Tambient is
#        driven across both thresholds while a video stream is running
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 04.09.2026 | Martin Oeder  | initial
#******************************************************************************
"""
Only automatic mode is used, no manual override: the heating value read back
is purely a function of Timager crossing Tauto_off (heating off) or Tauto_on
(heating on). At 70 degC the DUT may additionally be in over-temperature
protection, but that reads back identically to "automatic, off", so the two
cases are not distinguished here.
"""
from time import sleep, perf_counter

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-100349"

SUPPLY_CH = 1
SUPPLY_V = 28.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_HEATER
HEATING_ON = 0x0001
HEATING_OFF = 0x0000
ROI = 0xC0000003                    # human vision, ROI 3, flipped and mirrored
EXCLUSIVE_TTL_S = 2                 # setCamExclusive payload 0x00000002 (test step 9)
RTP_TIMEOUT_S = 2.0

# Hard-coded in the DUT software, not part of the parameter set.
T_SER_PROT_ON = 40.0
T_SER_PROT_OFF = 35.0

# --- Climate chamber ---
T_WARM_1 = 30.0                     # above Tauto_off, before power-on (step 3)
T_HOT = 70.0                        # further above Tauto_off, maybe protection (step 12)
T_COLD = -20.0                      # below Tauto_on (step 16)
T_WARM_2 = 40.0                     # above Tauto_off again (step 23)
T_END = 20.0                        # final settle before power-down (step 29)
CHAMBER_TOLERANCE = 1.0
CHAMBER_TIMEOUT_S = 70 * 60         # reach-and-settle timeout (steps 16, 23 - no
                                     # fixed "Waiting time" given for those there)
CHAMBER_POLL_S = 30
CHAMBER_WAIT_S = 3600               # "Waiting time: 3600s" (steps 3, 12 and 29)

# --- Temperature criteria ---
# The wait ends as soon as the criterion holds, it is not a fixed soak.
TEMP_TIMEOUT_S = 90 * 60
TEMP_POLL_S = 5 * 60
SOAK_S = 0                          # fallback wait when Timager is unreadable


# #############################################################################
# Helper functions
# #############################################################################
def wait_for_temperatures(testresult, client, chamber, predicate, descr,
                          soak_s=SOAK_S, verify_control=None,
                          poll_s=TEMP_POLL_S):
    """Poll Timager and Tser until the predicate holds, then write the verdict.

    The predicate answers True, False or None, None meaning it misses a value it
    needs and can never be decided. Also serves as a one-shot check when the
    predicate already holds on the first sample.

    verify_control, when given, is (ctrl_idx, exp_mode, exp_value): on every
    iteration where the predicate is still False, getCamControl is cyclically
    re-checked against it, confirming the control has not already changed while
    the criterion is still being waited for.

    poll_s sets the interval between polls, defaulting to TEMP_POLL_S.
    """
    t_start = perf_counter()

    while True:
        t_imager, imager_reason = cs.imager_temperature(client)
        t_ser, ser_reason = cs.serializer_temperature(client)
        elapsed = perf_counter() - t_start
        ambient = ("%.1f degC" % chamber.getCurrentTemp()) if chamber else "unknown"

        # The reason carries the raw payload, so the log holds it next to the value.
        readings = ("Timager %s [%s], Tser %s [%s]"
                    % ("%.2f degC" % t_imager if t_imager is not None
                       else "not readable", imager_reason,
                       "%.2f degC" % t_ser if t_ser is not None
                       else "not readable", ser_reason))

        verdict = predicate(t_imager, t_ser)

        # A criterion that misses a value it needs can never become true, no
        # matter how long the test polls. Say so and return.
        if verdict is None:
            testresult.append(["%s: cannot be decided, %s" % (descr, readings),
                               "FAILED"])
            if soak_s:
                testresult.addInfo("Soaking %.0f min instead, the criterion stays "
                                   "unverified" % (soak_s / 60.0))
                sleep(soak_s)
            return t_imager, t_ser

        if verdict:
            testresult.append(["%s: %s after %.0f s (Tambient %s)"
                               % (descr, readings, elapsed, ambient), "PASSED"])
            return t_imager, t_ser

        # Still waiting: cyclically confirm the control has not changed yet.
        if verify_control is not None:
            ctrl_idx, exp_mode, exp_value = verify_control
            cs.check_control(testresult, client, ctrl_idx, exp_mode, exp_value,
                             "unchanged while waiting for %s" % descr)

        if elapsed >= TEMP_TIMEOUT_S:
            testresult.append(["%s: not reached within %d s, %s (Tambient %s)"
                               % (descr, TEMP_TIMEOUT_S, readings, ambient), "FAILED"])
            return t_imager, t_ser

        testresult.addInfo("%s, Tambient %s (%.0f s elapsed)"
                           % (readings, ambient, elapsed))
        sleep(poll_s)


def report_open_points(testresult):
    """Deviations from the test steps, so the report states them."""
    testresult.addInfo("Open point 1: Test step (set chamber temperature to 70°C "
                       "wait until Timager reach Tprotection_on instead of Tauto_off.")

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

    sw = cs.sw_config()
    t_auto_on = sw.t_imager_auto_on_c
    t_auto_off = sw.t_imager_auto_off_c
    t_img_prot_on = sw.t_imager_protection_on_c

    def above_tauto_off(t_imager, t_ser):
        """Automatic mode switches the heating off once Timager > Tauto_off."""
        if t_imager is None:
            return None
        return t_imager > t_auto_off

    def below_tauto_on(t_imager, t_ser):
        """Automatic mode switches the heating on once Timager < Tauto_on."""
        if t_imager is None:
            return None
        return t_imager < t_auto_on

    def in_protection(t_imager, t_ser):
        """Entering condition, an OR, so one known value can already satisfy it.
    
        Undecidable (None) only while no value at all can be read.
        """
        if t_imager is None and t_ser is None:
            return None
        return ((t_imager is not None and t_imager >= t_img_prot_on)
                or (t_ser is not None and t_ser > T_SER_PROT_ON))

    try:
        # #####################################################################
        testresult.addHeader("Preconditions")
        # #####################################################################
        cs.log_dut_config(testresult)

        # Test step 3: chamber heats up to 30 degC before the camera is powered.
        cs.set_chamber_temperature(testresult, chamber, T_WARM_1)
        sleep(CHAMBER_WAIT_S)

        # Test step 4: power on. The power cycle restores defaultHeaterMode
        # (automatic), so the following setCamControl is only an explicit
        # re-confirmation of the default.
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        cs.subscribe_roi(testresult, client, ROI)
        cs.stream_active(testresult, True, "active after subscribeROIVideo",
                         timeout_s=RTP_TIMEOUT_S)

        cs.lock(testresult, client, EXCLUSIVE_TTL_S)
        cs.set_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                       "automatic heating mode")
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off")

        # #####################################################################
        testresult.addHeader("Automatic mode at Tambient = %.0f degC" % T_HOT)
        # #####################################################################
        cs.set_chamber_temperature(testresult, chamber, T_HOT)
        sleep(CHAMBER_WAIT_S)

        wait_for_temperatures(testresult, client, chamber, above_tauto_off,
                              "Timager > %.1f degC (Tauto_off)" % t_auto_off)

        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off (protection or normal "
                         "automatic behavior read back the same)")

        # #####################################################################
        testresult.addHeader("Automatic mode: heating on at Tambient = %.0f degC"
                             % T_COLD)
        # #####################################################################
        cs.chamber_temperature(testresult, chamber, T_COLD, CHAMBER_TOLERANCE,
                               CHAMBER_TIMEOUT_S, CHAMBER_POLL_S)
        wait_for_temperatures(testresult, client, chamber, below_tauto_on,
                              "Timager < %.1f degC (Tauto_on)" % t_auto_on,
                              verify_control=(IDX, cs.MODE_AUTOMATIC, HEATING_OFF),
                              poll_s=10)    # polling changed to 5s
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_ON,
                         "in automatic mode and on now that Tauto_on is reached")

        # #####################################################################
        testresult.addHeader("Automatic mode: heating off at Tambient = %.0f degC"
                             % T_WARM_2)
        # #####################################################################
        cs.chamber_temperature(testresult, chamber, T_WARM_2, CHAMBER_TOLERANCE,
                               CHAMBER_TIMEOUT_S, CHAMBER_POLL_S)
        wait_for_temperatures(testresult, client, chamber, above_tauto_off,
                              "Timager > %.1f degC (Tauto_off)" % t_auto_off,
                              verify_control=(IDX, cs.MODE_AUTOMATIC, HEATING_ON))
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off now that Tauto_off is reached")

        # #####################################################################
        testresult.addHeader("Postcondition: warm up and stream off")
        # #####################################################################
        cs.set_chamber_temperature(testresult, chamber, T_END)
        sleep(CHAMBER_WAIT_S)

        cs.unsubscribe_roi(testresult, client, ROI)
        cs.stream_active(testresult, False, "off after unSubscribeROIVideo",
                         timeout_s=RTP_TIMEOUT_S)

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

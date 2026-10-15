
#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-100351-Check_heating_modes_during_runtime_while_Streaming_OP_inactive.py
# Task : Manual heating mode commands during runtime while a video stream is
#        running, confirming they are not overridden by the automatic-mode
#        Tauto_on/Tauto_off logic (no over-temperature protection involved)
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
OP inactive: none of the three chamber setpoints reach the over-temperature
protection thresholds, so every heating value read back is the direct result
of the last setCamControl written, not of the protection logic (see
MVC-100350 / MVC-92668 for the protection-active counterpart).

The central check is at Tambient < Tauto_on: a manual OFF written while warm
has to stay off even once the ambient would make automatic mode switch on.
"""
from time import sleep, perf_counter

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-100351"

SUPPLY_CH = 1
SUPPLY_V = 28.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_HEATER
HEATING_ON = 0x0001
HEATING_OFF = 0x0000
ROI = 0xC0000003                    # human vision, ROI 3, flipped and mirrored
EXCLUSIVE_TTL_S = 1                 # the steps lock the camera for 1 s per write
MIN_SWITCH_PERIOD_S = 1             # t_heater_min_switch_period between two switches
RTP_TIMEOUT_S = 2.0

# --- Climate chamber ---
T_WARM_1 = 30.0                     # above Tauto_off, automatic mode would be off (step 8)
T_COLD = -25.0                      # below Tauto_on, automatic mode would be on (step 18)
T_WARM_2 = 20.0                     # above Tauto_off again (step 25)
CHAMBER_WAIT_S = 3600               # "Waiting time: 3600s" (steps 8, 18, 25)

# --- Temperature criteria ---
# The wait ends as soon as the criterion holds, it is not a fixed soak.
TEMP_TIMEOUT_S = 2 * 60
TEMP_POLL_S = 1 * 60
SOAK_S = 0                          # fallback wait when Timager is unreadable


# #############################################################################
# Helper functions
# #############################################################################
def wait_for_temperatures(testresult, client, chamber, predicate, descr,
                          soak_s=SOAK_S):
    """Poll Timager and Tser until the predicate holds, then write the verdict.

    The predicate answers True, False or None, None meaning it misses a value it
    needs and can never be decided.
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

        if elapsed >= TEMP_TIMEOUT_S:
            testresult.append(["%s: not reached within %d s, %s (Tambient %s)"
                               % (descr, TEMP_TIMEOUT_S, readings, ambient), "FAILED"])
            return t_imager, t_ser

        testresult.addInfo("%s, Tambient %s (%.0f s elapsed)"
                           % (readings, ambient, elapsed))
        sleep(TEMP_POLL_S)


def switch_heating(testresult, client, value, exp_value, descr):
    """Lock the camera, write manual modified with value and read the state back.

    The lock expires after EXCLUSIVE_TTL_S, so it is taken before every write.
    """
    sleep(MIN_SWITCH_PERIOD_S)
    cs.lock(testresult, client, EXCLUSIVE_TTL_S)
    cs.set_control(testresult, client, IDX, cs.MODE_MANUAL_MODIFIED, value, descr)
    return cs.check_control(testresult, client, IDX, cs.MODE_MANUAL, exp_value, descr)


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

    def above_tauto_off(t_imager, t_ser):
        """Ambient warm enough that automatic mode would keep the heating off."""
        if t_imager is None:
            return None
        return t_imager > t_auto_off

    def below_tauto_on(t_imager, t_ser):
        """Ambient cold enough that automatic mode would switch the heating on."""
        if t_imager is None:
            return None
        return t_imager < t_auto_on

    try:
        # #####################################################################
        testresult.addHeader("Preconditions")
        # #####################################################################
        cs.log_dut_config(testresult)

        # The power cycle restores defaultHeaterMode, so no mode is written here.
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        cs.subscribe_roi(testresult, client, ROI)
        cs.stream_active(testresult, True, "active after subscribeROIVideo",
                         timeout_s=RTP_TIMEOUT_S)

        # #####################################################################
        testresult.addHeader("Manual switching at Tambient = %.0f degC" % T_WARM_1)
        # #####################################################################
        cs.set_chamber_temperature(testresult, chamber, T_WARM_1)
        sleep(CHAMBER_WAIT_S)
        wait_for_temperatures(testresult, client, chamber, above_tauto_off,
                              "Timager > %.1f degC (Tauto_off)" % t_auto_off)

        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off")

        switch_heating(testresult, client, HEATING_ON, HEATING_ON,
                       "in manual mode and on")
        switch_heating(testresult, client, HEATING_OFF, HEATING_OFF,
                       "in manual mode and off")

        # #####################################################################
        testresult.addHeader("Manual mode holds at Tambient = %.0f degC" % T_COLD)
        # #####################################################################
        cs.set_chamber_temperature(testresult, chamber, T_COLD)
        sleep(CHAMBER_WAIT_S)
        wait_for_temperatures(testresult, client, chamber, below_tauto_on,
                              "Timager < %.1f degC (Tauto_on)" % t_auto_on)

        # The manual OFF is the point of the test: Tauto_on being crossed must
        # not switch the heating back on, only automatic mode reacts to it.
        cs.check_control(testresult, client, IDX, cs.MODE_MANUAL, HEATING_OFF,
                         "still in manual mode and off although Tambient < Tauto_on")

        switch_heating(testresult, client, HEATING_ON, HEATING_ON,
                       "in manual mode and on")

        # #####################################################################
        testresult.addHeader("Switch back to automatic mode at Tambient = %.0f degC"
                             % T_WARM_2)
        # #####################################################################
        cs.set_chamber_temperature(testresult, chamber, T_WARM_2)
        sleep(CHAMBER_WAIT_S)
        wait_for_temperatures(testresult, client, chamber, above_tauto_off,
                              "Timager > %.1f degC (Tauto_off)" % t_auto_off)

        switch_heating(testresult, client, HEATING_OFF, HEATING_OFF,
                       "in manual mode and off")

        cs.lock(testresult, client, EXCLUSIVE_TTL_S)
        cs.set_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                       "automatic heating mode")
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off")

        wait_for_temperatures(testresult, client, chamber, above_tauto_off,
                              "still Timager > %.1f degC (Tauto_off) after the "
                              "switch to automatic" % t_auto_off)

        # #####################################################################
        testresult.addHeader("Postcondition: stream off")
        # #####################################################################
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


#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-100346-Check_heating_modes_during_runtime_OP_active.py
# Task : Over-temperature protection overrides a manual ON during runtime, and
#        releases it again once Timager/Tser return within bounds
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 07.09.2026 | Martin Oeder  | initial
#******************************************************************************
"""
Entering the protection state:  Timager >= Timg_prot_on OR Tser > Tser_prot_on
Returning to normal operation:  Timager <= Timg_prot_off AND Tser <= Tser_prot_off

The central check is the readout after a manual ON: the protection has to keep the
heating off, so the value stays 0.
"""
from time import sleep, perf_counter

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-100346"

SUPPLY_CH = 1
SUPPLY_V = 28.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_HEATER
HEATING_ON = 0x0001
HEATING_OFF = 0x0000
EXCLUSIVE_TTL_S = 1                 # the steps lock the camera for 1 s per write
MIN_SWITCH_PERIOD_S = 1             # t_heater_min_switch_period between two switches

# Hard-coded in the DUT software, not part of the parameter set.
T_SER_PROT_ON = 40.0
T_SER_PROT_OFF = 35.0

# --- Climate chamber ---
T_HOT = 50.0                        # drives the DUT into the protection state
T_COLD = 20.0                       # brings it back to normal operation
CHAMBER_WAIT_S = 3600               # "Waiting time: 3600s" (steps 6 and 18)

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
    t_img_prot_on = sw.t_imager_protection_on_c
    t_img_prot_off = sw.t_imager_protection_off_c
    t_auto_off = sw.t_imager_auto_off_c

    def in_protection(t_imager, t_ser):
        """Entering condition, an OR, so one known value can already satisfy it.

        Undecidable (None) only while no value at all can be read.
        """
        if t_imager is None and t_ser is None:
            return None
        return ((t_imager is not None and t_imager >= t_img_prot_on)
                or (t_ser is not None and t_ser > T_SER_PROT_ON))

    def out_of_protection(t_imager, t_ser):
        """Return condition, an AND.

        A readable value that misses its limit decides the condition as false,
        the DUT is then still on its way and the test keeps waiting. Only once
        every readable value is inside its limit does a missing one make the
        condition undecidable (None).
        """
        if t_ser is not None and t_ser > T_SER_PROT_OFF:
            return False
        if t_imager is not None and (t_imager > t_img_prot_off
                                     or t_imager <= t_auto_off):
            return False
        if t_imager is None or t_ser is None:
            return None
        return True

    try:
        # #####################################################################
        testresult.addHeader("Preconditions")
        # #####################################################################
        cs.log_dut_config(testresult)

        # The power cycle restores defaultHeaterMode, so no mode is written here.
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        # #####################################################################
        testresult.addHeader("Protection state at Tambient = %.0f degC" % T_HOT)
        # #####################################################################
        cs.set_chamber_temperature(testresult, chamber, T_HOT)
        sleep(CHAMBER_WAIT_S)
        wait_for_temperatures(testresult, client, chamber, in_protection,
                              "Timager >= %.1f degC or Tser > %.1f degC"
                              % (t_img_prot_on, T_SER_PROT_ON))

        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off")

        # The manual ON is the point of the test: the protection has to override it.
        switch_heating(testresult, client, HEATING_ON, HEATING_OFF,
                       "in manual mode and off although ON was written")
        switch_heating(testresult, client, HEATING_OFF, HEATING_OFF,
                       "in manual mode and off")

        # #####################################################################
        testresult.addHeader("Normal operation at Tambient = %.0f degC" % T_COLD)
        # #####################################################################
        cs.set_chamber_temperature(testresult, chamber, T_COLD)
        sleep(CHAMBER_WAIT_S)
        wait_for_temperatures(testresult, client, chamber, out_of_protection,
                              "Timager <= %.1f degC and Tser <= %.1f degC and "
                              "Timager > %.1f degC"
                              % (t_img_prot_off, T_SER_PROT_OFF, t_auto_off))

        switch_heating(testresult, client, HEATING_OFF, HEATING_OFF,
                       "in manual mode and off")

        cs.lock(testresult, client, EXCLUSIVE_TTL_S)
        cs.set_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                       "in automatic mode")
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, HEATING_OFF,
                         "in automatic mode and off")

        wait_for_temperatures(testresult, client, chamber, out_of_protection,
                              "still out of protection after the switch to automatic")

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

#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92780-Shutter_modes_default_configuration_at_startup.py
# Task : Shutter modes: default configuration at startup
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 04.08.2026 | Ehu Li   | initial  
#******************************************************************************
from time import sleep

from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92780"

SUPPLY_CH = 1
SUPPLY_V = 24.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_SHUTTER
OPEN = 0x0001
CLOSED = 0x0000
ROI = 0
SHUTTER_MOVE_S = 1                  # t_shutter_open is 0.7 s


# #############################################################################
# Helper functions
# #############################################################################
def expect_shutter(testresult, client, value, descr):
    """Read the shutter control and expect automatic mode with the given value."""
    return cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, value, descr)


# #############################################################################
# Test
# #############################################################################
with TestEnv(testcase_id=TESTCASE_ID) as testenv:

    testresult = testenv.getResults()
    psu = testenv.getPSU()
    client = None

    try:
        # #####################################################################
        testresult.addHeader("First startup: shutter defaults to automatic mode")
        # #####################################################################
        cs.log_dut_config(testresult)
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        expect_shutter(testresult, client, CLOSED,
                       "in automatic mode and closed after startup")

        cs.subscribe_roi(testresult, client, ROI)
        sleep(SHUTTER_MOVE_S)
        expect_shutter(testresult, client, OPEN,
                       "in automatic mode and open while streaming")

        # #####################################################################
        testresult.addHeader("Second startup: the default is reproducible")
        # #####################################################################
        client.close_socket()
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        expect_shutter(testresult, client, CLOSED,
                       "in automatic mode and closed after startup")

        cs.subscribe_roi(testresult, client, ROI)
        sleep(SHUTTER_MOVE_S)
        expect_shutter(testresult, client, OPEN,
                       "in automatic mode and open while streaming")

        cs.unsubscribe_roi(testresult, client, ROI)
        sleep(SHUTTER_MOVE_S)
        expect_shutter(testresult, client, CLOSED,
                       "in automatic mode and closed after the stream was stopped")

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        if client is not None:
            client.close_socket()

        if POWER_OFF_AT_END:
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

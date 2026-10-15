#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92785-Shutter_mode_activation_during_runtime.py
# Task : Shutter mode activation during runtime
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 03.08.2026 | Ehu Li   | initial  
#******************************************************************************
from time import sleep

from _automation_wrapper_ import TestEnv
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92785"

SUPPLY_CH = 1
SUPPLY_V = 24.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_SHUTTER
OPEN = 0x0001
CLOSED = 0x0000
ROI = 3
EXCLUSIVE_TTL_S = 360               # one lock for the whole test, released at the end
SHUTTER_MOVE_S = 2                  # t_shutter_open is 0.7 s


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

        # #####################################################################
        testresult.addHeader("Automatic mode follows the video stream")
        # #####################################################################
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, CLOSED,
                         "in automatic mode and closed")

        cs.subscribe_roi(testresult, client, ROI)
        sleep(SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, OPEN,
                         "in automatic mode and open")

        # #####################################################################
        testresult.addHeader("ManualModified applies the control value")
        # #####################################################################
        cs.lock(testresult, client, EXCLUSIVE_TTL_S)

        cs.set_control(testresult, client, IDX, cs.MODE_MANUAL_MODIFIED, OPEN,
                       "switch to ManualModified ON", settle_s=SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_MANUAL, OPEN,
                         "in manual mode and open")

        cs.set_control(testresult, client, IDX, cs.MODE_MANUAL_MODIFIED, CLOSED,
                       "switch to ManualModified OFF", settle_s=SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_MANUAL, CLOSED,
                         "in manual mode and closed")

        # #####################################################################
        testresult.addHeader("Manual mode ignores the control value")
        # #####################################################################
        cs.set_control(testresult, client, IDX, cs.MODE_MANUAL, OPEN,
                       "switch to Manual ON", settle_s=SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_MANUAL, CLOSED,
                         "in manual mode and closed")

        cs.set_control(testresult, client, IDX, cs.MODE_MANUAL, CLOSED,
                       "switch to Manual OFF", settle_s=SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_MANUAL, CLOSED,
                         "in manual mode and closed")

        # #####################################################################
        testresult.addHeader("Manual mode overrides the video stream")
        # #####################################################################
        cs.subscribe_roi(testresult, client, ROI)
        sleep(SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_MANUAL, CLOSED,
                         "in manual mode and closed while the stream is active")

        # #####################################################################
        testresult.addHeader("Automatic mode takes control back")
        # #####################################################################
        cs.set_control(testresult, client, IDX, cs.MODE_AUTOMATIC, CLOSED,
                       "switch to Automatic", settle_s=SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, OPEN,
                         "in automatic mode and open")

        cs.unsubscribe_roi(testresult, client, ROI)
        sleep(SHUTTER_MOVE_S)
        cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, CLOSED,
                         "in automatic mode and closed")

        cs.unlock(testresult, client)

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

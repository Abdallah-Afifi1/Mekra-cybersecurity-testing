#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-100520-Shutter_behavior_in_automatic_mode.py
# Task : Shutter behavior in automatic mode with dual streaming (HV / CV)
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
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-100520"

SUPPLY_CH = 1
SUPPLY_V = 24.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_SHUTTER
OPEN = 0x0001
CLOSED = 0x0000
SHUTTER_MOVE_S = 1                  # t_shutter_open is 0.7 s

# Full 4-byte ROI payload: bit 31 flip, bit 30 mirror, bits 7..0 the ROI index.
ROI_HV = 0xC0000003                 # human vision, ROI 3
ROI_CV = 0xC000000A                 # computer vision, ROI 10


# #############################################################################
# Helper functions
# #############################################################################
def expect_shutter(testresult, client, value, descr):
    """Read the shutter control and expect automatic mode with the given value."""
    return cs.check_control(testresult, client, IDX, cs.MODE_AUTOMATIC, value, descr)


def subscribe(testresult, client, roi):
    """Subscribe one ROI and give the shutter time to move."""
    cs.subscribe_roi(testresult, client, roi)
    sleep(SHUTTER_MOVE_S)


def unsubscribe(testresult, client, roi):
    """Unsubscribe one ROI and give the shutter time to move."""
    cs.unsubscribe_roi(testresult, client, roi)
    sleep(SHUTTER_MOVE_S)


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
        testresult.addHeader("HV first: the shutter closes only with the last stream")
        # #####################################################################
        expect_shutter(testresult, client, CLOSED, "closed without any stream")

        subscribe(testresult, client, ROI_HV)
        expect_shutter(testresult, client, OPEN, "open with HV streaming")

        subscribe(testresult, client, ROI_CV)
        expect_shutter(testresult, client, OPEN, "open with HV and CV streaming")

        unsubscribe(testresult, client, ROI_HV)
        expect_shutter(testresult, client, OPEN, "still open, CV is streaming")

        unsubscribe(testresult, client, ROI_CV)
        expect_shutter(testresult, client, CLOSED, "closed after the last stream")

        # #####################################################################
        testresult.addHeader("CV first: same behaviour in the other order")
        # #####################################################################
        subscribe(testresult, client, ROI_CV)
        expect_shutter(testresult, client, OPEN, "open with CV streaming")

        subscribe(testresult, client, ROI_HV)
        expect_shutter(testresult, client, OPEN, "open with CV and HV streaming")

        unsubscribe(testresult, client, ROI_CV)
        expect_shutter(testresult, client, OPEN, "still open, HV is streaming")

        unsubscribe(testresult, client, ROI_HV)
        expect_shutter(testresult, client, CLOSED, "closed after the last stream")

        # #####################################################################
        testresult.addHeader("The same ROI subscribed twice keeps it open")
        # #####################################################################
        subscribe(testresult, client, ROI_HV)
        expect_shutter(testresult, client, OPEN, "open with HV streaming")

        subscribe(testresult, client, ROI_HV)
        expect_shutter(testresult, client, OPEN, "open after subscribing HV again")

        # #####################################################################
        testresult.addHeader("After a restart: CV only, subscribed twice")
        # #####################################################################
        client.close_socket()
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        expect_shutter(testresult, client, CLOSED, "closed without any stream")

        subscribe(testresult, client, ROI_CV)
        expect_shutter(testresult, client, OPEN, "open with CV streaming")

        subscribe(testresult, client, ROI_CV)
        expect_shutter(testresult, client, OPEN, "open after subscribing CV again")

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

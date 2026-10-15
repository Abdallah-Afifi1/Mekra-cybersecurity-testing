#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-100610-Shutter_not_Supported.py
# Task : MVC does not support a shutter (only valid for DUTs without a shutter)
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
TESTCASE_ID = "HIL_Test.MVC-100610"

SUPPLY_CH = 1
SUPPLY_V = 24.0
POWER_OFF_AT_END = True

USE_DHCP = True                     # the DUT is power-cycled and asks for an address

IDX = cs.CTRL_IDX_SHUTTER
RC_INVALID_CONTROL_INDEX = 0x35
EXCLUSIVE_TTL_S = 360

# Full 4-byte ROI payload: bit 31 flip, bit 30 mirror, bits 7..0 the ROI index.
ROI = 0xC0000003

# #############################################################################
# Helper functions
# #############################################################################
def expect_shutter_rejected(testresult, client, descr):
    """getCamControl on the shutter index has to be rejected."""
    rx = cs.send(client, cs.build_request(cs.M_GET_CAM_CONTROL, 0x09, bytes([IDX])))
    return cs.negative_response(testresult, rx, cs.M_GET_CAM_CONTROL,
                                RC_INVALID_CONTROL_INDEX,
                                "getCamControl shutter %s" % descr)


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
        testresult.addHeader("The shutter control index is rejected")
        # #####################################################################
        expect_shutter_rejected(testresult, client, "after startup")

        # #####################################################################
        testresult.addHeader("A running video stream does not create a shutter")
        # #####################################################################
        cs.subscribe_roi(testresult, client, ROI)
        expect_shutter_rejected(testresult, client, "while the stream is active")

        # #####################################################################
        testresult.addHeader("Writing the shutter control is rejected as well")
        # #####################################################################
        cs.lock(testresult, client, EXCLUSIVE_TTL_S)

        payload = bytes([IDX, cs.SUPPORTED_MODES, cs.MODE_MANUAL_MODIFIED]) \
            + (0x0001).to_bytes(2, "big")
        rx = cs.send(client, cs.build_request(cs.M_SET_CAM_CONTROL, 0x0D, payload))
        cs.negative_response(testresult, rx, cs.M_SET_CAM_CONTROL,
                             RC_INVALID_CONTROL_INDEX,
                             "setCamControl shutter ManualModified ON")

        expect_shutter_rejected(testresult, client, "after the rejected write")

        # #####################################################################
        testresult.addHeader("Postcondition: the service stays usable")
        # #####################################################################
        cs.unsubscribe_roi(testresult, client, ROI)
        expect_shutter_rejected(testresult, client, "after the stream was stopped")

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

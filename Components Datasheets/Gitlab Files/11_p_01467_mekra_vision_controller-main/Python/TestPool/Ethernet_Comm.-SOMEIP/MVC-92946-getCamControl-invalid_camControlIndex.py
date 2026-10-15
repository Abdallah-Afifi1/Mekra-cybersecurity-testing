#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92946-getCamControl-invalid_camControlIndex.py
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
# The test steps end with U_in = 0.0 V and specify no request with a valid
# control index. The postcondition below adds one, so a failure of all 19 checks
# cannot be mistaken for a camera that stopped answering getCamControl entirely.
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92946"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # test step 22: U_in = 0.0 V

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# getCamControl carries the control index as a 1-byte payload, so the length
# field is 0x08 header + 1 byte.
REQUEST_LENGTH = 0x09

# Control indices to reject. The camera implements 0x09 (heater) and 0x50
# (shutter), see cs.CTRL_IDX_HEATER / cs.CTRL_IDX_SHUTTER. The list walks around
# both of them: 0x08 / 0x0A and 0x4F / 0x52 are their direct neighbours, 0x00 is
# the low boundary and 0xFF the high one.
INVALID_CONTROL_INDICES = [0x00, 0x01, 0x03, 0x04, 0x07, 0x08, 0x0A, 0x0B, 0x0C,
                           0x0D, 0x0F, 0x10, 0x40, 0x4F, 0x52, 0x5F, 0x49, 0x70,
                           0xFF]


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
        testresult.addHeader("Invalid control indices are rejected with "
                             "E_INVALID_CONTROL_INDEX")
        # #####################################################################
        for control_index in INVALID_CONTROL_INDICES:
            someipcheck.send_and_check_error(
                testresult, client,
                cs.build_request(cs.M_GET_CAM_CONTROL, REQUEST_LENGTH,
                                 bytes([control_index])),
                someipcheck.RC_E_INVALID_CONTROL_INDEX,
                "getCamControl, control index 0x%02X" % control_index)

        # #####################################################################
        testresult.addHeader("Postcondition: a valid control index still answers")
        # #####################################################################
        rx = cs.send(client, cs.build_request(cs.M_GET_CAM_CONTROL, REQUEST_LENGTH,
                                              bytes([cs.CTRL_IDX_HEATER])))
        cs.positive_response(testresult, rx, cs.M_GET_CAM_CONTROL,
                             "getCamControl on the implemented control index "
                             "0x%02X (heater)" % cs.CTRL_IDX_HEATER)

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        SomeipClient.close_clients(client)

        if POWER_OFF_AT_END:
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

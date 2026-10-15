#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92940-eraseCamExclusive-not_locked.py
# Task : Validation of Exclusive lock of the camera
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 08.09.2026 | Martin Oeder  | initial
# 1.1.0  | 09.09.2026 | Martin Oeder  | shared steps moved to someip_checks
#******************************************************************************
#******************************************************************************
# """Deviations from the test steps, so the report states them."""
#
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92940"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address


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

        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                             "camera not locked")

        # #####################################################################
        testresult.addHeader("eraseCamExclusive while not locked is rejected "
                             "with E_NOT_LOCKED")
        # #####################################################################
        someipcheck.send_and_check_negative(testresult, client,
                                    cs.build_request(cs.M_ERASE_CAM_EXCLUSIVE, 0x08),
                                    cs.M_ERASE_CAM_EXCLUSIVE,
                                    someipcheck.RC_E_NOT_LOCKED,
                                    "eraseCamExclusive (camera not locked)")

        # #####################################################################
        testresult.addHeader("Postcondition: camera is still not locked")
        # #####################################################################
        someipcheck.check_lock_state(testresult, client, someipcheck.LOCKED_BY_NONE,
                             "camera not locked")

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        SomeipClient.close_clients(client)

        if POWER_OFF_AT_END:
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

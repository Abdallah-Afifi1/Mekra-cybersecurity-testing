#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92891-SOMEIP_message_header-wrong_interface_version.py
# Task : Wrong interface version is rejected with E_WRONG_INTERFACE_VERSION
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 01.09.2026 | Martin Oeder  | initial
# 1.1.0  | 10.09.2026 | Martin Oeder  | shared steps moved to someip_checks
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92891"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_nominal
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Method used for most of the test: it exists and takes no payload (getCamStatus),
# only the interface version is invalid.
METHOD_ID = cs.M_GET_CAM_STATUS     # 0x0002
REQUEST_LENGTH = 0x08

# Interface versions to reject, none of them is the valid version 0x01. 0x00 is
# the low boundary, 0xFF the high boundary, 0x02 / 0x03 are the direct neighbours
# of the valid version, 0xAB / 0xF0 are generic placeholders.
WRONG_INTERFACE_VERSIONS = [0x00, 0xAB, 0xFF, 0x02, 0x03, 0xF0]

# Step 9: the same check on setCamExclusive with a non-empty payload, to prove
# the interface version is validated before the payload is even evaluated.
EXCL_METHOD_ID = cs.M_SET_CAM_EXCLUSIVE     # 0x0011
EXCL_INTERFACE_VERSION = 0x11
EXCL_TTL_S = 2
EXCL_PAYLOAD = EXCL_TTL_S.to_bytes(4, "big")  # setCamExclusive payload: ttl in s
EXCL_REQUEST_LENGTH = 0x0C


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
        cs.service_answers(testresult, client, METHOD_ID)

        # #####################################################################
        testresult.addHeader("Positive control: known interface version is "
                             "accepted")
        # #####################################################################
        rx = cs.send(client, cs.build_request(METHOD_ID, REQUEST_LENGTH))
        cs.positive_response(testresult, rx, METHOD_ID,
                             "getCamStatus (0x%04X) on the valid interface version "
                             "0x01" % METHOD_ID)

        # #####################################################################
        testresult.addHeader("Wrong interface versions are rejected with "
                             "E_WRONG_INTERFACE_VERSION")
        # #####################################################################
        for wrong_version in WRONG_INTERFACE_VERSIONS:
            someipcheck.send_and_check_error(
                testresult, client,
                someipcheck.build_request(METHOD_ID, REQUEST_LENGTH,
                                 interface_version=wrong_version),
                someipcheck.RC_E_WRONG_INTERFACE_VERSION,
                "Interface Version 0x%02X (method 0x%04X)"
                % (wrong_version, METHOD_ID))

        # A SET method with a payload is checked the same way as a GET method.
        someipcheck.send_and_check_error(
            testresult, client,
            someipcheck.build_request(EXCL_METHOD_ID, EXCL_REQUEST_LENGTH, EXCL_PAYLOAD,
                             interface_version=EXCL_INTERFACE_VERSION),
            someipcheck.RC_E_WRONG_INTERFACE_VERSION,
            "Interface Version 0x%02X (method 0x%04X)"
            % (EXCL_INTERFACE_VERSION, EXCL_METHOD_ID))

        # #####################################################################
        testresult.addHeader("Postcondition: service still available")
        # #####################################################################
        rx = cs.send(client, cs.build_request(METHOD_ID, REQUEST_LENGTH))
        cs.positive_response(testresult, rx, METHOD_ID,
                             "getCamStatus (0x%04X) still answered on the valid "
                             "interface version after the rejected requests"
                             % METHOD_ID)

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

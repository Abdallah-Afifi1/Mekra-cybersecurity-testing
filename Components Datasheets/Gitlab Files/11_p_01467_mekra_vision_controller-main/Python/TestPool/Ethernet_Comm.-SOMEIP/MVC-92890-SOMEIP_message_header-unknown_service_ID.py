#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92890-SOMEIP_message_header-unknown_service_ID.py
# Task : Unknown Service ID is rejected with E_UNKNOWN_SERVICE
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
from tools.SOMEIP.someip_packet import SomeipPacket
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92890"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_nominal
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Method ID used in every request; it exists (getCamStatus), only the service ID
# under test is invalid.
METHOD_ID = cs.M_GET_CAM_STATUS     # 0x0002
VALID_SERVICE_RESP_LENGTH = 0x0F

# Service IDs to reject, none of them is the camera's own service ID
# (cs.SERVICE_ID, 0x433F). 0x433E / 0x4340 are its direct neighbours,
# 0x0000 / 0x0001 are the low boundary, 0xFFFF the high boundary, 0xAFFE a
# generic mid-range placeholder.
UNKNOWN_SERVICES = [0x433E, 0x4340, 0x0001, 0xFFFF, 0xAFFE, 0x0000]


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
        testresult.addHeader("Positive control: known service ID is accepted")
        # #####################################################################
        rx = cs.send(client, cs.build_request(METHOD_ID, 0x08))
        if rx is None:
            testresult.append(["getCamStatus (0x%04X): no response from camera"
                               % METHOD_ID, "FAILED"])
        else:
            testresult.addInfo("Response: %s"
                               % " ".join(SomeipPacket.get_packet_stream(rx)))
            testresult.append([
                "Known service ID 0x%04X answered with message type 0x%s, return "
                "code 0x%s, length 0x%s (expected 0x80 / 0x00 / 0x%08X)"
                % (cs.SERVICE_ID, rx.get_message_type(), rx.get_return_code(),
                   rx.get_length(), VALID_SERVICE_RESP_LENGTH),
                "PASSED" if (rx.get_message_type() == "80"
                             and rx.get_return_code() == "00"
                             and rx.get_length() == "%08x" % VALID_SERVICE_RESP_LENGTH)
                else "FAILED"])

        # #####################################################################
        testresult.addHeader("Unknown service IDs are rejected with "
                             "E_UNKNOWN_SERVICE")
        # #####################################################################
        for unknown_service in UNKNOWN_SERVICES:
            someipcheck.send_and_check_error(testresult, client,
                                    someipcheck.build_request(METHOD_ID, 0x08,
                                                     service_id=unknown_service),
                                    someipcheck.RC_E_UNKNOWN_SERVICE,
                                    "Unknown Service ID 0x%04X" % unknown_service)

        # #####################################################################
        testresult.addHeader("Postcondition: service still available")
        # #####################################################################
        rx = cs.send(client, cs.build_request(METHOD_ID, 0x08))
        cs.positive_response(testresult, rx, METHOD_ID,
                             "getCamStatus (0x%04X) still answered on the valid "
                             "service ID after the rejected requests" % METHOD_ID)

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

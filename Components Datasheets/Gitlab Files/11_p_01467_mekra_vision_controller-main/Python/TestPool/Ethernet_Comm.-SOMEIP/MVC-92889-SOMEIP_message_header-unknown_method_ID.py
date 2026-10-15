#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92417-Unknown_Method_ID.py
# Task : Unknown Method ID is rejected with E_UNKNOWN_METHOD
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 03.08.2026 | Ehu Li   | initial
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
TESTCASE_ID = "HIL_Test.MVC-92889"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 24.0                     # U_nominal
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# Positive control: a method the camera implements, to prove it tells known from
# unknown apart.
VALID_METHOD = 0x0010               # getCamIdentification
VALID_METHOD_RESP_LENGTH = 0x17

# Method IDs to reject, none of them is a documented method of the service.
# 0x0202 sits between setCamControl and getCamControl, 0x7FFF is the highest ID
# in the method range, 0xFFFF is already in the event range.
UNKNOWN_METHODS = [0x0000, 0x0003, 0x0022, 0x0202, 0x0306, 0x7FFF, 0xFFFF]


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
        cs.service_answers(testresult, client, VALID_METHOD)

        # #####################################################################
        testresult.addHeader("Positive control: known method is accepted")
        # #####################################################################
        rx = cs.send(client, cs.build_request(VALID_METHOD, 0x08))
        if rx is None:
            testresult.append(["getCamIdentification (0x%04X): no response from camera"
                               % VALID_METHOD, "FAILED"])
        else:
            testresult.addInfo("Response: %s"
                               % " ".join(SomeipPacket.get_packet_stream(rx)))
            testresult.append([
                "Known method 0x%04X answered with message type 0x%s, return code "
                "0x%s, length 0x%s (expected 0x80 / 0x00 / 0x%08X)"
                % (VALID_METHOD, rx.get_message_type(), rx.get_return_code(),
                   rx.get_length(), VALID_METHOD_RESP_LENGTH),
                "PASSED" if (rx.get_message_type() == "80"
                             and rx.get_return_code() == "00"
                             and rx.get_length() == "%08x" % VALID_METHOD_RESP_LENGTH)
                else "FAILED"])

        # #####################################################################
        testresult.addHeader("Unknown method IDs are rejected with E_UNKNOWN_METHOD")
        # #####################################################################
        for unknown_method in UNKNOWN_METHODS:
            someipcheck.send_and_check_error(testresult, client,
                                    cs.build_request(unknown_method, 0x08),
                                    someipcheck.RC_E_UNKNOWN_METHOD,
                                    "Unknown Method ID 0x%04X" % unknown_method)

        # #####################################################################
        testresult.addHeader("Postcondition: service still available")
        # #####################################################################
        rx = cs.send(client, cs.build_request(VALID_METHOD, 0x08))
        testresult.append([
            "Known method 0x%04X still answered after the rejected requests"
            % VALID_METHOD,
            "PASSED" if (rx is not None and rx.get_message_type() == "80"
                         and rx.get_return_code() == "00") else "FAILED"])

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

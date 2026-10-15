#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92888-SOMEIP_message_header-malformed_message.py
# Task : Validation of message length
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 08.09.2026 | Martin Oeder  | initial
# 1.1.0  | 10.09.2026 | Martin Oeder  | shared steps moved to someip_checks
#******************************************************************************
#******************************************************************************
# """Deviations from the test steps, so the report states them."""
#
#******************************************************************************
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.helpFunctions import camera_steps as cs
from tools.SOMEIP.someip_client import SomeipClient


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92888"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 1-2
POWER_OFF_AT_END = True             # leave the bench powered down for the next test

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

M_GET_DATA_SHEET = 0x0001           # getDataSheet, not exposed as a constant in
                                     # camera_steps.py

# Each entry sends one implemented method with a Length/Payload that does not
# match what that specific method expects. Most entries keep the declared Length
# consistent with the actual bytes sent (just wrong for the method); the two
# marked entries go further and also break the raw framing itself (the declared
# Length does not match the real byte count on the wire). Either way the camera
# is expected to return E_MALFORMED_MESSAGE.
MALFORMED_REQUESTS = [
    {
        "descr": "getCamStatus, length 0x09 (1-byte payload instead of none)",
        "method_id": cs.M_GET_CAM_STATUS,
        "length": 0x00000009,
        "payload": bytes([0x01]),
    },
    {
        "descr": "getCamStatus, length 0x0A (2-byte payload instead of none)",
        "method_id": cs.M_GET_CAM_STATUS,
        "length": 0x0000000A,
        "payload": bytes.fromhex("1111"),
    },
    {
        "descr": "getDataSheet, length 0x0A (2-byte payload instead of none)",
        "method_id": cs.M_GET_DATA_SHEET,
        "length": 0x0000000A,
        "payload": bytes.fromhex("1111"),
    },
    {
        "descr": "setCamExclusive, length 0x08 (no payload instead of the "
                 "4-byte TTL)",
        "method_id": cs.M_SET_CAM_EXCLUSIVE,
        "length": 0x00000008,
        "payload": None,
    },
    {
        "descr": "eraseCamExclusive, length 0x09 (1-byte payload instead of "
                 "none)",
        "method_id": cs.M_ERASE_CAM_EXCLUSIVE,
        "length": 0x00000009,
        "payload": bytes([0xFF]),
    },
    {
        "descr": "subscribeROIVideo, length 0x08 (no payload instead of the "
                 "4-byte ROI)",
        "method_id": cs.M_SUBSCRIBE_ROI_VIDEO,
        "length": 0x00000008,
        "payload": None,
    },
    {
        "descr": "subscribeROIVideo, length 0x0A but an 8-byte payload actually "
                 "attached (raw framing mismatch, real length 0x10)",
        "method_id": cs.M_SUBSCRIBE_ROI_VIDEO,
        "length": 0x0000000A,
        "payload": bytes.fromhex("1111111111111111"),
    },
    {
        "descr": "unsubscribeROIVideo, length 0x08 (no payload instead of the "
                 "4-byte ROI)",
        "method_id": cs.M_UNSUBSCRIBE_ROI_VIDEO,
        "length": 0x00000008,
        "payload": None,
    },
    {
        "descr": "setCamControl, length 0x08 (no payload instead of the 5-byte "
                 "control block)",
        "method_id": cs.M_SET_CAM_CONTROL,
        "length": 0x00000008,
        "payload": None,
    },
    {
        "descr": "setCamControl, length 0x0B (3-byte payload instead of the "
                 "5-byte control block)",
        "method_id": cs.M_SET_CAM_CONTROL,
        "length": 0x0000000B,
        "payload": bytes.fromhex("234567"),
    },
    {
        "descr": "getCamControl, length 0x08 (no payload instead of the 1-byte "
                 "control index)",
        "method_id": cs.M_GET_CAM_CONTROL,
        "length": 0x00000008,
        "payload": None,
    },
    {
        "descr": "getCamControl, length 0x09 but a 4-byte payload actually "
                 "attached (raw framing mismatch, real length 0x0C)",
        "method_id": cs.M_GET_CAM_CONTROL,
        "length": 0x00000009,
        "payload": bytes.fromhex("deadbeef"),
    },
]


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
        testresult.addHeader("Malformed length/payload per Method ID is "
                             "rejected with E_MALFORMED_MESSAGE")
        # #####################################################################
        for case in MALFORMED_REQUESTS:
            someipcheck.send_and_check_error(testresult, client,
                                    cs.build_request(case["method_id"],
                                                     case["length"],
                                                     case["payload"]),
                                    someipcheck.RC_E_MALFORMED_MESSAGE, case["descr"])

        # #####################################################################
        testresult.addHeader("Postcondition: a well-formed request still returns "
                             "E_OK")
        # #####################################################################
        rx = cs.send(client, cs.build_request(cs.M_GET_CAM_STATUS, 0x08))
        cs.positive_response(testresult, rx, cs.M_GET_CAM_STATUS,
                             "getCamStatus (0x%04X) with a valid header"
                             % cs.M_GET_CAM_STATUS)

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

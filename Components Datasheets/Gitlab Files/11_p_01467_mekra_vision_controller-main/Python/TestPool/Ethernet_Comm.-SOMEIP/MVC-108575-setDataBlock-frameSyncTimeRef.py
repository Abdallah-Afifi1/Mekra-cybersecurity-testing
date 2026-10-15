#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-108575-setDataBlock-frameSyncTimeRef.py
# Task : frameSyncTimeRef only accepts a higher value and is volatile
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
# Test steps 4, 5 and 7: the response length is given as 0x00000014 together
# with "no Payload", which contradicts itself. Asserted is 0x08, the length of a
# response without payload.
# Return code 0x51 (E_INVALID_BLOCK_DEFINITION) is not in the table of
# helperModule.get_human_readable_return_code(), so the report shows an empty
# name next to the code.
#
#******************************************************************************
"""
frameSyncTimeRef is an absolute timestamp in ns. setDataBlock accepts a new value
only when it is higher than the current one, a lower one is rejected with
E_INVALID_BLOCK_DEFINITION.

Test steps 8 and 9 power-cycle the DUT: step 10 expects the default value back,
so the written value is volatile.

The client socket has to be closed before the camera is powered up again,
SomeipClient binds a fixed source port.
"""
from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_checks as someipcheck
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-108575"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 2 and 9
POWER_OFF_AT_END = True             # test step 11: U_in = 0.0 V

# --- Network ---
USE_DHCP = True                     # the DUT is power-cycled and asks for an address

# --- The data block under test ---
DEVICE_ID = cs.DEVICE_SOW2_RUNTIME          # 0x0001
BLOCK_ID = cs.BLOCK_FRAME_SYNC_TIME_REF     # 0x0000, frameSyncTimeRef
BLOCK_SIZE = 8                      # the block carries an 8-byte timestamp
SET_REQUEST_LENGTH = 0x18           # 8 header + 2 device + 2 block + 4 size + 8 value

# --- frameSyncTimeRef values, absolute timestamps in ns ---
DEFAULT_NS = 0x01D2EB40             # 30 600 000 ns, the value after a power cycle
LOWER_NS = 0x01C9C380               # 30 000 000 ns, below the current value
HIGHER_NS = 0x021F3680              # 35 600 000 ns, above the current value


# #############################################################################
# Helper functions
# #############################################################################
def check_frame_sync_time_ref(testresult, client, expected_ns, descr):
    """getDataBlock on frameSyncTimeRef and compare the 8-byte timestamp."""
    content, reason = cs.data_block(client, DEVICE_ID, BLOCK_ID)
    if content is None:
        testresult.append(["getDataBlock (frameSyncTimeRef, %s): %s"
                           % (descr, reason), "FAILED"])
        return False

    expected = "%0*x" % (BLOCK_SIZE * 2, expected_ns)
    passed = (content == expected)
    testresult.append(["frameSyncTimeRef shall be 0x%s (%s): received 0x%s [%s]"
                       % (expected, descr, content, reason),
                       "PASSED" if passed else "FAILED"])
    return passed


def set_frame_sync_time_ref(testresult, client, value_ns, descr,
                            expected_rc=None):
    """setDataBlock on frameSyncTimeRef, positive unless expected_rc is given."""
    payload = (DEVICE_ID.to_bytes(2, "big")
               + BLOCK_ID.to_bytes(2, "big")
               + BLOCK_SIZE.to_bytes(4, "big")
               + value_ns.to_bytes(BLOCK_SIZE, "big"))
    request = cs.build_request(cs.M_SET_DATA_BLOCK, SET_REQUEST_LENGTH, payload)
    full_descr = "setDataBlock (frameSyncTimeRef 0x%0*X, %s)" % (BLOCK_SIZE * 2,
                                                                 value_ns, descr)

    rx = cs.send(client, request)
    if expected_rc is None:
        passed = cs.positive_response(testresult, rx, cs.M_SET_DATA_BLOCK,
                                      full_descr)
    else:
        passed = cs.negative_response(testresult, rx, cs.M_SET_DATA_BLOCK,
                                      expected_rc, full_descr)

    # The response carries no payload, so the length field is back to 8.
    return someipcheck.check_no_payload(testresult, rx, full_descr) and passed


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
        testresult.addHeader("frameSyncTimeRef starts at its default value")
        # #####################################################################
        check_frame_sync_time_ref(testresult, client, DEFAULT_NS,
                                  "default after start")

        # #####################################################################
        testresult.addHeader("A lower frameSyncTimeRef is rejected with "
                             "E_INVALID_BLOCK_DEFINITION")
        # #####################################################################
        set_frame_sync_time_ref(testresult, client, LOWER_NS,
                                "below the current value",
                                expected_rc=someipcheck.RC_E_INVALID_BLOCK_DEFINITION)

        # #####################################################################
        testresult.addHeader("A higher frameSyncTimeRef is accepted")
        # #####################################################################
        set_frame_sync_time_ref(testresult, client, HIGHER_NS,
                                "above the current value")
        check_frame_sync_time_ref(testresult, client, HIGHER_NS,
                                  "the value just written")

        # #####################################################################
        testresult.addHeader("A lower frameSyncTimeRef is still rejected")
        # #####################################################################
        set_frame_sync_time_ref(testresult, client, LOWER_NS,
                                "below the new current value",
                                expected_rc=someipcheck.RC_E_INVALID_BLOCK_DEFINITION)

        # #####################################################################
        testresult.addHeader("Power cycle: the written value must not survive it")
        # #####################################################################
        # Free the fixed source port before the camera comes up again.
        SomeipClient.close_clients(client)
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        cs.service_answers(testresult, client, cs.M_GET_CAM_STATUS)

        check_frame_sync_time_ref(testresult, client, DEFAULT_NS,
                                  "default after the power cycle")

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

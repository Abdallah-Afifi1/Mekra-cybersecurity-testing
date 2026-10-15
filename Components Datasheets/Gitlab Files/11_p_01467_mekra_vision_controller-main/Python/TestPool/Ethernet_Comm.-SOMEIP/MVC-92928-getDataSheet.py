#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-92928-getDataSheet.py
# Task : getDataSheet returns the flash parameters at their defined offsets
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 11.09.2026 | Martin Oeder  | initial
#******************************************************************************
#******************************************************************************
# """Deviations from the test steps, so the report states them."""
# The test steps list the payload values but not their format. The layout below
# is the one of the MCP test case INT10111_11467 (steps 06 and 10), which builds
# the same 517 byte payload. It also matches the deviceIdentification parser
# helperModule.read_data_sheet_from_bin_output() of this framework.
# numberOfTemperatures: the test steps demand 0x00000001, the MCP test case
# expects 0x00000002 for its own product. 0x00000001 of the test steps is used.
# intrinsicCamParam at offset 305 is not supported by this camera and has to be
# zero, so it is covered by the zero check and not written by setHostParameters
# as the MCP test case does.
# The SWVer timestamp is set at compile time, so only its format is a verdict,
# as the test steps demand. The value of DutSettings.ExpectedSoftwareInfo is
# written into the report as information.
# Test step 9 "Stop DHCP" has no counterpart: cs.dhcp_lease() serves a single
# lease and returns, there is no server left running that could be stopped.
#
#******************************************************************************
"""
Payload layout of the response, 517 bytes (SOME/IP length 0x0000020D):

    offset   0, 67 bytes : deviceIdentification, production data, nine flash
                           parameters, each one closed by '\\n'
    offset  67, n bytes  : deviceIdentification, SWVer releaseID + '\\n'
    offset  67 + n, 14   : deviceIdentification, SWVer timestamp,
                           "yyyymmdd_hhmm\\0", value set at compile time
    offset 256,  4 bytes : standardVersion, 0x00000001
    offset 305, 100 bytes: intrinsicCamParam, not supported, all zeros
    offset 505,  4 bytes : numberOfTemperatures, 0x00000001
    offset 509,  4 bytes : numbersOfRegionOfInterest, from the parameter set

Everything else is filled with 0x00.

macAddress, partRev and timestamp are raw bytes inside deviceIdentification,
the other parameters are ASCII. That is what makes the nine parameters plus
their separators add up to exactly 67 bytes.
"""
import re

from _automation_wrapper_ import TestEnv
from tools.DutSettings import ExpectedSoftwareInfo
from tools.SOMEIP.someip_client import SomeipClient
from tools.helpFunctions import camera_steps as cs


# #############################################################################
# Configuration
# #############################################################################
TESTCASE_ID = "HIL_Test.MVC-92928"

# --- Power supply ---
SUPPLY_CH = 1                       # PSU channel the camera is connected to
SUPPLY_V = 28.0                     # U_in per test steps 2-3
POWER_OFF_AT_END = True             # test step 8: U_in = 0.0 V

# --- Network ---
USE_DHCP = True                     # test step 1: DHCP server for IP allocation

# --- Response layout ---
RESPONSE_LENGTH = 0x0000020D        # 525 = 8 byte header + 517 byte payload
PAYLOAD_LENGTH = 517

SEPARATOR = 0x0A                    # '\n' after every deviceIdentification field

OFF_PRODUCTION_DATA = 0
LEN_PRODUCTION_DATA = 67
OFF_SW_RELEASE_ID = 67              # length depends on the release ID
LEN_SW_TIMESTAMP = 14               # "yyyymmdd_hhmm\0"
OFF_STANDARD_VERSION = 256
OFF_INTRINSIC_CAM_PARAM = 305
LEN_INTRINSIC_CAM_PARAM = 100
OFF_NUM_TEMPERATURES = 505
OFF_NUM_ROI = 509

STANDARD_VERSION = 0x00000001
NUM_TEMPERATURES = 0x00000001       # per the test steps, the MCP product has 2

SW_TIMESTAMP_PATTERN = r"[0-9]{8}_[0-9]{4}"


# #############################################################################
# Helper functions
# #############################################################################
def u32(data, offset):
    """The 4-byte big endian value at an offset."""
    return int.from_bytes(data[offset:offset + 4], "big")


def check_u32(testresult, data, offset, expected, descr):
    """Verdict on one 4-byte field of the payload."""
    actual = u32(data, offset)
    testresult.append(["%s at offset %d shall be 0x%08X: received 0x%08X"
                       % (descr, offset, expected, actual),
                       "PASSED" if actual == expected else "FAILED"])
    return actual == expected


def check_bytes(testresult, data, offset, expected, descr):
    """Verdict on a byte field of the payload, reported as hex and as text."""
    actual = bytes(data[offset:offset + len(expected)])
    testresult.append(["%s at offset %d shall be %s (%r): received %s (%r)"
                       % (descr, offset, expected.hex(),
                          expected.decode("ascii", errors="replace"),
                          actual.hex(), actual.decode("ascii", errors="replace")),
                       "PASSED" if actual == expected else "FAILED"])
    return actual == expected


def check_separator(testresult, data, offset, descr):
    """Verdict on the '\\n' that closes a deviceIdentification field."""
    actual = data[offset] if offset < len(data) else None
    testresult.append(["%s is closed by 0x%02X at offset %d: received %s"
                       % (descr, SEPARATOR, offset,
                          "0x%02X" % actual if actual is not None else "nothing"),
                       "PASSED" if actual == SEPARATOR else "FAILED"])
    return actual == SEPARATOR


def check_zeros(testresult, data, start, end, descr):
    """Verdict on a region that has to be filled with 0x00."""
    region = data[start:end]
    non_zero = [start + i for i, byte in enumerate(region) if byte != 0]
    testresult.append(["%s (offset %d..%d) is filled with 0x00: %d of %d bytes "
                       "differ%s"
                       % (descr, start, end - 1, len(non_zero), len(region),
                          ", first at offset %d" % non_zero[0] if non_zero else ""),
                       "PASSED" if not non_zero else "FAILED"])
    return not non_zero


def check_sw_timestamp(testresult, data, offset):
    """Verdict on the format of the SWVer timestamp, "yyyymmdd_hhmm\\0".

    The value itself is set at compile time and cannot be an expected value,
    so only the format decides, as the test steps demand.
    """
    stamp = bytes(data[offset:offset + LEN_SW_TIMESTAMP])
    text = stamp[:-1].decode("ascii", errors="replace")
    ok = re.match(SW_TIMESTAMP_PATTERN, text) is not None and stamp[-1] == 0

    testresult.append(["SWVer timestamp at offset %d has the format "
                       "yyyymmdd_hhmm and a terminating 0x00: received %r"
                       % (offset, stamp.decode("ascii", errors="replace")),
                       "PASSED" if ok else "FAILED"])
    testresult.addInfo("SWVer timestamp is set at compile time, its value is "
                       "not a verdict. DutSettings expects %r, received %r"
                       % (ExpectedSoftwareInfo.uc_sw_timestamp, text))
    return ok


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
        # Test steps 1 to 5: DHCP, U_in 0.0 V, U_in 28.0 V, IP address,
        # SD OfferService.
        cs.log_dut_config(testresult)
        client = cs.start_camera(testresult, psu, SUPPLY_CH, SUPPLY_V, USE_DHCP)

        # The first request of a session can be lost, so warm up before measuring.
        cs.service_answers(testresult, client, cs.M_GET_CAM_STATUS)

        # #####################################################################
        testresult.addHeader("Test step 6: getDataSheet is answered")
        # #####################################################################
        rx = cs.send(client, cs.build_request(cs.M_GET_DATA_SHEET, 0x08))
        cs.positive_response(testresult, rx, cs.M_GET_DATA_SHEET, "getDataSheet")

        if rx is None:
            raise RuntimeError("getDataSheet gave no response, the payload "
                               "cannot be checked")

        length = rx.get_length()
        testresult.append(["Length field shall be 0x%08X: received 0x%s"
                           % (RESPONSE_LENGTH, length),
                           "PASSED" if length == "%08x" % RESPONSE_LENGTH
                           else "FAILED"])

        payload = rx.get_payload_as_bytes() or b""
        testresult.addInfo("Received payload: %s"
                           % " ".join("%02x" % byte for byte in payload))
        testresult.append(["Payload shall be %d bytes long: received %d bytes"
                           % (PAYLOAD_LENGTH, len(payload)),
                           "PASSED" if len(payload) == PAYLOAD_LENGTH else "FAILED"])

        if len(payload) < PAYLOAD_LENGTH:
            raise RuntimeError("Payload is shorter than %d bytes, the fields "
                               "cannot be checked" % PAYLOAD_LENGTH)

        # #####################################################################
        testresult.addHeader("Test step 7: deviceIdentification, production data")
        # #####################################################################
        production = cs.production_data()
        sw = cs.sw_config()

        # macAddress, partRev and timestamp are raw bytes, the rest is ASCII.
        fields = [
            ("macAddress",
             bytes.fromhex(production.mac_address.replace(":", ""))),
            ("batchNumber", production.batch_number.encode("ascii")),
            ("partNumber", str(production.part_number).encode("ascii")),
            ("partRev", bytes(production.part_rev_raw)),
            ("serialNumber", production.serial_number.encode("ascii")),
            ("timestamp", bytes(production.timestamp_raw or b"")),
            ("epShort", production.ep_short.encode("ascii")),
            ("hwVer", production.hw_ver.encode("ascii")),
            ("parVer", sw.par_ver.encode("ascii")),
        ]

        # The nine parameters plus their separators have to fill the block. A
        # mismatch means the reference files do not belong to this sample.
        expected_len = sum(len(value) + 1 for _, value in fields)
        testresult.append(["The %d expected flash parameters and their "
                           "separators fill the %d byte production data block: "
                           "%d bytes"
                           % (len(fields), LEN_PRODUCTION_DATA, expected_len),
                           "PASSED" if expected_len == LEN_PRODUCTION_DATA
                           else "FAILED"])

        offset = OFF_PRODUCTION_DATA
        for name, value in fields:
            check_bytes(testresult, payload, offset, value, name)
            offset += len(value)
            check_separator(testresult, payload, offset, name)
            offset += 1

        # #####################################################################
        testresult.addHeader("Test step 7: deviceIdentification, SW version")
        # #####################################################################
        release_id = ExpectedSoftwareInfo.uc_sw_version.encode("ascii")
        check_bytes(testresult, payload, OFF_SW_RELEASE_ID, release_id,
                    "SWVer releaseID")
        check_separator(testresult, payload, OFF_SW_RELEASE_ID + len(release_id),
                        "SWVer releaseID")

        off_sw_timestamp = OFF_SW_RELEASE_ID + len(release_id) + 1
        check_sw_timestamp(testresult, payload, off_sw_timestamp)

        # #####################################################################
        testresult.addHeader("Test step 7: the remaining payload fields")
        # #####################################################################
        check_u32(testresult, payload, OFF_STANDARD_VERSION, STANDARD_VERSION,
                  "standardVersion")
        check_zeros(testresult, payload, OFF_INTRINSIC_CAM_PARAM,
                    OFF_INTRINSIC_CAM_PARAM + LEN_INTRINSIC_CAM_PARAM,
                    "intrinsicCamParam, not supported by this camera")
        check_u32(testresult, payload, OFF_NUM_TEMPERATURES, NUM_TEMPERATURES,
                  "numberOfTemperatures")
        check_u32(testresult, payload, OFF_NUM_ROI, sw.numbers_of_roi,
                  "numbersOfRegionOfInterest")

        # Everything the fields above do not cover has to be 0x00. The gaps are
        # listed without intrinsicCamParam, that one got its own verdict above.
        for start, end in [(off_sw_timestamp + LEN_SW_TIMESTAMP,
                            OFF_STANDARD_VERSION),
                           (OFF_STANDARD_VERSION + 4, OFF_INTRINSIC_CAM_PARAM),
                           (OFF_INTRINSIC_CAM_PARAM + LEN_INTRINSIC_CAM_PARAM,
                            OFF_NUM_TEMPERATURES),
                           (OFF_NUM_ROI + 4, PAYLOAD_LENGTH)]:
            check_zeros(testresult, payload, start, end, "Unused payload")

    except Exception as ex:
        testresult.append(["%s: %s" % (type(ex).__name__, ex), "ERROR"])
        raise

    finally:
        # #####################################################################
        # Cleanup
        # #####################################################################
        SomeipClient.close_clients(client)

        # Test step 8
        if POWER_OFF_AT_END:
            testresult.addSubHeader("U_in = 0.0 V")
            cs.power_off(testresult, psu, SUPPLY_CH)

print("Done.")

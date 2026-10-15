#******************************************************************************
# -*- coding: utf-8 -*-
# File : camera_steps.py
# Task : Reusable test steps for the camera service
#
# Copyright 2026 Mekra Lang GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 03.08.2026 | Ehu Li   | initial  
# 1.1.0  | 05.08.2026 | Ehu Li   | added rtp_port(); rtp_packet()
#                                  stream_active() and set_control()
# 1.2.0  | 10.08.2026 |  Ehu Li   | added serializer_temperature() via getDataBlock 0x0251
# 1.3.0  | 10.09.2026 | Martin Oeder  | added the method IDs setDataBlock 0x0250
#                                  and setCamID 0x0409, and the block ID
#                                  frameSyncTimeRef
#******************************************************************************
"""
Reusable test steps for the camera service: each one performs a bench or SOME/IP
action and writes its verdict into the TTK test result.

"""
import os
import socket
from binascii import hexlify
from time import sleep, perf_counter

from tools.SOMEIP.someip_packet import SomeipPacket
from tools.SOMEIP.someip_client import SomeipClient
from tools.ServiceDiscovery.servicediscovery import ServiceDiscovery
from tools.dhcp.dhcp_server import DHCPServer
from tools.dut_config_loader import read_production_data, read_sw_config
from tools.helpFunctions import helperModule


# The SW configuration and production data flashed on the DUT.
DUT_PAR_FILE = "PAR_10C1.py"
DUT_PRODUCTION_FILE = "Volvo_Standard_1Gbit_SN00012803.py"

REFERENCE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                 "reference_value"))

SERVICE_ID = 0x433F
REQUEST_ID = 0x12345678

# Address of the test PC, not part of the DUT configuration.
CLIENT_IP = "192.168.120.1"
DHCP_SERVER_IP = [0xC0, 0xA8, 0x78, 0x01]
DHCP_CLIENT_IP = [0xC0, 0xA8, 0x78, 0x0A]
INFINITE_LEASE = [51, 4, 0xFF, 0xFF, 0xFF, 0xFF]

# Fallbacks, used only when the parameter set cannot be read.
SD_IP = "239.120.1.1"
SD_PORT = 30490
SERVICE_PORT = 30501
SERVER_IP = "192.168.120.10"

M_GET_DATA_SHEET = 0x0001
M_GET_CAM_STATUS = 0x0002
M_GET_CAM_IDENTIFICATION = 0x0010
M_SET_CAM_EXCLUSIVE = 0x0011
M_ERASE_CAM_EXCLUSIVE = 0x0019
M_SUBSCRIBE_ROI_VIDEO = 0x0131
M_UNSUBSCRIBE_ROI_VIDEO = 0x0132
M_SET_CAM_CONTROL = 0x0201
M_GET_CAM_CONTROL = 0x0203
M_SET_DATA_BLOCK = 0x0250
M_GET_DATA_BLOCK = 0x0251
M_SET_CAM_ID = 0x0409

CTRL_IDX_HEATER = 0x09
CTRL_IDX_SHUTTER = 0x50
MODE_MANUAL = 0x02
MODE_MANUAL_MODIFIED = 0x03
MODE_AUTOMATIC = 0x04
SUPPORTED_MODES = 0x07

# Both sensors report a signed 16-bit raw value with this scale.
TEMP_SCALE = 0.0078125                      # 1/128 degC per LSB
TEMP_RANGE_C = (-60.0, 150.0)               # a value outside this did not decode

# set/getDataBlock selectors, deviceID and blockID
DEVICE_CAMERA_EEPROM = 0x0000
DEVICE_SOW2_RUNTIME = 0x0001
DEVICE_SERIALIZER = 0x0002
BLOCK_SERIALIZER_TEMP = 0x0000          # of DEVICE_SERIALIZER
BLOCK_FRAME_SYNC_TIME_REF = 0x0000      # of DEVICE_SOW2_RUNTIME

LOG_TX = False                      # print every outgoing request, set from a test

STARTUP_SETTLE_S = 2.0              # DUT startup time after the OfferService


_sw_cache = {}
_pd_cache = {}


def sw_config(par_file=DUT_PAR_FILE):
    """SW configuration of the DUT, read once per parameter set."""
    if par_file not in _sw_cache:
        _sw_cache[par_file] = read_sw_config(
            os.path.join(REFERENCE_DIR, "SW_config", par_file))
    return _sw_cache[par_file]


def production_data(prod_file=DUT_PRODUCTION_FILE):
    """Production data of the DUT, read once per file."""
    if prod_file not in _pd_cache:
        _pd_cache[prod_file] = read_production_data(
            os.path.join(REFERENCE_DIR, "production_data", prod_file))
    return _pd_cache[prod_file]


try:
    _SW = sw_config()
    SD_IP = _SW.someip_sd_dst_ip
    SD_PORT = _SW.someip_sd_dst_port
    SERVICE_PORT = _SW.camera_service_port
except Exception as _ex:                # keep the fallbacks and report on first use
    _SW = None
    _SW_ERROR = _ex


def log_dut_config(testresult):
    """Report which parameter set and which sample the values come from."""
    if _SW is None:
        testresult.addInfo("SW configuration %s not readable (%s), using %s:%d and "
                           "SD %s:%d" % (DUT_PAR_FILE, _SW_ERROR, SERVER_IP,
                                         SERVICE_PORT, SD_IP, SD_PORT))
        return None

    testresult.addInfo("SW config %s (%s): service port %d, SD %s:%d, %d ROIs, "
                       "Tauto %.1f/%.1f degC, Tprotection %.1f/%.1f degC"
                       % (_SW.par_ver, _SW.device_type, _SW.camera_service_port,
                          _SW.someip_sd_dst_ip, _SW.someip_sd_dst_port,
                          _SW.numbers_of_roi, _SW.t_imager_auto_on_c,
                          _SW.t_imager_auto_off_c, _SW.t_imager_protection_on_c,
                          _SW.t_imager_protection_off_c))
    try:
        pd = production_data()
        testresult.addInfo("Production data %s: MAC %s, serial %s, hwVer %s"
                           % (DUT_PRODUCTION_FILE, pd.mac_address, pd.serial_number,
                              pd.hw_ver))
    except Exception as ex:
        testresult.addInfo("Production data not readable (%s)" % ex)
    return _SW


# #############################################################################
# Requests
# #############################################################################
def build_request(method_id, length, payload=None, service_id=SERVICE_ID,
                  request_id=REQUEST_ID):
    """Build a SOME/IP request packet with the global header constants."""
    return SomeipPacket(service_id=service_id,
                        method_id=method_id,
                        length=length,
                        request_id=request_id,
                        protocol_version=0x01,
                        interface_version=0x01,
                        message_type=0x00,
                        return_code=0x00,
                        payload=payload)


def request_bytes(packet):
    """The datagram of a request as one hex string, for logs and comparisons."""
    return hexlify(packet.packet()).decode("ascii")


def log_request(testresult, packet, descr=""):
    """Write the bytes of an outgoing request into the test report."""
    testresult.addInfo("TX %s%s | %s" % (descr, " " if descr else "",
                                         request_bytes(packet)))
    testresult.addInfo("TX fields: %s"
                       % " ".join(SomeipPacket.get_packet_stream(packet)))


def _log_tx(packet):
    """Print an outgoing request to the console while LOG_TX is on."""
    if LOG_TX:
        print("TX %s | %s" % (request_bytes(packet),
                              " ".join(SomeipPacket.get_packet_stream(packet))))


def send(client, packet, attempts=3):
    """Send a packet until a response arrives and return it, None if none did.

    The first request of a session can be lost while the address resolution
    settles, hence the retries.
    """
    _log_tx(packet)
    for _ in range(attempts):
        client.send_packet(packet, client.serverIP, client.destinationPort)
        if client.someip_rx_packet is not None:
            return client.someip_rx_packet
    return None


def send_wait(client, packet, wait_s=5.0, attempts=2):
    """Send a packet and poll for the response for up to wait_s per attempt.

    send_packet() reads the socket after a fixed short delay, which is too early
    for a request whose handling takes longer, such as starting a video stream.
    """
    _log_tx(packet)
    for _ in range(attempts):
        client.send_packet_dont_wait_for_response(packet, client.serverIP,
                                                 int(client.destinationPort))
        t_start = perf_counter()
        while perf_counter() - t_start < wait_s:
            response = client.receive_packet()
            if response is not None:
                return response
    return None


def send_timed(client, packet, attempts=3):
    """Send a packet and return (response, delay in ms).

    send_packet() sleeps before it reads the socket, which hides response times
    below that sleep, so the request goes out unbuffered here.
    """
    _log_tx(packet)
    for _ in range(attempts):
        t_start = perf_counter()
        client.send_packet_dont_wait_for_response(packet, client.serverIP,
                                                 int(client.destinationPort))
        response = client.receive_packet()
        delay_ms = (perf_counter() - t_start) * 1000.0
        if response is not None:
            return response, delay_ms
    return None, None


def positive_response(testresult, rx, method_id, descr):
    """Verdict on a positive response: message type 0x80 and return code E_OK."""
    if rx is None:
        testresult.append(["%s: no response from camera" % descr, "FAILED"])
        return False

    method = rx.get_method_id()
    msg_type = rx.get_message_type()
    ret_code = rx.get_return_code()
    passed = (method == "%04x" % method_id and msg_type == "80" and ret_code == "00")

    testresult.append([
        "%s: method 0x%s, message type 0x%s, return code 0x%s (%s)"
        % (descr, method, msg_type, ret_code,
           helperModule.get_human_readable_return_code(ret_code)),
        "PASSED" if passed else "FAILED"])
    return passed


def negative_response(testresult, rx, method_id, expected_rc, descr):
    """Verdict on a negative response: message type 0x81 and the expected code."""
    if rx is None:
        testresult.append(["%s: no response from camera" % descr, "FAILED"])
        return False

    method = rx.get_method_id()
    msg_type = rx.get_message_type()
    ret_code = rx.get_return_code()
    passed = (method == "%04x" % method_id
              and msg_type == "81"
              and ret_code == "%02x" % expected_rc)

    testresult.append([
        "%s: method 0x%s, message type 0x%s, return code 0x%s (%s), expected 0x81 / "
        "0x%02X" % (descr, method, msg_type, ret_code,
                    helperModule.get_human_readable_return_code(ret_code), expected_rc),
        "PASSED" if passed else "FAILED"])
    return passed


# #############################################################################
# Power supply
# #############################################################################
def power_off(testresult, psu, channel):
    """Disable one supply channel."""
    psu.channelOutputEnable(channel, False)
    testresult.addInfo("Channel %d disabled, DUT powered down" % channel)


def power_on(testresult, psu, channel, voltage, tol=0.1, settle_s=1.0):
    """Enable one supply channel at the given voltage and verify it."""
    getattr(psu, "voltage_preset_ch%d" % channel).set(voltage)
    psu.channelOutputEnable(channel, True)
    psu.masterOutputEnable(True)
    sleep(settle_s)

    testresult.addCheckAbsTol(getattr(psu, "voltage_ch%d" % channel), voltage,
                              abs_tol=tol,
                              descr="Supply voltage on channel %d" % channel)


def power_cycle(testresult, psu, channel, voltage, off_time_s=2.0, tol=0.1):
    """Power the DUT down and up again, so a test starts from a defined state."""
    power_off(testresult, psu, channel)
    sleep(off_time_s)
    power_on(testresult, psu, channel, voltage, tol=tol)


# #############################################################################
# Address allocation and OPERATIONAL state
# #############################################################################
def dhcp_lease(testresult, client_ip=None, server_ip=None, timeout_s=60,
               renew_ip=True):
    """Serve one DHCP lease to the booting DUT."""
    client_ip = client_ip or DHCP_CLIENT_IP
    server_ip = server_ip or DHCP_SERVER_IP

    server = DHCPServer(67, server_ip, 68, client_ip, INFINITE_LEASE, 1024,
                        renew_ip=renew_ip, wait_for_discovery=True)
    acknowledged = server.serve_one_lease(timeout_s)

    lease = ".".join(str(b) for b in client_ip)
    if acknowledged:
        testresult.append(["DHCP lease %s acknowledged to the DUT" % lease, "PASSED"])
    else:
        testresult.append(["No DHCP lease served within %d s, the DUT sent no Discover"
                           % timeout_s, "FAILED"])
    return acknowledged


def operational(testresult, timeout_s=60, poll_s=2, sd_ip=SD_IP, sd_port=SD_PORT):
    """Wait for the OfferService and return the announced (ip, port).

    Returns (None, None) when the DUT did not announce itself, so the caller can
    fall back to a configured endpoint.
    """
    sd = ServiceDiscovery(sd_ip, sd_port)
    try:
        sd.connect()
        t_start = perf_counter()

        while perf_counter() - t_start < timeout_s:
            msg = sd.get_sd_message_noevent(timeout=poll_s)
            if msg is None:
                continue

            testresult.append(["SD OfferService received after %.1f s -> DUT has an IP "
                               "address and is in OPERATIONAL state"
                               % (perf_counter() - t_start), "PASSED"])
            try:
                config = msg.configuration()
            except Exception as ex:
                config = "not decodable (%s)" % ex
            testresult.addInfo("OfferService announces service 0x%04X at %s:%d | "
                               "config %s" % (msg.serviceID(), msg.address(),
                                              msg.port(), config))
            return msg.address(), msg.port()

        testresult.append(["No SD OfferService within %d s -> DUT did not reach "
                           "OPERATIONAL state" % timeout_s, "FAILED"])
        return None, None
    finally:
        sd.disconnect()


def log_endpoint(testresult, client):
    """Log which endpoint the requests actually use."""
    testresult.addInfo("SOME/IP endpoint: local %s -> target %s:%s"
                       % (client.hostSocket.getsockname(), client.serverIP,
                          client.destinationPort))


def connect(testresult, timeout_s=60, client_ip=CLIENT_IP):
    """Wait for the OfferService and return a client on the announced endpoint.

    Falls back to the endpoint from the DUT's SW configuration when nothing is
    announced.
    """
    testresult.addSubHeader("DUT reaches OPERATIONAL state")
    server_ip, server_port = operational(testresult, timeout_s)

    if server_ip is None:
        server_ip, server_port = SERVER_IP, SERVICE_PORT
        testresult.addInfo("No endpoint announced, using %s:%d from the SW "
                           "configuration" % (server_ip, server_port))

    client = SomeipClient(client_ip=client_ip,
                          server_ip=server_ip,
                          client_source_port="0",
                          client_destination_port=server_port)
    log_endpoint(testresult, client)
    return client


def start_camera(testresult, psu, channel, voltage, use_dhcp=True, off_time_s=2.0,
                 timeout_s=60):
    """Power-cycle the DUT, serve it an address and return a connected client.

    The DUT stops answering when a request arrives before its video pipeline is
    up, so STARTUP_SETTLE_S is waited out after the OfferService.
    """
    testresult.addSubHeader("U_in = 0.0 V")
    power_off(testresult, psu, channel)
    sleep(off_time_s)

    testresult.addSubHeader("U_in = %.1f V" % voltage)
    power_on(testresult, psu, channel, voltage)

    if use_dhcp:
        testresult.addSubHeader("DHCP address allocation")
        dhcp_lease(testresult)

    client = connect(testresult, timeout_s)

    testresult.addInfo("Waiting %.1f s for the DUT to finish its startup"
                       % STARTUP_SETTLE_S)
    sleep(STARTUP_SETTLE_S)

    return client


def service_answers(testresult, client, method_id=M_GET_CAM_IDENTIFICATION,
                    timeout_s=20):
    """Check that the camera answers a method that is known to be implemented.

    Separates a transport problem from a problem with one single method.
    """
    t_start = perf_counter()
    while True:
        rx = send(client, build_request(method_id, 0x08))
        elapsed = perf_counter() - t_start

        if rx is not None:
            testresult.append(["Camera answers method 0x%04X after %.1f s with message "
                               "type 0x%s, return code 0x%s -> SOME/IP transport works"
                               % (method_id, elapsed, rx.get_message_type(),
                                  rx.get_return_code()), "PASSED"])
            return True

        if elapsed >= timeout_s:
            testresult.append(["Camera does not answer method 0x%04X within %d s -> no "
                               "request reaches %s:%s at all"
                               % (method_id, timeout_s, client.serverIP,
                                  client.destinationPort), "FAILED"])
            return False


# #############################################################################
# Exclusive lock
# #############################################################################
def lock(testresult, client, ttl_s=1):
    """setCamExclusive: take the camera lock, required before writing a control."""
    rx = send(client, build_request(M_SET_CAM_EXCLUSIVE, 0x0C,
                                    ttl_s.to_bytes(4, "big")))
    return positive_response(testresult, rx, M_SET_CAM_EXCLUSIVE,
                             "setCamExclusive (lock camera for %d s)" % ttl_s)


def unlock(testresult, client):
    """eraseCamExclusive: release the lock."""
    rx = send(client, build_request(M_ERASE_CAM_EXCLUSIVE, 0x08))
    return positive_response(testresult, rx, M_ERASE_CAM_EXCLUSIVE,
                             "eraseCamExclusive (release the lock)")


# #############################################################################
# Video stream
# #############################################################################
def subscribe_roi(testresult, client, roi, wait_s=5.0):
    """subscribeROIVideo: video streaming ON.

    roi is the full 4-byte payload: index in bits 7..0, flip/mirror/stream and
    the T3 fields in the upper bits.
    """
    rx = send_wait(client, build_request(M_SUBSCRIBE_ROI_VIDEO, 0x0C,
                                        roi.to_bytes(4, "big")), wait_s)
    return positive_response(testresult, rx, M_SUBSCRIBE_ROI_VIDEO,
                             "subscribeROIVideo (0x%08X, ROI %d)" % (roi, roi & 0xFF))


def unsubscribe_roi(testresult, client, roi, wait_s=5.0):
    """unSubscribeROIVideo: video streaming OFF."""
    rx = send_wait(client, build_request(M_UNSUBSCRIBE_ROI_VIDEO, 0x0C,
                                        roi.to_bytes(4, "big")), wait_s)
    return positive_response(testresult, rx, M_UNSUBSCRIBE_ROI_VIDEO,
                             "unSubscribeROIVideo (0x%08X, ROI %d)" % (roi, roi & 0xFF))


def rtp_port(stream=1, server_ip=SERVER_IP):
    """The UDP port an RTP stream arrives on.

    The DUT adds the last octet of its own address to the base port of the
    parameter set.
    """
    sw = sw_config()
    base = sw.rtp_dst_port1 if stream == 1 else sw.rtp_dst_port2
    return base + int(server_ip.split(".")[-1])


def rtp_packet(port, timeout_s=2.0, client_ip=CLIENT_IP):
    """Wait for one RTP packet on the port, return (received, reason).

    received is None when the port cannot be opened, which is not the same as an
    inactive stream.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout_s)

    try:
        sock.bind((client_ip, port))
    except OSError as ex:
        sock.close()
        return None, "port %d cannot be opened (%s)" % (port, ex)

    try:
        data, addr = sock.recvfrom(2048)
        return True, "%d bytes from %s:%d" % (len(data), addr[0], addr[1])
    except socket.timeout:
        return False, "no packet within %.1f s" % timeout_s
    finally:
        sock.close()


def stream_active(testresult, expect_active, descr, stream=1, timeout_s=2.0):
    """Verdict on whether RTP packets arrive on the stream's port."""
    port = rtp_port(stream)
    received, reason = rtp_packet(port, timeout_s)

    if received is None:
        testresult.append(["RTP stream %s on port %d: %s" % (descr, port, reason),
                           "FAILED"])
        return False

    testresult.append(["RTP stream %s on port %d: %s" % (descr, port, reason),
                       "PASSED" if received == expect_active else "FAILED"])
    return received == expect_active


# #############################################################################
# Camera controls: heater 0x09, shutter 0x50, ...
# #############################################################################
def set_control(testresult, client, control_index, mode, value, descr,
                supported_modes=SUPPORTED_MODES, settle_s=0.0, error_rc=None):
    """setCamControl on one control index. Requires an active lock.

    error_rc turns the expectation around, the response then has to carry that
    return code instead of being positive.
    """
    payload = bytes([control_index, supported_modes, mode]) + value.to_bytes(2, "big")
    rx = send(client, build_request(M_SET_CAM_CONTROL, 0x0D, payload))

    if error_rc is None:
        passed = positive_response(testresult, rx, M_SET_CAM_CONTROL,
                                   "setCamControl (%s)" % descr)
    else:
        passed = negative_response(testresult, rx, M_SET_CAM_CONTROL, error_rc,
                                   "setCamControl (%s)" % descr)
    if settle_s:
        sleep(settle_s)
    return passed


def check_control(testresult, client, control_index, exp_mode, exp_value, descr,
                  supported_modes=SUPPORTED_MODES):
    """getCamControl on one control index and compare the returned control block."""
    rx = send(client, build_request(M_GET_CAM_CONTROL, 0x09,
                                    bytes([control_index])))
    if not positive_response(testresult, rx, M_GET_CAM_CONTROL,
                             "getCamControl (read control 0x%02X)" % control_index):
        return False

    expected = "%02x%02x%04x" % (supported_modes, exp_mode, exp_value)
    actual = rx.get_payload()
    passed = (actual == expected)

    testresult.append(["Control 0x%02X shall be %s: payload 0x%s (expected 0x%s)"
                       % (control_index, descr, actual, expected),
                       "PASSED" if passed else "FAILED"])
    return passed


# #############################################################################
# Imager temperature
# #############################################################################
def parse_temperature(hex_value):
    """Convert a raw temperature field to degC.

    The DUT reports a signed 16-bit value, TEMP_SCALE degC per LSB.
    """
    raw = int(hex_value, 16)
    if raw & (1 << 15):
        raw -= (1 << 16)
    return raw * TEMP_SCALE


def imager_temperature(client):
    """getCamStatus: return (temperature in degC, reason).

    The temperature is None when it cannot be used, the reason then says why.
    Writes no verdict, so it can be polled.
    """
    rx = send(client, build_request(M_GET_CAM_STATUS, 0x08))
    if rx is None:
        return None, "no response from camera"

    if rx.get_message_type() != "80" or rx.get_return_code() != "00":
        return None, ("message type 0x%s, return code 0x%s (%s)"
                      % (rx.get_message_type(), rx.get_return_code(),
                         helperModule.get_human_readable_return_code(
                             rx.get_return_code())))

    field = rx.get_payload()[-4:]
    if int(field, 16) == 0:
        return None, "temperature field is 0x0000, no video stream active"

    return parse_temperature(field), "payload 0x%s" % rx.get_payload()


def data_block(client, device_id, block_id):
    """getDataBlock: return (block content as hex string, reason).

    The response carries the block size as uint32 first and the content after it.
    """
    request = device_id.to_bytes(2, "big") + block_id.to_bytes(2, "big")
    rx = send(client, build_request(M_GET_DATA_BLOCK, 0x0C, request))
    if rx is None:
        return None, "no response from camera"

    if rx.get_message_type() != "80" or rx.get_return_code() != "00":
        return None, ("message type 0x%s, return code 0x%s (%s)"
                      % (rx.get_message_type(), rx.get_return_code(),
                         helperModule.get_human_readable_return_code(
                             rx.get_return_code())))

    answer = rx.get_payload()
    size = int(answer[:8], 16)
    content = answer[8:]

    if len(content) != size * 2:
        return None, ("block size %d does not match %d content bytes (payload 0x%s)"
                      % (size, len(content) // 2, answer))
    return content, "block 0x%04X/0x%04X, %d bytes, payload 0x%s" % (device_id,
                                                                    block_id, size,
                                                                    answer)


def serializer_temperature(client, device_id=DEVICE_SERIALIZER,
                           block_id=BLOCK_SERIALIZER_TEMP):
    """getDataBlock: return (serializer temperature in degC, reason)."""
    content, reason = data_block(client, device_id, block_id)
    if content is None:
        return None, reason

    value = parse_temperature(content)
    reason = "%s, %.2f degC" % (reason, value)

    low, high = TEMP_RANGE_C
    if not low <= value <= high:
        return None, ("%.2f degC is outside %.0f..%.0f degC (%s)"
                      % (value, low, high, reason))
    return value, reason


# #############################################################################
# Climate chamber
# #############################################################################
def chamber_temperature(testresult, chamber, target, tolerance=1.0,
                        timeout_s=90 * 60, poll_s=30):
    """Drive the chamber to target and write the verdict."""
    if chamber is None:
        testresult.addInfo("Climate chamber not available, %.1f degC not set" % target)
        return False

    try:
        elapsed, ambient = chamber.reachTemperature(target,
                                                    target_accuracy=tolerance,
                                                    timeout_s=timeout_s,
                                                    poll_interval_s=poll_s)
    except TimeoutError as ex:
        testresult.append(["Tambient did not reach %.1f degC: %s" % (target, ex),
                           "FAILED"])
        return False

    testresult.append(["Tambient reached %.1f degC (target %.1f +/- %.1f degC) after "
                       "%.0f s" % (ambient, target, tolerance, elapsed), "PASSED"])
    return True


def set_chamber_temperature(testresult, chamber, target):
    """Set the chamber setpoint once, without waiting for it to be reached.

    Unlike cs.chamber_temperature(), this does not poll the chamber and
    return as soon as the setpoint is reached - the caller waits out the
    fixed "Waiting time" itself with a separate sleep().
    """
    if chamber is None:
        testresult.addInfo("Climate chamber not available, %.1f degC not set" % target)
        return

    chamber.manualMode(True)
    chamber.temperature_setpoint.set(target)
    testresult.addInfo("Chamber setpoint set to %.1f degC" % target)
    

def release_chamber(chamber):
    """Clear manual mode and close the connection."""
    if chamber is not None:
        chamber.manualMode(False)
        chamber.close()

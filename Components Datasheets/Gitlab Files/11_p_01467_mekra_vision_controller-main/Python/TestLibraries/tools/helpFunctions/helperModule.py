import sys
import importlib.util
import pathlib

import numpy as np
import serial

from tools.dhcp.dhcp_server import DHCPServer
from tools.helpFunctions import comFinder
from tools.SOMEIP import someip_client
from tools.SOMEIP import someip_packet
from tools.ServiceDiscovery.servicediscovery import ServiceDiscovery




def evaluate_response(param_testreport, send_packet, expected_packet, actual_packet, description, info=""):

    someippacket = someip_packet.SomeipPacket
    if expected_packet is not None:
        payload_expected = expected_packet.get_payload()

        if payload_expected == "Ignored":
            if expected_packet.compare_packet_ignore_payload(actual_packet) is True:
                print("   --> PASSED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Passed",
                                              "Payload ignored for packet compare! " + info)
            else:
                print("--> FAILED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Failed",
                                              "Payload ignored for packet compare! " + info)
        else:
            if expected_packet == actual_packet:
                print("   --> PASSED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Passed",
                                              info)
            else:
                print("--> FAILED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Failed",
                                              info)
    else:
        if expected_packet == actual_packet:
            print("   --> PASSED")
            param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                          someippacket.get_formatted_packet(expected_packet),
                                          description,
                                          someippacket.get_formatted_packet(actual_packet),
                                          "Passed",
                                          info)
        else:
            print("--> FAILED")
            param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                          someippacket.get_formatted_packet(expected_packet),
                                          description,
                                          someippacket.get_formatted_packet(actual_packet),
                                          "Failed",
                                          info)


def evaluate_measurements(param_testreport, send, expected_value, actual_value, unit, description, info=""):
    expected = parse_range(expected_value)
    lower_threshold = expected[0] - expected[2]
    upper_threshold = expected[0] + expected[1]

    if lower_threshold <= float(actual_value) <= upper_threshold:
        print("   --> PASSED")
        param_testreport.add_teststep(send,
                                      str(lower_threshold) + str(unit) + " .. " + str(upper_threshold) + str(unit),
                                      description,
                                      str(float(actual_value)) + str(unit),
                                      "Passed",
                                      info)
    else:
        print("--> FAILED")
        param_testreport.add_teststep(send,
                                      str(lower_threshold) + str(unit) + " .. " + str(upper_threshold) + str(unit),
                                      description,
                                      str(float(actual_value)) + str(unit),
                                      "Failed",
                                      info)


def evaluate_string(param_testreport, send, expected_value, actual_value, description, info=""):
    if expected_value == actual_value:
        print("   --> PASSED")
        param_testreport.add_teststep(send,
                                      expected_value,
                                      description,
                                      actual_value,
                                      "Passed",
                                      info)
    else:
        print("--> FAILED")
        param_testreport.add_teststep(send,
                                      expected_value,
                                      description,
                                      actual_value,
                                      "Failed",
                                      info)


def evaluate_payload(param_testreport, send, expected_values, actual_value, description, info=""):
    for exp_val in expected_values:
        if exp_val == actual_value:
            print("   --> PASSED")
            param_testreport.add_teststep(send,
                                          expected_values,
                                          description,
                                          actual_value,
                                          "Passed",
                                          info)
            return

    print("--> FAILED")
    param_testreport.add_teststep(send,
                                  expected_values,
                                  description,
                                  actual_value,
                                  "Failed",
                                  info)


def parse_range(value_and_range):
    # 5p2m1 ==> 5 plus 2 minus 1 ==> range 4 to 7
    # returns: [value, plus, minus]

    value = value_and_range.split("p")
    try:
        plus_minus = value[1].split("m")
        return [round(float(value[0]), 3), round(float(plus_minus[0]), 3), round(float(plus_minus[1]), 3)]
    except IndexError:
        return [round(float(value[0]), 3), 0.0, 0.0]


def get_human_readable_return_code(return_code):

    if return_code == "00" or return_code == 0:
        response = "E_OK"
    elif return_code == "01" or return_code == 1:
        response = "E_NOT_OK"
    elif return_code == "02" or return_code == 2:
        response = "E_UNKNOWN_SERVICE"
    elif return_code == "03" or return_code == 3:
        response = "E_UNKNOWN_METHOD"
    elif return_code == "04" or return_code == 4:
        response = "E_NOT_READY"
    elif return_code == "05" or return_code == 5:
        response = "E_NOT_REACHABLE"
    elif return_code == "06" or return_code == 6:
        response = "E_TIMEOUT"
    elif return_code == "07" or return_code == 7:
        response = "E_WRONG_PROTOCOL_VERSION"
    elif return_code == "08" or return_code == 8:
        response = "E_WRONG_INTERFACE_VERSION"
    elif return_code == "09" or return_code == 9:
        response = "E_MALFORMED_MESSAGE"
    elif return_code == "20" or return_code == 32:
        response = "E_LOCKED_BY_FOREIGN_INSTANCE"
    elif return_code == "21" or return_code == 33:
        response = "E_LOCK_EXPIRED"
    elif return_code == "22" or return_code == 34:
        response = "E_NOT_LOCKED"
    elif return_code == "24" or return_code == 36:
        response = "E_INVALID_PS_ENTRY"
    elif return_code == "25" or return_code == 37:
        response = "E_INVALID_PS_OPERATION"
    elif return_code == "26" or return_code == 38:
        response = "E_INVALID_PS_DATA"
    elif return_code == "27" or return_code == 39:
        response = "E_NO_MORE_SPACE"
    elif return_code == "30" or return_code == 48:
        response = "E_INVALID_ROI_INDEX"
    elif return_code == "31" or return_code == 49:
        response = "E_INVALID_ROI_NUMBER"
    elif return_code == "32" or return_code == 50:
        response = "E_INVALID_VIDEO_FORMAT"
    elif return_code == "33" or return_code == 51:
        response = "E_INVALID_HISTOGRAM_FORMAT"
    elif return_code == "35" or return_code == 53:
        response = "E_INVALID_CONTROL_INDEX"
    elif return_code == "36" or return_code == 54:
        response = "E_INVALID_CONTROL_MODE"
    elif return_code == "37" or return_code == 55:
        response = "E_INVALID_CONTROL_VALUE"
    elif return_code == "38" or return_code == 56:
        response = "E_INVALID_REGISTER_ADDRESS"
    elif return_code == "39" or return_code == 57:
        response = "E_INVALID_REGISTER_VALUE"
    elif return_code == "3A" or return_code == 58:
        response = "E_INVALID_REGISTER_OPERATION"
    else:
        response = ""

    return response


def get_human_readable_method_id(method_id):

    if method_id == "0001" or method_id == 1:
        response = "getDataSheet"
    elif method_id == "0002" or method_id == 2:
        response = "getCamStatus"
    elif method_id == "0003" or method_id == 3:
        response = "setCamMode"
    elif method_id == "0011" or method_id == 17:
        response = "setCamExclusive"
    elif method_id == "0019" or method_id == 25:
        response = "eraseCamExclusive"
    elif method_id == "0022" or method_id == 34:
        response = "setHostParameters"
    elif method_id == "0024" or method_id == 36:
        response = "getHostParameters"
    elif method_id == "0029" or method_id == 41:
        response = "eraseHostParameters"
    elif method_id == "0101" or method_id == 257:
        response = "setRegionOfInterest"
    elif method_id == "0102" or method_id == 258:
        response = "setRegionsOfInterest"
    elif method_id == "0103" or method_id == 259:
        response = "getRegionOfInterest"
    elif method_id == "0104" or method_id == 260:
        response = "getRegionsOfInterest"
    elif method_id == "0109" or method_id == 265:
        response = "eraseRegionOfInterest"
    elif method_id == "0111" or method_id == 273:
        response = "setVideoFormat"
    elif method_id == "0113" or method_id == 275:
        response = "getVideoFormat"
    elif method_id == "0119" or method_id == 281:
        response = "eraseVideoFormat"
    elif method_id == "0121" or method_id == 289:
        response = "setHistogrammFormat"
    elif method_id == "0123" or method_id == 291:
        response = "getHistogrammFormat"
    elif method_id == "0129" or method_id == 297:
        response = "eraseHistogrammFormat"
    elif method_id == "0131" or method_id == 305:
        response = "subscribeROIVideo"
    elif method_id == "0132" or method_id == 306:
        response = "unSubscribeROIVideo"
    elif method_id == "0133" or method_id == 307:
        response = "subscribeROIHistogram"
    elif method_id == "0134" or method_id == 308:
        response = "unSubscribeROIHistogram"
    elif method_id == "0201" or method_id == 513:
        response = "setCamControl"
    elif method_id == "0202" or method_id == 514:
        response = "setCamControls"
    elif method_id == "0203" or method_id == 515:
        response = "getCamControl"
    elif method_id == "0204" or method_id == 516:
        response = "getCamControls"
    elif method_id == "0301" or method_id == 769:
        response = "setCamRegister"
    elif method_id == "0302" or method_id == 770:
        response = "setCamRegisters"
    elif method_id == "0303" or method_id == 771:
        response = "getCamRegister"
    elif method_id == "0304" or method_id == 772:
        response = "getCamRegisters"
    elif method_id == "0305" or method_id == 773:
        response = "setUsedRegisterSet"
    else:
        response = ""

    return response


def evaluate_camstatus(actual_packet):

    someippacket = someip_packet.SomeipPacket

    actpac_payload = someippacket.get_payload(actual_packet)
    actpac_methodid = someippacket.get_method_id(actual_packet)

    if str(actpac_methodid) == "0002":  # getCamStatus
        imager_temperature_hex = actpac_payload[-4:]
        power_status_hex = actpac_payload[-6:-4]
        lockedby_address_hex = actpac_payload[0:8]
        scale = 16  # equals to hexadecimal

        # calculate imager temperature
        imager_temperature_int = parse_imager_temp(imager_temperature_hex)

        # prepare power status
        power_status_bin = bin(int(power_status_hex, scale))[2:].zfill(8)
        power_status_input_voltage = parse_power_status_value(power_status_bin[0:2])
        power_status_internal_voltage = parse_power_status_value(power_status_bin[2:4])
        power_status_watchdog = parse_power_status_value(power_status_bin[4:6])
        power_status_luma = parse_power_status_value(power_status_bin[6:8])

        # prepare ip address
        lockedby_address_bin = bin(int(lockedby_address_hex, scale))[2:].zfill(32)
        lockedby_address_str = parse_ip_address(lockedby_address_bin)

        cam_status_list = [imager_temperature_int,
                           power_status_input_voltage,
                           power_status_internal_voltage,
                           power_status_watchdog,
                           power_status_luma,
                           lockedby_address_str]

        return cam_status_list
    else:
        return [""]


def parse_power_status_value(power_status_val):
    if str(power_status_val) == "00":
        return "E_OK"
    elif str(power_status_val) == "01":
        return "E_LOW"
    elif str(power_status_val) == "10":
        return "E_HIGH"
    elif str(power_status_val) == "11":
        return "E_PERM"
    else:
        return "power status invalid"


def parse_ip_address(ip_address_bin):
    ip_part01 = int(ip_address_bin[0:8], 2)
    ip_part02 = int(ip_address_bin[8:16], 2)
    ip_part03 = int(ip_address_bin[16:24], 2)
    ip_part04 = int(ip_address_bin[24:], 2)

    return str(ip_part01) + "." + str(ip_part02) + "." + str(ip_part03) + "." + str(ip_part04)


def parse_imager_temp(imager_hex_temp):
    val = int(imager_hex_temp, 16)
    if (val & (1 << 15)) != 0:
        val = val - (1 << 16)

    return val * 0.0078125


def parse_ntc_adc_value(adc_hex_val):
    u_meas = float(int(adc_hex_val, 16)) / 1023 * 3.3
    r_ntc = (u_meas * 15000) / (3.3 - u_meas)
    ntc_temp = round(((298.15 * 3455) / (3455 + np.log(r_ntc / 10000) * 298.15) - 273), 1)

    return ntc_temp


def parse_data_sheet(data_sh):
    data_sheet = dict()
    dev_id = data_sh[0:512]
    # print(dev_id)

    data_sheet['dev_id_mac_address'] = dev_id[0:dev_id.find("0a")]
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_batch_number'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_part_number'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    try:
        data_sheet['dev_id_part_rev'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    except ValueError:
        try:
            data_sheet['dev_id_part_rev'] = bytearray.fromhex(dev_id[0:2]).decode()
            print("            " + data_sheet['dev_id_part_rev'])
        except ValueError:
            data_sheet['dev_id_part_rev'] = str(bytearray.fromhex(dev_id[0:dev_id.find("0a")]))
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_serial_number'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_timestamp'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_ep_short'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_hw_version'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_par_version'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_sw_version'] = bytearray.fromhex(dev_id[0:dev_id.find("0a")]).decode()
    dev_id = dev_id[dev_id.find("0a") + 2:]
    data_sheet['dev_id_sw_timestamp'] = bytearray.fromhex(dev_id[0:26]).decode()
    dev_id = dev_id[26:]
    data_sheet['dev_id_rest'] = dev_id[0:344]

    data_sheet['standard_version'] = data_sh[512:520]
    data_sheet['imager_characteristic'] = data_sh[520:610]
    data_sheet['intrinsic_cam_param'] = data_sh[610:810]
    data_sheet['extrinsic_cam_param'] = data_sh[810:1002]
    data_sheet['defect_pixel_map'] = data_sh[1002:1010]
    data_sheet['num_of_temperatures'] = data_sh[1010:1018]
    data_sheet['num_of_roi'] = data_sh[1018:1026]
    data_sheet['max_length_persist_entry'] = data_sh[1026:]

    return data_sheet


def read_data_sheet_from_bin_output(filename):
    with open(filename, 'r') as file:
        par_file = file.readlines()

    data_sheet = dict()

    for line in par_file:
        # if line.find("macAddress") != -1:
        #     start = line.find("[") + 1
        #     end = line.find("]")
        #     target = line[start:end].replace("0x", "")
        #     target = target.replace(", ", "")
        #     data_sheet['dev_id_mac_address'] = target

        if line.find("batchNumber") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_batch_number'] = bytearray.fromhex(target).decode()

        if line.find("partNumber") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_part_number'] = bytearray.fromhex(target).decode()

        if line.find("partRev") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_part_rev'] = bytearray.fromhex(target).decode()

        if line.find("serialNumber") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_serial_number'] = bytearray.fromhex(target).decode()

        if line.find("timestamp") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_timestamp'] = target

        if line.find("epShort") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_ep_short'] = bytearray.fromhex(target).decode()

        if line.find("hwVer") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_hw_version'] = bytearray.fromhex(target).decode()

        if line.find("parVer") != -1:
            start = line.find("[") + 1
            end = line.find("]")
            target = line[start:end].replace("0x", "")
            target = target.replace(", ", "")
            data_sheet['dev_id_par_version'] = bytearray.fromhex(target).decode()

        if line.find("numbersOfRegionOfInterest") != -1:
            start = line.find("= ") + 1
            end = line.find("\n")
            target = str(int(line[start:end], 16))
            data_sheet['num_of_roi'] = target

    return data_sheet

def read_file_as_python_module(filename):
    # reads passed file and returns it as python module

    # specify the module that needs to be
    # imported relative to the path of the
    # module
    pathlib.Path(filename).name
    spec=importlib.util.spec_from_file_location(pathlib.Path(filename).name, str(filename))
    
    # creates a new module based on spec
    foo = importlib.util.module_from_spec(spec)
    
    # executes the module in its own namespace
    # when a module is imported or reloaded.
    spec.loader.exec_module(foo)

    return foo

def get_sample_mac_address(sd_ip='239.120.1.1', sd_port=30490, sender='192.168.120.3'):
    sd = ServiceDiscovery(sd_ip, sd_port)
    sd.connect()
    sd_message = sd.getSDMessage(sender=sender, timeout=2)
    sd.disconnect()
    config = sd_message.configuration()
    return config['mac_address']


def get_sample_serial_nb(sd_ip='239.120.1.1', sd_port=30490, sender='192.168.120.3'):
    sd = ServiceDiscovery(sd_ip, sd_port)
    sd.connect()
    sd_message = sd.getSDMessage(sender=sender, timeout=2)
    sd.disconnect()
    config = sd_message.configuration()
    return config['serial_nb']


def get_sample_device_type(sd_ip='239.120.1.1', sd_port=30490, sender='192.168.120.3'):
    #sd_port = 30490
    sd = ServiceDiscovery(sd_ip, sd_port)
    sd.connect()
    sd_message = sd.getSDMessage(sender=sender, timeout=2)
    sd.disconnect()
    config = sd_message.configuration()
    return config['device_type']


def get_sample_configstring(sd_ip='239.120.1.1', sd_port=30490, sender='192.168.120.3'):
    sd = ServiceDiscovery(sd_ip, sd_port)
    sd.connect()
    sd_message = sd.getSDMessage(sender=sender, timeout=2)
    sd.disconnect()
    return str(sd_message.configurationString())


def set_someip_client(client_ip="192.168.120.66", server_ip="192.168.120.2", client_source_port=6000,
                      client_destination_port=30501):

    return someip_client.SomeipClient(client_ip, server_ip, client_source_port, client_destination_port)


def assign_default_ip(ip=[0xC0, 0xA8, 0x78, 0x01], lt=[51, 4, 0xFF, 0xFF, 0xFF, 0xFF], dhcp_client_ip="any"):
    dhcpserver_ip = [ip[0], ip[1], ip[2], 0x01]

    dhcpserver = DHCPServer(67, dhcpserver_ip,
                            68, ip, lt, 1024,
                            renew_ip=False, wait_for_discovery=True, dhcp_client_ip=dhcp_client_ip)
    dhcpserver.server()
    return dhcpserver.actual_ip

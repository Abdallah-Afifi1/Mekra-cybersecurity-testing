import datetime
import sys
import time
import os


#from Lib.General import helperModule
from SOMEIP.someip_client import SomeipClient
from SOMEIP.someip_packet import SomeipPacket
#from Lib.General import SomeipSdScanner

#global dut, someip_client


def initialize():

    print("ReadCamData ini")
    """
    Initialization of the test environment.
    
    Scans for a camera with a matching device type and sets up the SOMEIP client to communicate with it.
    
    :return: None
    """
    """
    # General settings
    device_types = ["MCPnetE", "fpcam", "auxcam", "backupcam", "rearcam", "MCPnetB"]

    
    # Select camera
    dut = {}
    connected_cams = SomeipSdScanner.scan_cameras()
    print(connected_cams)
    for cam in connected_cams:
        if cam['device_type'] in device_types:
            dut = cam
            print(dut)
            break
    
    # SOMEIP client
    print("print ip: ", dut['ip_address'][0:dut['ip_address'].rfind(".") + 1] + "1")
    someip_client = SomeipClient(dut['ip_address'][0:dut['ip_address'].rfind(".") + 1] + "1",
                                 dut['ip_address'],
                                 dut['camera_service_port'],
                                 dut['camera_service_port'])
    return someip_client
    """

def parse_data_sheet(data_sh):
    data_sheet = dict()
    dev_id = data_sh[0:512]
    # print(dev_id)

    data_sheet['dev_id_mac_address'] = dev_id[0:12]
    print(data_sheet['dev_id_mac_address'])
    data_sheet['dev_id_batch_number'] = bytearray.fromhex(dev_id[14:34]).decode()
    print(data_sheet['dev_id_batch_number'] )
    data_sheet['dev_id_part_number'] = bytearray.fromhex(dev_id[36:60]).decode()
    print(data_sheet['dev_id_part_number'])
    data_sheet['dev_id_part_rev'] = bytearray.fromhex(dev_id[62:66]).decode()
    print(data_sheet['dev_id_part_rev'])
    data_sheet['dev_id_serial_number'] = bytearray.fromhex(dev_id[68:84]).decode()
    print(data_sheet['dev_id_serial_number'])
    data_sheet['dev_id_timestamp'] = bytearray.fromhex(dev_id[86:102]).decode()
    print(data_sheet['dev_id_timestamp']) 
    data_sheet['dev_id_ep_short'] = bytearray.fromhex(dev_id[104:112]).decode()
    print(data_sheet['dev_id_ep_short']) 
    data_sheet['dev_id_hw_version'] = bytearray.fromhex(dev_id[114:122]).decode()
    print(data_sheet['dev_id_hw_version'])
    data_sheet['dev_id_par_version'] = bytearray.fromhex(dev_id[124:132]).decode()
    print(data_sheet['dev_id_par_version'])
    data_sheet['dev_id_sw_version'] = bytearray.fromhex(dev_id[134:140]).decode()
    print(data_sheet['dev_id_sw_version'])
    data_sheet['dev_id_sw_timestamp'] = bytearray.fromhex(dev_id[142:168]).decode()
    print(data_sheet['dev_id_sw_timestamp'])
    dev_id = dev_id[168:]
    data_sheet['dev_id_rest'] = dev_id[0:344]
    print(data_sheet['dev_id_rest'])
    data_sheet['standard_version'] = data_sh[512:520]
    data_sheet['imager_characteristic'] = data_sh[520:610]
    data_sheet['intrinsic_cam_param'] = data_sh[610:810]
    data_sheet['extrinsic_cam_param'] = data_sh[810:1002]
    data_sheet['defect_pixel_map'] = data_sh[1002:1010]
    data_sheet['num_of_temperatures'] = data_sh[1010:1018]
    data_sheet['num_of_roi'] = data_sh[1018:1026]
    data_sheet['max_length_persist_entry'] = data_sh[1026:]

    return data_sheet


def get_cam_ident(someip_client):
    """
    Retrieve camera identification data from the camera.

    This function sends a SOME/IP request to the camera to retrieve its identification data.
    The function prints out the identification data it receives from the camera.

    :return: (data_sheet, rxpayload)
        - data_sheet: a dictionary containing the camera's identification dataf
        - rxpayload: the raw data received from the camera
    """
    print("start")
# <editor-fold desc="             # Step 01: getCamIdentification">
    print(str(datetime.datetime.now()) + " Step 01: getCamIdentification")
    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0010,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=None)

    someip_client.send_packet(
        packet=txpacket,
        target_ip=someip_client.serverIP,
        destination_port=someip_client.destinationPort)

    rxpacket = someip_client.someip_rx_packet
    rxpayload = rxpacket.get_payload()
# </editor-fold>
# <editor-fold desc="             # Step 02: snpnVolvo">
    print(str(datetime.datetime.now()) + " Step 02: SNPN Volvo")

    rx_snpn_volvo = rxpayload[0:10]  # Bytes 0 - 5, but as string representation -> 0 - 10
    print("\t" + rx_snpn_volvo)
# </editor-fold>
# <editor-fold desc="             # Step 03: serial number">
    print(str(datetime.datetime.now()) + " Step 03: Serial number")

    rx_serial_nb = rxpayload[10:18]  # Bytes 5 - 9, but as string representation -> 10 - 18
    print("\t" + rx_serial_nb)
# </editor-fold>
# <editor-fold desc="         # Step 04: mac address">
    print(str(datetime.datetime.now()) + " Step 04: MAC address")

    rx_mac_address = rxpayload[18:30]  # Bytes 9 - 15, but as string representation -> 18 - 30
    print("\t" + rx_mac_address)
# </editor-fold>
# <editor-fold desc="             # Step 05: getDataSheet">
    print(str(datetime.datetime.now()) + " Step 05: getDataSheet")

    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0001,
        length=0x00000008,
        request_id=0x00000001,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=None)

    someip_client.send_packet(
        packet=txpacket,
        target_ip=someip_client.serverIP,
        destination_port=someip_client.destinationPort)

    rxpacket = someip_client.someip_rx_packet
    # print("payload: ", rxpacket.get_payload())
    data_sheet = parse_data_sheet(rxpacket.get_payload())
    #print("instrinsic_cam_param: ", int(data_sheet['intrinsic_cam_param'], 16))
    byte_data = bytes.fromhex(data_sheet['intrinsic_cam_param'])
    string_data = byte_data[0:]
    print(string_data)
    # print("result: ", string_data.decode("utf-8"))
    
    
# </editor-fold>
# <editor-fold desc="             # Step 06: Protocol device identification batch number">
    print(str(datetime.datetime.now()) + " Step 06: Batch number")
    batch_number = data_sheet['dev_id_batch_number']
    print("\t" + batch_number)
# </editor-fold>
# <editor-fold desc="             # Step 07: device identification part number">
    print(str(datetime.datetime.now()) + " Step 07: Part number")
    part_number = data_sheet['dev_id_part_number']
    print("\t" + part_number)
# </editor-fold>
# <editor-fold desc="             # Step 08: device identification part rev">
    print(str(datetime.datetime.now()) + " Step 08: Part rev")
    part_rev = data_sheet['dev_id_part_rev']
    print("\t" + part_rev)
# </editor-fold>
# <editor-fold desc="             # Step 09: Protocol device identification serial number">
    print(str(datetime.datetime.now()) + " Step 09: Serial number")
    serial_nb = data_sheet['dev_id_serial_number']
    print("\t" + serial_nb)
# </editor-fold>
# <editor-fold desc="             # Step 10: Protocol device identification timestamp">
    print(str(datetime.datetime.now()) + " Step 10: Timestamp")
    timestamp = data_sheet['dev_id_timestamp']
    human_readable_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(timestamp, 16)))
    print("\t" + human_readable_time)
# </editor-fold>
# <editor-fold desc="             # Step 11: device identification ep short">
    print(str(datetime.datetime.now()) + " Step 11: EP short")
    ep_short = data_sheet['dev_id_ep_short']
    print("\t" + ep_short)
# </editor-fold>
# <editor-fold desc="             # Step 12: device identification HW version">
    print(str(datetime.datetime.now()) + " Step 12: HW version")
    hw_version = data_sheet['dev_id_hw_version']
    print("\t" + hw_version)
# </editor-fold>
# <editor-fold desc="             # Step 13: device identification PAR version">
    print(str(datetime.datetime.now()) + " Step 13: PAR version")
    par_version = data_sheet['dev_id_par_version']
    print("\t" + par_version)
# </editor-fold>
# <editor-fold desc="             # Step 14: device identification SW version">
    print(str(datetime.datetime.now()) + " Step 14: SW version")
    sw_version = data_sheet['dev_id_sw_version']
    print("\t" + sw_version)
# </editor-fold>
# <editor-fold desc="             # Step 15: device identification SW timestamp">
    print(str(datetime.datetime.now()) + " Step 15: SW timestamp")
    sw_timestamp = data_sheet['dev_id_sw_timestamp']
    print("\t" + sw_timestamp)
# </editor-fold>
# <editor-fold desc="             # Step 16: number of ROI">
    print(str(datetime.datetime.now()) + " Step 16: Number of ROI")
    num_roi = str(int(data_sheet['num_of_roi'], 16))
    print("\t" + num_roi)
# </editor-fold>
    print("finished")

    return data_sheet, rxpayload

def resource_path(relative_path):
    """
    Get absolute path to resource.
    
    Parameters
    ----------
    relative_path : str
        Relative path to the resource.
    
    Returns
    -------
    str
        Absolute path to the resource.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def cleanup(someip_client):
    """
    Clean up after the test run.
    
    This function is a central place to put all necessary cleanup code.
    It currently closes the SOME/IP socket and exits the program with status code 0.
    """
    someip_client.close_socket()
    #sys.exit(0)


def main():
    someip_client = initialize()
    data_sheet, payload = get_cam_ident(someip_client)
    #generate_report(data_sheet, payload)
    cleanup(someip_client)
    return data_sheet, payload


if __name__ == "__main__":
    main()



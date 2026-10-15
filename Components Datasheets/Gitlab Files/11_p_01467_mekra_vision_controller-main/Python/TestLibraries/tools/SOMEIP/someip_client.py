import ipaddress
import socket
import select
from binascii import hexlify
#from Lib.General import eventList
from tools.SOMEIP.someip_packet import SomeipPacket
from time import sleep


class SomeipClient:
    # Default server ip
    _DEFAULT_SERVER_IP = "192.168.120.10"
    # Default client ip
    _DEFAULT_CLIENT_IP = "192.168.120.1"
    # Default client port
    # using 0 lets the operating system choose the client port automatically, see "bind()" documentation
    _DEFAULT_CLIENT_PORT = 0
    # Default destination port
    _DEFAULT_DESTINATION_PORT = 30501

    def __init__(self,
                 client_ip=_DEFAULT_CLIENT_IP,
                 server_ip=_DEFAULT_SERVER_IP,
                 client_source_port=_DEFAULT_CLIENT_PORT,
                 client_destination_port=_DEFAULT_DESTINATION_PORT):

        self.hostIP = client_ip
        print("self.hostIP: ", self.hostIP)
        self.serverIP = server_ip
        print("self.serverIP: ", self.serverIP)
        self.hostPort = 50010#client_source_port ###########################this part was changed
        print("self.hostPort: ", self.hostPort)
        self.destinationPort = client_destination_port
        print("self.destinationPort: ", self.destinationPort)
        self.hostSocket = None

        # Previously send some ip message
        self.someip_tx_packet = None
        # Previously received some ip message
        self.someip_rx_packet = None

        if not self.verify_input():
            raise ValueError
        if not self.open_socket():
            raise ValueError

    def verify_input(self):

        # Check whether provided ip addresses are valid
        try:
            ipaddress.ip_address(self.hostIP)
            ipaddress.ip_address(self.serverIP)
            is_input_valid = True

        except ValueError as invalid_ip:
            print(invalid_ip)
            is_input_valid = False

        # Check host port
        if self.hostPort < 0 or self.hostPort > 65535:
            print("Wrong host port provided: " + str(self.hostPort))
            is_input_valid = False
        # check destinationPort
        if int(self.destinationPort) < 1 or int(self.destinationPort) > 65535:
            print("Wrong destination port provided: " + str(self.destinationPort))
            is_input_valid = False

        return is_input_valid

    def open_socket(self):

        try:
            # socket for some/ip camera methods
            self.hostSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("hostSocket: ", self.hostSocket)
            self.hostSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("hostSocket: ", self.hostSocket)
            host_data = (self.hostIP, self.hostPort)
            print("host_data: ", host_data)
            self.hostSocket.bind(host_data)
            print("hostSocket: ",self.hostSocket)
            self.hostSocket.setblocking(0)

            open_success = True

        except OSError as l_exceptionError:
            print("Error starts here !!!!!!!!!")
            print(l_exceptionError)
            open_success = False

        return open_success

    def close_socket(self):
        self.hostSocket.close()

    def close_clients(*clients):
        """Close every client that was opened, ignoring the ones that never were."""
        for client in clients:
            if client is not None:
                client.close_socket()    

    def subscribe_roi_video(self,
                            roi_index,
                            service_id=0x433F,
                            method_id=0x0131,
                            length=0xC,
                            request_id=0x12345678,
                            protocol_version=0x01,
                            interface_version=0x01,
                            message_type=0x00,
                            return_code=0x00):

        roi_index_byte_size = 4
        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(roi_index, roi_index_byte_size)

        self.send_packet(packet, self.serverIP, self.destinationPort)

    def unsubscribe_roi_video(self,
                              roi_index,
                              service_id=0x433F,
                              method_id=0x0132,
                              length=0xC,
                              request_id=0x12345678,
                              protocol_version=0x01,
                              interface_version=0x01,
                              message_type=0x00,
                              return_code=0x00):

        roi_index_byte_size = 4
        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(roi_index, roi_index_byte_size)

        self.send_packet(packet, self.serverIP, self.destinationPort)

    def get_cam_status(self,
                       service_id=0x433F,
                       method_id=0x0002,
                       length=0x08,
                       request_id=0x12345678,
                       protocol_version=0x01,
                       interface_version=0x01,
                       message_type=0x00,
                       return_code=0x00):

        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(None, 0)

        self.send_packet(packet, self.serverIP, self.destinationPort)

    def set_cam_exclusive(self,
                          ttl,
                          service_id=0x433F,
                          method_id=0x0011,
                          length=0x0C,
                          request_id=0x12345678,
                          protocol_version=0x01,
                          interface_version=0x01,
                          message_type=0x00,
                          return_code=0x00):

        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(ttl, 4)

        self.send_packet(packet, self.serverIP, self.destinationPort)

    def erase_cam_exclusive(self,
                            service_id=0x433F,
                            method_id=0x0019,
                            length=0x08,
                            request_id=0x12345678,
                            protocol_version=0x01,
                            interface_version=0x01,
                            message_type=0x00,
                            return_code=0x00):

        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(None, 0)

        self.send_packet(packet, self.serverIP, self.destinationPort)

    def get_cam_control(self,
                        control_index,
                        service_id=0x433F,
                        method_id=0x0203,
                        length=0x09,
                        request_id=0x12345678,
                        protocol_version=0x01,
                        interface_version=0x01,
                        message_type=0x00,
                        return_code=0x00):

        packet = SomeipPacket()
        control_index_byte_size = 1

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(control_index, control_index_byte_size)

        self.send_packet(packet, self.serverIP, self.destinationPort)

    def set_cam_control(self,
                        control_index,
                        control_mode,
                        supported_mode,
                        control_value,
                        service_id=0x433F,
                        method_id=0x0201,
                        length=0x0D,
                        request_id=0x12345678,
                        protocol_version=0x01,
                        interface_version=0x01,
                        message_type=0x00,
                        return_code=0x00):

        packet = SomeipPacket()
        control_index_byte_size = 1
        control_mode_byte_size = 1
        supported_mode_byte_size = 1
        control_value_byte_size = 2

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)

        control_index_data = (SomeipPacket.parse_someip_input(control_index)).to_bytes(control_index_byte_size,
                                                                                       byteorder='big')
        control_mode_data = (SomeipPacket.parse_someip_input(control_mode)).to_bytes(control_mode_byte_size,
                                                                                     byteorder='big')
        supported_mode_data = (SomeipPacket.parse_someip_input(supported_mode)).to_bytes(supported_mode_byte_size,
                                                                                         byteorder='big')
        control_value_data = (SomeipPacket.parse_someip_input(control_value)).to_bytes(control_value_byte_size,
                                                                                       byteorder='big')

        payload = control_index_data + supported_mode_data + control_mode_data + control_value_data
        packet.set_payload(payload,
                           control_index_byte_size +
                           control_mode_byte_size +
                           supported_mode_byte_size +
                           control_value_byte_size,
                           True)

        self.send_packet(packet, self.serverIP, self.destinationPort)

    def send_packet(self,
                    packet=None,
                    target_ip=_DEFAULT_SERVER_IP,
                    destination_port=_DEFAULT_DESTINATION_PORT,
                    event=False):

        if packet:
            data = packet.packet()
        else:
            # Abort sending
            return

        self.someip_tx_packet = packet
        self.hostSocket.sendto(data, (target_ip, int(destination_port)))
        #wait time because auf latez bei receiving packets
        sleep(0.3)
        # Check whether we get a response
        if event:          # set event when response is received
            self.someip_rx_packet = self.receive_packet_with_event()
        else:
            self.someip_rx_packet = self.receive_packet()

        return

    def send_packet_dont_wait_for_response(self,
                                           packet=None,
                                           target_ip=_DEFAULT_SERVER_IP,
                                           destination_port=_DEFAULT_DESTINATION_PORT):

        if packet:
            data = packet.packet()
        else:
            # Abort sending
            return

        self.someip_tx_packet = packet
        self.hostSocket.sendto(data, (target_ip, destination_port))

        return

    def receive_packet(self):

        select_timeout = 0.20
        receive_max_bytes = 1024
        # Wait to receive any incoming messages for certain amount of time described in select_timeout
        readable, writeable, exceptional = select.select([self.hostSocket], [], [], select_timeout)
        if self.hostSocket in readable:
            data, addr = self.hostSocket.recvfrom(receive_max_bytes)
            received_data = hexlify(data).decode('ascii')

            response_packet = SomeipPacket()
            response_packet.set_service_id("0x" + received_data[0:4])
            response_packet.set_method_id("0x" + received_data[4:8])
            response_packet.set_length("0x" + received_data[8:16])
            response_packet.set_request_id("0x" + received_data[16:24])
            response_packet.set_protocol_version("0x" + received_data[24:26])
            response_packet.set_interface_version("0x" + received_data[26:28])
            response_packet.set_message_type("0x" + received_data[28:30])
            response_packet.set_return_code("0x" + received_data[30:32])

            payload_data = received_data[32:]
            payload_size = len(payload_data)

            if payload_size > 0:
                response_packet.set_payload("0x" + payload_data, (payload_size // 2))
            else:
                response_packet.set_payload(None, 0)

        else:
            print("No incoming message received...")
            response_packet = None

        return response_packet

    def receive_packet_with_event(self):

        select_timeout = 0.10
        receive_max_bytes = 1024
        # Wait to receive any incoming messages for certain amount of time described in select_timeout
        readable, writeable, exceptional = select.select([self.hostSocket], [], [], select_timeout)
        if self.hostSocket in readable:
            #eventList.addEvent("SOMEIP message received")

            data, addr = self.hostSocket.recvfrom(receive_max_bytes)
            received_data = hexlify(data).decode('ascii')

            response_packet = SomeipPacket()
            response_packet.set_service_id("0x" + received_data[0:4])
            response_packet.set_method_id("0x" + received_data[4:8])
            response_packet.set_length("0x" + received_data[8:16])
            response_packet.set_request_id("0x" + received_data[16:24])
            response_packet.set_protocol_version("0x" + received_data[24:26])
            response_packet.set_interface_version("0x" + received_data[26:28])
            response_packet.set_message_type("0x" + received_data[28:30])
            response_packet.set_return_code("0x" + received_data[30:32])

            payload_data = received_data[32:]
            payload_size = len(payload_data)

            if payload_size > 0:
                response_packet.set_payload("0x" + payload_data, (payload_size // 2))
            else:
                response_packet.set_payload(None, 0)

        else:
            print("No incoming message received...")
            response_packet = None

        return response_packet

    def create_subscribe_roi_packet(self,
                                    roi_index=0x00,
                                    service_id=0x433F,
                                    method_id=0x0131,
                                    length=0xC,
                                    request_id=0x12345678,
                                    protocol_version=0x01,
                                    interface_version=0x01,
                                    message_type=0x00,
                                    return_code=0x00):
        roi_index_byte_size = 4
        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(roi_index, roi_index_byte_size)

        return packet

    def create_unsubscribe_roi_packet(self,
                                      roi_index=0x00,
                                      service_id=0x433F,
                                      method_id=0x0132,
                                      length=0xC,
                                      request_id=0x12345678,
                                      protocol_version=0x01,
                                      interface_version=0x01,
                                      message_type=0x00,
                                      return_code=0x00):

        roi_index_byte_size = 4
        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(roi_index, roi_index_byte_size)

        return packet

    def create_get_cam_status_packet(self,
                                     service_id=0x433F,
                                     method_id=0x0002,
                                     length=0x08,
                                     request_id=0x12345678,
                                     protocol_version=0x01,
                                     interface_version=0x01,
                                     message_type=0x00,
                                     return_code=0x00):

        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(None, 0)

        return packet

    def create_set_cam_exclusive_packet(self,
                                        ttl=3600,
                                        service_id=0x433F,
                                        method_id=0x0011,
                                        length=0x0C,
                                        request_id=0x12345678,
                                        protocol_version=0x01,
                                        interface_version=0x01,
                                        message_type=0x00,
                                        return_code=0x00):

        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(ttl, 4)

        return packet

    def create_erase_cam_exclusive_packet(self,
                                          service_id=0x433F,
                                          method_id=0x0019,
                                          length=0x08,
                                          request_id=0x12345678,
                                          protocol_version=0x01,
                                          interface_version=0x01,
                                          message_type=0x00,
                                          return_code=0x00):

        packet = SomeipPacket()

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(None, 0)

        return packet

    def create_get_cam_control_packet(self,
                                      control_index=0x02,
                                      service_id=0x433F,
                                      method_id=0x0203,
                                      length=0x09,
                                      request_id=0x12345678,
                                      protocol_version=0x01,
                                      interface_version=0x01,
                                      message_type=0x00,
                                      return_code=0x00):

        packet = SomeipPacket()
        control_index_byte_size = 1

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)
        packet.set_payload(control_index, control_index_byte_size)

        return packet

    def create_set_cam_control_packet(self,
                                      control_index=0x02,
                                      control_mode=0x03,
                                      supported_mode=0x00,
                                      control_value=0x64,
                                      service_id=0x433F,
                                      method_id=0x0201,
                                      length=0x0D,
                                      request_id=0x12345678,
                                      protocol_version=0x01,
                                      interface_version=0x01,
                                      message_type=0x00,
                                      return_code=0x00):

        packet = SomeipPacket()
        control_index_byte_size = 1
        control_mode_byte_size = 1
        supported_mode_byte_size = 1
        control_value_byte_size = 2

        packet.set_service_id(service_id)
        packet.set_method_id(method_id)
        packet.set_length(length)
        packet.set_request_id(request_id)
        packet.set_protocol_version(protocol_version)
        packet.set_interface_version(interface_version)
        packet.set_message_type(message_type)
        packet.set_return_code(return_code)

        control_index_data = (SomeipPacket.parse_someip_input(control_index)).to_bytes(control_index_byte_size,
                                                                                       byteorder='big')
        control_mode_data = (SomeipPacket.parse_someip_input(control_mode)).to_bytes(control_mode_byte_size,
                                                                                     byteorder='big')
        supported_mode_data = (SomeipPacket.parse_someip_input(supported_mode)).to_bytes(supported_mode_byte_size,
                                                                                         byteorder='big')
        control_value_data = (SomeipPacket.parse_someip_input(control_value)).to_bytes(control_value_byte_size,
                                                                                       byteorder='big')

        payload = control_index_data + supported_mode_data + control_mode_data + control_value_data
        packet.set_payload(payload,
                           control_index_byte_size +
                           control_mode_byte_size +
                           supported_mode_byte_size +
                           control_value_byte_size,
                           True)

        return packet

    def get_human_readable_return_code(self, return_code):

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


# socket for some/ip sd
# self.hostSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# l_hostData = ("", self.hostPort)
# self.hostSocket.bind(l_hostData)
# self.hostSocket.setblocking(0)
# Add host to multicast group
# l_mreq = socket.inet_aton(self.multicastIP) + socket.inet_aton(self.hostIP)
# self.hostSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, l_mreq)

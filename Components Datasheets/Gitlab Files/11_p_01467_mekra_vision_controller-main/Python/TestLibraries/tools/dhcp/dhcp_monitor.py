#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : dhcp_monitor.py
# Package : tools.dhcp
# Task    : monitor dhcp messages.
#
#
#   See also:
#              -Project MCP and MCP MoPf
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 02.07.2025 | Völler J. | initial
# 1.0.1  | 03.07.2025 | Völler J. | eventlist replaced for use with new 
#                                 | Testframework
#******************************************************************************
#
"""
.. module:: dhcp_monitor
    :platform: Unix, Windows
    :synopsis: monitor DHCP messages
"""
#
#Imports:

import binascii
import select
import socket
import time

BUFFER_SIZE = 1024


def make_even(value):
    """
    This helper is used to convert any value to an even integer.
    :param value: The given value.
    :type value: int.
    :return: int - Even number.
    """
    if value is None:
        return value
    else:
        result = int(value)
        return result if result % 2 == 0 else result + 1


class DHCPmonitor:
    """
    Can be used to receive DHCP objects or the time between DHCP packets.
    """

    def __init__(self, server_ip='192.168.120.1', client_ip='192.168.120.2'):
        """
        :param client_ip: The client address.
        :type client_ip: str.
        :param server_ip: The DHCP server address.
        :type server_ip: str.
        """
        self.client_ip = client_ip
        self.server_ip = server_ip
        self.port = 67  # DHCP destination port
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ret_val_discover = "DHCP Discover"
        self.ret_val_request = "DHCP Request"
        self.ret_val_no_msg = "No DHCP message"

    def connect(self):
        """
        Binds the socket to the given port.
        """
        print("self.server_ip: ", self.server_ip)
        print("self.port: ", self.port)
        self.sock_.bind((self.server_ip, self.port))

    def disconnect(self):
        """
        Disconnects the socket from the given port.
        """
        self.sock_.close()

    def get_dhcp_message(self, timeout=1):
        """
        :param timeout: The timeout in seconds. Use None for no timeout.
        :type timeout: float.
        :return: DHCP message type
        """

        t_start = time.perf_counter()
        t_next = t_start

        while timeout is None or t_next - t_start < timeout:
            ready = select.select([self.sock_], [], [], 1.0)

            if ready[0]:  # Read if data ready
                data, address = self.sock_.recvfrom(BUFFER_SIZE)
                l_decoded_data = (binascii.hexlify(data)).decode('utf-8')

                if address[0] == self.client_ip or self.client_ip == 'any':
                    if str(l_decoded_data[480:486]) == "350101":  # received data is of type DHCP Discover
                        temp_timestamp = time.time()
                        description = "DHCPmonitor.get_dhcp_message == DHCP Discover"
                        #eventList.addEvent('DHCPmonitor.get_dhcp_message == DHCP Discover')
                        return self.ret_val_discover, temp_timestamp, description

                    if str(l_decoded_data[480:486]) == "350103":  # received data is of type DHCP Request
                        temp_timestamp = time.time()
                        description = "DHCPmonitor.get_dhcp_message == DHCP Request"                         
                        #eventList.addEvent('DHCPmonitor.get_dhcp_message == DHCP Request')
                        return self.ret_val_discover, temp_timestamp, description


            t_next = time.perf_counter()

        return self.ret_val_no_msg

    def get_time_difference_discover(self, timeout=1, packets=2):
        """
        Get the time difference between multiple consecutive packets.
        This function is blocking. If both timeout and packets are negative,
        this will never return.
        :param timeout: The timeout in seconds. Use None for no timeout.
        :type timeout: float.
        :param packets: The number of packets to wait for. Use None for infinite.
        :type packets: int.
        :return: float[] - Time differences between consecutive packets.
        """
        t_start = time.perf_counter()
        t_next = t_start
        t_packet = []
        packet = 0
        packets = make_even(packets)

        while (timeout is None or t_next - t_start < timeout) and (packets is None or packet < packets):
            ready = select.select([self.sock_], [], [], 0.5)

            if ready[0]:  # Read if data ready
                data, address = self.sock_.recvfrom(BUFFER_SIZE)
                l_decoded_data = (binascii.hexlify(data)).decode('utf-8')

                if (address[0] == self.client_ip) and (str(l_decoded_data[480:486]) == "350101"):
                    t_packet.append(time.perf_counter())
                    packet += 1

            t_next = time.perf_counter()

        return [j - i for i, j in zip(t_packet[:-1], t_packet[1:])]

    def get_time_difference_request(self, timeout=1, packets=2):
        """
        Get the time difference between multiple consecutive packets.
        This function is blocking. If both timeout and packets are negative,
        this will never return.
        :param timeout: The timeout in seconds. Use None for no timeout.
        :type timeout: float.
        :param packets: The number of packets to wait for. Use None for infinite.
        :type packets: int.
        :return: float[] - Time differences between consecutive packets.
        """
        t_start = time.perf_counter()
        t_next = t_start
        t_packet = []
        packet = 0
        packets = make_even(packets)

        while (timeout is None or t_next - t_start < timeout) and (packets is None or packet < packets):
            ready = select.select([self.sock_], [], [], 1.0)

            if ready[0]:  # Read if data ready
                data, address = self.sock_.recvfrom(BUFFER_SIZE)
                l_decoded_data = (binascii.hexlify(data)).decode('utf-8')

                if (address[0] == self.client_ip) and (str(l_decoded_data[480:486]) == "350103"):
                    t_packet.append(time.perf_counter())
                    packet += 1

            t_next = time.perf_counter()

        return [j - i for i, j in zip(t_packet[:-1], t_packet[1:])]





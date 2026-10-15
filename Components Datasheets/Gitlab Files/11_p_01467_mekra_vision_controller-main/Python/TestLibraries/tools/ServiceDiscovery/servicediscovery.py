"""
.. module:: servicediscovery
    :platform: Unix, Windows
    :synopsis: Discover services :)
"""

import select
import socket
import struct
import time

#from Lib.General import eventList
from tools.ServiceDiscovery.sdmessage import SDMessage
from tools import eventList
BUFFER_SIZE: int = 2048


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


class ServiceDiscovery:
    """
    Can be used to receive SDMessage objects or the time between SD packets.
    """

    def __init__(self, sd_ip, sd_port):
        """
        :param sd_ip: The multicast address.
        :type sd_ip: str.
        :param sd_port: The port to bind to.
        :type sd_port: int.
        """
        self.address = sd_ip
        self.port = sd_port
        self.sock_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        print("socket.AF_INET: ", socket.AF_INET)
        print("socket.SOCK_DGRAM: ", socket.SOCK_DGRAM)
        print("socket.IPPROTO_UDP: ", socket.IPPROTO_UDP)
        #self.sock_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        """
        Binds the socket to the given port.
        """
        self.sock_.bind(('', self.port))
        mreq = struct.pack('4sL', socket.inet_aton(self.address), socket.INADDR_ANY)
        self.sock_.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def connect_if(self, ip):
        """
        Binds the socket to the given port and network interface.
        """
        try:
            self.sock_.bind((ip, self.port))
            self.sock_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock_.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
            self.sock_.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
            self.sock_.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
            self.sock_.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.address) +
                                  socket.inet_aton(ip))
        except OSError as e:
            print(e)
            print("IP:", ip)
            exit(111)

    def disconnect(self):
        """
        Disconnects the socket from the given port.
        """
        self.sock_.close()

    def getSDMessage(self, sender='Any', timeout=1):
        """
        :param sender: The sending cameras address.
        :type sender: str.
        :param timeout: The timeout in seconds. Use None for no timeout.
        :type timeout: float.
        :return: SDMessage
        """
        message = None
        t_start = time.perf_counter()
        t_next = t_start
        st = 'None' if timeout is None else str(timeout)

        while timeout is None or t_next - t_start < timeout:
            print("self.sock_: ", self.sock_)
            ready = select.select([self.sock_], [], [], timeout)
            print("ready: ", ready)

            if ready[0]:  # Read if data ready
                data, address = self.sock_.recvfrom(BUFFER_SIZE)
                print("data: ", data)
                print("address: ", address)
                if sender == 'Any' or address[0] == sender:
                    eventList.addEvent('ServiceDiscovery.getSDMessage(' + sender + ', ' + st + ')')
                    message = SDMessage(data)
                    break

            t_next = time.perf_counter()
        else:
            print("timeout ({}) expired when waiting for SD message from {} sent to {}:{}".format(timeout,
                                                                                                  sender,
                                                                                                  self.address,
                                                                                                  self.port))

        return message

    def get_sd_message_noevent(self, sender='Any', timeout=1):
        """
        :param sender: The sending cameras address.
        :type sender: str.
        :param timeout: The timeout in seconds. Use None for no timeout.
        :type timeout: float.
        :return: SDMessage
        """
        message = None
        t_start = time.perf_counter()
        t_next = t_start

        while timeout is None or t_next - t_start < timeout:
            ready = select.select([self.sock_], [], [], timeout)

            if ready[0]:  # Read if data ready
                data, address = self.sock_.recvfrom(BUFFER_SIZE)

                if sender == 'Any' or address[0] == sender:
                    message = SDMessage(data)
                    break

            t_next = time.perf_counter()
        else:
            print("timeout ({}) expired when waiting for SD message from {} sent to {}:{}".format(timeout,
                                                                                                  sender,
                                                                                                  self.address,
                                                                                                  self.port))

        return message

    def getTimeDifference(self, sender, timeout=1, packets=2):
        """
        Get the time difference between multiple consecutive packets.
        This function is blocking. If both timeout and packets are negative,
        this will never return.
        :param sender: The sending cameras address.
        :type sender: str.
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
        st = 'None' if timeout is None else str(timeout)
        sp = 'None' if packets is None else str(packets)

        while (timeout is None or t_next - t_start < timeout) and (packets is None or packet < packets):
            ready = select.select([self.sock_], [], [], timeout)

            if ready[0]:  # Read if data ready
                data, address = self.sock_.recvfrom(BUFFER_SIZE)

                if address[0] == sender:
                    if packet == 0:
                        eventList.addEvent(
                            'ServiceDiscovery.getTimeDifference('
                            + sender + ', ' + st + ', ' + sp + ')')
                    t_packet.append(time.perf_counter())
                    packet += 1

            t_next = time.perf_counter()
        else:
            print("timeout ({}) expired when waiting for SD message from {} sent to {}:{}".format(timeout,
                                                                                                  sender,
                                                                                                  self.address,
                                                                                                  self.port))

        return [j - i for i, j in zip(t_packet[:-1], t_packet[1:])]

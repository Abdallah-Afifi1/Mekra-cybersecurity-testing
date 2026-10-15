"""
.. module:: rtpListener
    :platform: Unix, Windows
    :synopsis: Information about received RTP packets.
"""

import time
import socket
import select
import struct
import ipaddress
from tools.RtpSniffer import rtpParser


BUFFER_SIZE = 2048


def parseStream(port, timeout=2, streaming_dest_ip=None, network_iface_ip=None):
    """
    Reads compression, resolution and framerate from packets.
    :param port: The port to bind to.
    :type port: int.
    :param timeout: Timeout for wait to read.
    :type timeout: float.
    :return: RTPInfo -- JPEGInfo or H264Info
    """
    if (streaming_dest_ip == None) or \
       (ipaddress.ip_address(streaming_dest_ip).is_private) or \
       (ipaddress.ip_address(streaming_dest_ip).is_reserved):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
    elif ipaddress.ip_address(streaming_dest_ip).is_multicast:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        group = socket.inet_aton(streaming_dest_ip)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(network_iface_ip))
    else:
        print("Argument error: streaming_dest_ip is not a valid IP address.")
        return None

    ts = [0, 0]
    frame = 0
    t_start = time.perf_counter()
    t_next = t_start
    rtp_info = None

    while frame < 2:  # Read packets until 2 EOF packets have been received
        ready = select.select([sock], [], [], timeout)

        if t_next - t_start > timeout:
            return None

        if ready[0]:  # Read if data ready
            data = sock.recv(BUFFER_SIZE)
            rtp_info = rtpParser.parse(data)

            if rtp_info is not None:  # If packet is of type RTP
                if rtp_info.payload_type == 'H264' or rtp_info.payload_type == 'JPEG' and rtp_info.marker:
                    ts[frame] = rtp_info.timestamp
                    if frame == 1:
                        #eventList.addEvent("rtpSniffer.parseStream(" + str(port) + ", " + str(timeout) + ")")
                        rtp_info.framerate = (ts[1] - ts[0]) / 100
                    frame += 1

        t_next = time.perf_counter()

    sock.close()
    return rtp_info


def get_rtp_packet(port, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ready = select.select([sock], [], [], timeout)

    if ready[0]:  # Read if data ready
        data = sock.recv(BUFFER_SIZE)
        sock.close()
        return rtpParser.parse(data)

    else:
        sock.close()
        return None

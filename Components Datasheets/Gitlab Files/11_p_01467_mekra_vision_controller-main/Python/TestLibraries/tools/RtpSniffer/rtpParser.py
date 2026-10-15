"""
.. module:: rtpParser
    :platform: Unix, Windows
    :synopsis: Parse RTP packets.
"""

from tools.RtpSniffer import h264Parser
from tools.RtpSniffer import jpegParser
from tools.RtpSniffer.rtpInfo import *

# RTP adresses, masks and fields within UDP payload
RTP_VERS_ADDR = 0x00
RTP_VERS_MASK = 0xC0
RTP_VERS_SHIFT = 6
RTP_VERS = 2

RTP_PAD_ADDR = 0x00
RTP_PAD_MASK = 0x20

RTP_EXT_ADDR = 0x00
RTP_EXT_MASK = 0x10

RTP_CSIC_ADDR = 0x00
RTP_CSIC_MASK = 0x0F

RTP_MARK_ADDR = 0x01
RTP_MARK_MASK = 0x80

RTP_TYPE_ADDR = 0x01
RTP_TYPE_MASK = 0x7F
RTP_TYPE_H264 = 0x60
RTP_TYPE_JPEG = 0x1A

RTP_SNR_ADDR = 0x02
RTP_SNR_LENGTH = 2

RTP_TS_ADDR = 0x04
RTP_TS_LENGTH = 4

RTP_SSI_ADDR = 0x08
RTP_SSI_LENGTH = 4

RTP_PAY_ADDR = 0x0C

# H264 adresses and fields within RTP payload
H264_TYPE_ADDR = 0x00
H264_TYPE_MASK = 0x1F
H264_TYPE_SPS = 0x07


def parse(data):
    """
    Parses the RTP packet.
    """
    packet_info = RTPInfo()
    packet_info.version = (data[RTP_VERS_ADDR] & RTP_VERS_MASK) >> RTP_VERS_SHIFT
    packet_info.padding = bool(data[RTP_PAD_ADDR] & RTP_PAD_MASK)
    packet_info.extension = bool(data[RTP_EXT_ADDR] & RTP_EXT_MASK)
    packet_info.csic = data[RTP_CSIC_ADDR] & RTP_CSIC_MASK
    packet_info.marker = bool(data[RTP_MARK_ADDR] & RTP_MARK_MASK)
    packet_info.sequence_number = int.from_bytes(data[RTP_SNR_ADDR:(RTP_SNR_ADDR + RTP_SNR_LENGTH)], 'big')
    packet_info.timestamp = int.from_bytes(data[RTP_TS_ADDR:(RTP_TS_ADDR + RTP_TS_LENGTH)], 'big')
    packet_info.ssi = int.from_bytes(data[RTP_SSI_ADDR:(RTP_SSI_ADDR + RTP_SSI_LENGTH)], 'big')

    pt = data[RTP_TYPE_ADDR] & RTP_TYPE_MASK
    if pt == RTP_TYPE_H264:
        h264_type = data[RTP_PAY_ADDR + H264_TYPE_ADDR] & H264_TYPE_MASK
        if h264_type == H264_TYPE_SPS:  # Resolution only in 'sequence parameter set'
            packet_info.payload_type = 'H264'
            packet_info.payload = h264Parser.parse(data[RTP_PAY_ADDR:])

    elif pt == RTP_TYPE_JPEG:
        packet_info.payload_type = 'JPEG'
        packet_info.payload = jpegParser.parse(data[RTP_PAY_ADDR:])

    if packet_info.payload_type and packet_info.version == RTP_VERS:
        return packet_info
    else:
        return None

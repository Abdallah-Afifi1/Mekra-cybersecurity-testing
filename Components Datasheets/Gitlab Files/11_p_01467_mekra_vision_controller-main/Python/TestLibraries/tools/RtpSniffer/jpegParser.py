"""
.. module:: jpegParser
    :platform: Unix, Windows
    :synopsis: Parse JPEG packets.
"""

from tools.RtpSniffer.jpegInfo import *

# JPEG adresses and fields within RTP payload
JPEG_TYPES_ADDR   = 0x00

JPEG_FROFF_ADDR   = 0x01
JPEG_FROFF_LENGTH = 3

JPEG_TYPE_ADDR    = 0x04

JPEG_Q_ADDR       = 0x05

JPEG_WIDTH_ADDR   = 0x06
JPEG_HEIGHT_ADDR  = 0x07
JPEG_RES_FACTOR   = 8

def parse(data):
    """
    Parses the JPEG packet.
    """
    packetInfo = JPEGInfo()
    
    packetInfo.type_specific = data[JPEG_TYPES_ADDR]
    packetInfo.fragment_offset = int.from_bytes(data[JPEG_FROFF_ADDR:(JPEG_FROFF_ADDR + JPEG_FROFF_LENGTH)], 'big')
    packetInfo.type = data[JPEG_TYPE_ADDR]
    packetInfo.q = data[JPEG_Q_ADDR]
    packetInfo.width = data[JPEG_WIDTH_ADDR] * JPEG_RES_FACTOR
    packetInfo.height = data[JPEG_HEIGHT_ADDR] * JPEG_RES_FACTOR

    return packetInfo
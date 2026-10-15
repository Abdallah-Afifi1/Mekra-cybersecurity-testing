"""
.. module:: h264Parser
    :platform: Unix, Windows
    :synopsis: Parse H264 SPS packets.
"""

from bitstring import ConstBitStream
from tools.RtpSniffer.h264Info import *

def parse(data):
    bitstream = ConstBitStream(data)
    packetInfo = H264Info()

    # ... dein bisheriger Code bis seq_parameter_set_id = bitstream.read('ue')

    # WICHTIG: Standardwerte setzen, bevor irgendein if/else kommt
    chroma_format_idc = 1               # H.264-Standard: 4:2:0
    separate_colour_plane_flag = False  # Standard: keine separaten Ebenen

    if packetInfo.profile_idc == 100 or packetInfo.profile_idc == 110 or \
       packetInfo.profile_idc == 122 or packetInfo.profile_idc == 244 or \
       packetInfo.profile_idc == 44  or packetInfo.profile_idc == 83  or \
       packetInfo.profile_idc == 86  or packetInfo.profile_idc == 118 or \
       packetInfo.profile_idc == 128 or packetInfo.profile_idc == 138 or \
       packetInfo.profile_idc == 139 or packetInfo.profile_idc == 134 or \
       packetInfo.profile_idc == 135:

        chroma_format_idc = bitstream.read('ue')
        if chroma_format_idc == 3:
            separate_colour_plane_flag = bitstream.read('bool')

        bit_depth_luma_minus8 = bitstream.read('ue')
        bit_depth_chroma_minus8 = bitstream.read('ue')
        bitstream.pos += 1  # qpprime_y_zero_transform_bypass_flag

        seq_scaling_matrix_present_flag = bitstream.read('bool')
        if seq_scaling_matrix_present_flag:
            for i in range(0, 8 if chroma_format_idc != 3 else 12):
                bitstream.pos += 1  # seq_scaling_list_present_flag[i]
    
    else:
        chroma_format_idc = 1
        separate_colour_plane_flag = False

    log2_max_frame_num_minus4 = bitstream.read('ue')
    pic_order_cnt_type = bitstream.read('ue')

    if pic_order_cnt_type == 0:
        log2_max_pic_order_cnt_lsb_minus4 = bitstream.read('ue')

    elif pic_order_cnt_type == 1:
        bitstream.pos += 1 # delta_pic_order_always_zero_flag
        offset_for_non_ref_pic = bitstream.read('se')
        offset_for_top_to_bottom_field = bitstream.read('se')
        num_ref_frames_in_pic_order_cnt_cycle = bitstream.read('ue')

        for i in range(0, num_ref_frames_in_pic_order_cnt_cycle):
            bitstream.read('se') # offset_for_ref_frame[i]
    
    max_num_ref_frames = bitstream.read('ue')
    bitstream.pos += 1 # gaps_in_frame_num_value_allowed_flag

    pic_width_in_mbs_minus1 = bitstream.read('ue')
    pic_height_in_map_units_minus1 = bitstream.read('ue')

    frame_mbs_only_flag = bitstream.read('bool')
    if not frame_mbs_only_flag:
        bitstream.pos += 1 # mb_adaptive_frame_field_flag

    bitstream.pos += 1 # direct_8x8_inference_flag
    ChromaArrayType = chroma_format_idc if separate_colour_plane_flag == 0 else 0
    SubWidthC, SubHeightC = calcSubResC(chroma_format_idc, separate_colour_plane_flag)

    frame_cropping_flag = bitstream.read('bool')
    if frame_cropping_flag:
        frame_crop_left_offset = bitstream.read('ue')
        frame_crop_right_offset = bitstream.read('ue')
        frame_crop_top_offset = bitstream.read('ue')
        frame_crop_bottom_offset = bitstream.read('ue')

        if ChromaArrayType == 0:
            CropUnitX = 1
            CropUnitY = 2 - int(frame_mbs_only_flag)
        else:
            CropUnitX = SubWidthC
            CropUnitY = SubHeightC * (2 - int(frame_mbs_only_flag))

        raw_width = 16 * (pic_width_in_mbs_minus1 + 1)
        raw_height = 16 * (pic_height_in_map_units_minus1 + 1)
        packetInfo.width = raw_width - CropUnitX * (frame_crop_left_offset + frame_crop_right_offset)
        packetInfo.height = raw_height - CropUnitY * (frame_crop_top_offset + frame_crop_bottom_offset)

    else:
        packetInfo.width = 16 * (pic_width_in_mbs_minus1 + 1)
        packetInfo.height = 16 * (pic_height_in_map_units_minus1 + 1)

    return packetInfo

def calcSubResC(cfid, scpf):
    """
    Determines SubWidthC and SubHeightC based on
    chroma_format_idc and separate_colour_plane_flag
    :param cfid: chroma_format_idc.
    :type cfid: int.
    :param cfid: separate_colour_plane_flag.
    :type cfid: bool.
    """
    if cfid == 0 and scpf == False or scpf == True:
        SubWidthC = SubHeightC = 0
    elif cfid == 1:
        SubWidthC = SubHeightC = 2
    elif cfid == 2:
        SubWidthC = 2
        SubHeightC = 1
    elif cfid == 3:
        SubWidthC = SubHeightC = 1
    return (SubWidthC, SubHeightC)
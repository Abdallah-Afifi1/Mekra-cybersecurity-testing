#******************************************************************************
# -*- coding: utf-8 -*-
# File   : simit_common.py
# Package: ttk_tools.siemens
# Task   : Common definitions for SIMIT signal data access via SHM coupling 
# Python : 3
#
# Copyright 2023 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 19.07.2023 | JoTremmel  | initial, moved common definitions to simit_common
#******************************************************************************
""" 
@package ttk_tools.siemens.simit_common
Common definitions for SIMIT signal data access via SHM coupling 
"""
from enum import IntEnum


# #############################################################################
class DataType(IntEnum):
    """ Data types from "Tabelle 2-3 Typkennung der Signale" """
    bool_b0 =  0 # BOOL, Bitadresse 0
    bool_b1 =  1 # BOOL, Bitadresse 1
    bool_b2 =  2 # BOOL, Bitadresse 2
    bool_b3 =  3 # BOOL, Bitadresse 3
    bool_b4 =  4 # BOOL, Bitadresse 4
    bool_b5 =  5 # BOOL, Bitadresse 5
    bool_b6 =  6 # BOOL, Bitadresse 6
    bool_b7 =  7 # BOOL, Bitadresse 7

    byte    =  8 # BYTE  / uint8
    word    =  9 # WORD  / uint16
    int     = 10 # INT   / sint16
    dword   = 11 # DWORD / uint32
    dint    = 12 # DINT  / sint32
    real    = 13 # REAL  / float32
    
    @property
    def is_bool(self):
        return DataType.bool_b0 <= self <= DataType.bool_b7

    @property
    def byte_size(self):
        """ data type size in bytes """
        if DataType.bool_b0 <= self <= DataType.byte:
            size = 1
        elif DataType.word <= self <= DataType.int:
            size = 2
        elif DataType.dword <= self <= DataType.real:
            size = 4
        else:
            size = None # just in case
        return size

    @property
    def struct_fmt(self):
        """ struct format for binary packing/unpacking.
            Bool/bit types default to the containing byte.
        """
        return {
            DataType.byte:  "B", # uint8   / unsigned char
            DataType.word:  "H", # uint16  / unsigned short
            DataType.int:   "h", # sint16  / short
            DataType.dword: "I", # uint32  / unsigned int
            DataType.dint:  "i", # sint32  / int
            DataType.real:  "f", # float32 / float
            # all bit types default to the containing byte
            DataType.bool_b0: "B",
            DataType.bool_b1: "B",
            DataType.bool_b2: "B",
            DataType.bool_b3: "B",
            DataType.bool_b4: "B",
            DataType.bool_b5: "B",
            DataType.bool_b6: "B",
            DataType.bool_b7: "B",
        }.get(self, None)
    
    
# #############################################################################
class Direction(IntEnum):
    """ "E/A-Kennung, d. h. die Kennung, ob das Signal ein Eingangssignal 
         (Kennwert 0) oder Ausgangssignal (Kennwert 1) ist"
    """
    # amusingly, 
    #    * "Eingangssignal (Kennwert 0)" will be set for all signals configured 
    #       in Kopplung, Shared Memory, "Ausgänge" in SIMIT
    #    * "Ausgangssignal (Kennwert 1)" will be set for all signals configured 
    #       in Kopplung, Shared Memory, "Eingänge" in SIMIT
    shm_to_simit = 0
    simit_to_shm = 1


# #############################################################################
if __name__ == '__main__':
    pass
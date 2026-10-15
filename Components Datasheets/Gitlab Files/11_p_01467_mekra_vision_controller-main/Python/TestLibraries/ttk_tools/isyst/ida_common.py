#******************************************************************************
# -*- coding: utf-8 -*-
# File    : ida_common.py
# Package : ttk_tools.isyst
# Task    : Common iDA Testware definitions, classes and utility functions
#
# Copyright 2022 - 2023 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 31.05.2022 | J.Tremmel  | initial
# 1.1.0  | 23.03.2023 | J.Tremmel  | added definitions for data recorder
# 1.2.0  | 04.07.2023 | J.Tremmel  | name updated
#******************************************************************************
""" 
@package ttk_tools.isyst.ida_common
Common iDA Testware / middleware definitions, classes and utility functions
"""
from enum import IntEnum

from ttk_base.errors    import TTkException
#from ttk_base.baseutils import EnumInfo


def _enumName(EnumClass, value):
    """ Get value's name of an enum, or "<undefined>" for undefined values. """
    try:
        return EnumClass(value).name
    except ValueError:
        return "<undefined>"


def _hexRepr(value, nibbles=0):
    """ Get a hexadecimal representation of value, fallback to default 
        representation for non-integer values.
        Parameters:
            value   - value to format as hex
            nibbles - minimum number of nibbles to show
        Returns a string
    """
    if isinstance(value, int):
        return f"{'-' if value < 0 else ''}0x{abs(value):0{nibbles}X}"
    else:
        return repr(value)
    
    
# #############################################################################
# Exceptions ~~~~~~~~~~~~~~~~~~~~~~---
# #############################################################################
class MwError(TTkException):
    """ Generic iDA Testware middleware interface error. """
    

# #############################################################################
class MwAppError(MwError):
    """ Errors during Application RPC processing (i.e. errors detected server-side)."""
    def __init__(self, message, status):
        """ Parameters:
                message - error message
                status  - MwAppStatus value
        """
        self.status  = status
        self.message = message
        full_message = f"{message}: {MwAppStatus.info(status)}"
        super().__init__(full_message)
        print(">", full_message)
    

# #############################################################################
class MwRecError(MwError):
    """ Errors during data recording """

    def __init__(self, message, status=None, info=None):
        """ Parameters:
                message - error message
                status  - RecCommandStatus value (if available)
                info    - additional error info (usually names of failed 
                          variables for status bad_config)
        """
        self.status  = status
        self.message = message
        self.info    = str(info).strip() if info is not None else ""
        full_message = str(message)
        if status is not None:
            full_message = f"{message}: {RecCommandStatus.info(status)}"
        if info is not None:
            full_message += "\n\t" + self.info.replace("\n", "\n\t")
        super().__init__(full_message)
        print(">", full_message.replace("\n", "\n> "))


# #############################################################################
# Definitions ~~~~~~~~~~~~~~~~~~~~~~---
# #############################################################################
class MwAppStatus(IntEnum):
    """ Application RPC status info (internal success/error). """
    OK               = 0x0000
    NOT_FOUND        = 0x0100
    BAD_TYPE         = 0x0200
    UNDEFINED        = 0x0300
    
    OUT_OF_RANGE     = 0x1000
    NOT_AVAILABLE    = 0x1100 # used for SHM requests
    
    UNEXPECTED_ERROR = 0xFFFF
    
    def info(self):
        return f"{_enumName(MwAppStatus, self)} [{_hexRepr(self, 4)}]"
    
    
# #############################################################################
class MwDataType(IntEnum):
    """ Data types for middleware values, compare mwvalue.h: dataType_t 
        Note: 
            Utility methods may be called as 
                * class methods with a value to interpret or
                * on on an instance without a parameter
        
        Example: Utility methods 
            >>> MwDataType.FLOAT64.info()
            "FLOAT64 [0x21]"
            
            >>> MwDataType.info(0x03)
            "UINT32 [0x03]"
            
            MwDataType.info(0x4711)
            "<undefined> [0x4711]"
    
    """
    UNDEFINED = 0x00

    UINT8   = 0x01
    UINT16  = 0x02
    UINT32  = 0x03
    UINT64  = 0x04
    
    SINT8   = 0x11
    SINT16  = 0x12
    SINT32  = 0x13
    SINT64  = 0x14
    
    FLOAT32 = 0x20
    FLOAT64 = 0x21
    
    CHAR    = 0x30
    BLOB    = 0x40

    def isNumeric(self):
        return MwDataType.UINT8 <= self <= MwDataType.FLOAT64

    def isINT(self):
        return MwDataType.UINT8 <= self <= MwDataType.SINT64

    def isSINT(self):
        return MwDataType.SINT8 <= self <= MwDataType.SINT64
    
    def isUINT(self):
        return MwDataType.UINT8 <= self <= MwDataType.UINT64

    def isFLOAT(self):
        return MwDataType.FLOAT32 <= self <= MwDataType.FLOAT64
    
    def isBlobby(self):
        return self in (MwDataType.CHAR, MwDataType.BLOB)
    
    # #########################################################################
    def info(self):
        """ Get an info string for the supplied MwDataType. 
            Undefined values will show as <undefined> and not raise an exception.
        """
        return f"{_enumName(MwDataType, self)} [{_hexRepr(self, 2)}]"


# #############################################################################
class MetaKind(IntEnum):
    """ MetaKind as defined in protobuf message MetaId """
    # variable meta
    name            = 0 # string, base name of variable w/o index or system
    size            = 1 # uint32, array size for numeric types or length for blob/char types
    data_type       = 2 # uint8, from dataType_t enum 
    unit            = 3 # string
    display_format  = 4 # string
    min_limit       = 5 # numeric value, type depends on var data type
    max_limit       = 6 # numeric value, type depends on var data type
    default_value   = 7 # numeric value, type depends on var data type
    description     = 8 # string, optional description from system xml
    display_name    = 9 # string, may contain index suffix for array variables
    
    # system meta
    system_name     = 100 # string, name of system (from system description)
    instance_key    = 101 # uint64, unique instance key generated at service start
    var_count       = 102 # uint64, total number of available variables on system (i.e. IDs, counting all array elements)
    version         = 103 # string, main/system version (from MAIN_VERSION)
    
    def info(self):
        return f"{_enumName(MetaKind, self)} [{self}]"
        

# #############################################################################
class RecCommandStatus(IntEnum):
    """ Recorder command RPC status info (internal success/error). """
    success          = 0 # generic all-ok
    bad_config       = 1 # setupVars, not all variables could be resolved, info may contain extra information
    wrong_state      = 2 # action not possible in current state (run while running, stop while not running)
    already_in_state = 3 # state did not change, but that was ok (e.g. stopRecording while already stopped)
    
    def info(self):
        return f"{_enumName(RecCommandStatus, self)} [{self}]"


# #############################################################################
class RecState(IntEnum):
    """ Recorder state machine state """
    undefined       = 0 # undefined/invalid state
    not_configured  = 1 # not yet configured or last setup did not succeed
    configuring     = 2 # configuration pending
    ready           = 3 # configuration valid, "ready to run"
    start_recording = 4 # start recording (go to recording)
    recording       = 5 # currently recording
    stop_recording  = 6 # stop recording (and go to stopped)
    stopped         = 7 # recording stopped, data should be available to be retrieved
    sending_data    = 8 # data access/transmission in progress
    
    def info(self):
        return f"{_enumName(RecState, self)} [{self}]"


# #############################################################################
# @cond DOXYGEN_IGNORE
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    signed_types   = (MwDataType.SINT8, MwDataType.SINT16, MwDataType.SINT32, MwDataType.SINT64)
    unsigned_types = (MwDataType.UINT8, MwDataType.UINT16, MwDataType.UINT32, MwDataType.UINT64)
    float_types    = (MwDataType.FLOAT32, MwDataType.FLOAT64)


    assert MwDataType.FLOAT32 in MwDataType
    
    assert MwDataType.FLOAT32.isNumeric() 
    assert MwDataType(2).isNumeric() 

    for dt in signed_types:
        assert dt.isSINT()
        assert dt.isNumeric()
        assert MwDataType.isSINT(dt)
        assert MwDataType.isNumeric(dt)
        
        assert not dt.isUINT()
        assert not dt.isFLOAT()

    for dt in list(unsigned_types):
        assert dt.isUINT()
        assert dt.isNumeric()
        assert MwDataType.isUINT(dt)
        assert MwDataType.isNumeric(dt)
        
        assert not dt.isSINT()
        assert not dt.isFLOAT()

    for dt in (int(t) for t in unsigned_types):
        assert MwDataType.isUINT(dt)
        assert MwDataType.isNumeric(dt)


    for dt in float_types:
        assert dt.isFLOAT()
        assert dt.isNumeric()
        assert MwDataType.isFLOAT(dt)
        assert MwDataType.isNumeric(dt)
        
        assert not dt.isSINT()
        assert not dt.isUINT()



    try:
        MwDataType(4711)
    except Exception as ex:
        print(f"> {type(ex).__name__}: {ex}")
    
    print("\n#", MwDataType.FLOAT64)
    print("repr: ", repr(MwDataType.FLOAT64))
    print("str:  ", str(MwDataType.FLOAT64))
    print("name: ", MwDataType.FLOAT64.name)
    print("value:", MwDataType.FLOAT64.value)
    print()
    print("wrapped type FLOAT64's name:", MwDataType(MwDataType.FLOAT64).name)
    print("wrapped type 0x21's name:   ", MwDataType(0x21).name)
    
    print(MwDataType.FLOAT64.info())
    print(MwDataType.info(MwDataType.FLOAT64))
    print(MwDataType.info(33))
    print(MwDataType.info(0x4711))
    print(MwDataType.info(None))
    
    
    print("Done.")
# @endcond DOXYGEN_IGNORE
# #############################################################################

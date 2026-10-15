#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : gamma_api_common.py
# Package : ttk_tools.rst
# Task    : Common shared definitions and error classes for gamma_api
# Type    : Implementation
# Python  : 3.6+
#
# Copyright 2016 - 2020 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev. | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0  | 15.08.2016 | J.Tremmel | initial, moved "constants" and error classes
#                               | to a separate module
# 1.1  | 18.10.2016 | J.Tremmel | switched to EnumInfo for enum-like value containers
# 1.2  | 10.02.2017 | J.Tremmel | added DAQ exceptions and state machine states
# 1.3  | 30.06.2020 | J.Tremmel | migrated to Python 3
# 1.4  | 24.09.2020 | J.Tremmel | added GammaApiError, DataType, PVType, PVProperty,
#                               | ErrorCodes, moved BrowsingType here
# 1.5  | 09.10.2020 | J.Tremmel | added PVFieldType
#******************************************************************************
"""
@package ttk_tools.rst.gamma_api_common
Common shared definitions and error classes for gamma_api.
"""
from enum import IntFlag
from ttk_base.errors    import TTkException
from ttk_base.baseutils import EnumInfo


# #############################################################################
# Error handling ---
# #############################################################################
class GammaError(TTkException):
    """ Base Error for GammaV connection """ 
    

class GammaApiError(GammaError):
    """ Errors during C API access """
    def __init__(self, message, error_code=None):
        """ Parameters:
                message    - error message
                error_code - error code returned by API function, see ErrorCodes
        """
        super().__init__(message)
        self.error_code = error_code


class GammaDaqError(GammaError):
    """ Base Error for GammaV DAQ / data logger functionality """ 
    

class GammaDaqStateError(GammaDaqError):
    """ Gamma V DAQ state machine did not reach the expected state """ 
    def __init__(self, message, expected_state, current_state):
        """ Parameters:
                message        - error message
                expected_state - state that was expected (or potentially a list of expected states)
                current_state  - state that was actually reached (cause of error)
        """
        super().__init__(message)
        self.expected_state = expected_state
        self.current_state  = current_state
        

# #############################################################################
# Defines / Constants / Defaults ---
# #############################################################################

## default name for log files
DEFAULT_LOGFILE_NAME = "Gamma_Logfile.txt"

## default listen port of the gamma service (see gamma service configuration file)
DEFAULT_LISTEN_PORT = 0

## default timeout in [ms] to wait for the gamma service during attach
DEFAULT_ATTACH_TIMEOUT = 5000


# #############################################################################
class MESSAGE_MODE(EnumInfo):
    """ Message modes """
    CONSOLE        = 0
    FILE           = 1
    SYSLOG         = 2
    CONSOLE_FILE   = 3
    CONSOLE_SYSLOG = 4
    
    __info_mapping__ = {
        CONSOLE:        'console',
        FILE:           'file',
        SYSLOG:         'syslog',
        CONSOLE_FILE:   'console and file',
        CONSOLE_SYSLOG: 'console and syslog',
    }
    

# #############################################################################
class LOG_LEVEL(EnumInfo):
    """ Log levels """
    ERROR = 1
    WARN  = 2
    INFO  = 3
    
    __info_mapping__ = {
        ERROR:  'error',
        WARN:   'warning',
        INFO:   'info',
    }


# #############################################################################
class DataType(EnumInfo):
    """ Gamma Data Types (gc_DataType). """
    SINT_8  = 0x00
    UINT_8  = 0x01
    SINT_16 = 0x02
    UINT_16 = 0x03
    SINT_32 = 0x04
    UINT_32 = 0x05
    SINT_64 = 0x06
    UINT_64 = 0x07
    IEEE_32 = 0x08
    IEEE_64 = 0x09
    STRING  = 0x0A
    BLOB    = 0x0B
    
    INVALID = 0xFF
    
    @classmethod
    def isValid(cls, data_type):
        return cls.SINT_8 <= data_type <= cls.BLOB
    
    @classmethod
    def isNumeric(cls, data_type):
        return cls.SINT_8 <= data_type <= cls.IEEE_64
    
    @classmethod
    def isBlobby(cls, data_type):
        return data_type in (cls.STRING, cls.BLOB)
    

class PVType(EnumInfo):
    """ ga_PVType """
    # (used as c_uint) 
    SINGLE_VALUE = 0x00 # scalar value
    FIFO         = 0x01 # pv with fifo
    INVALID      = 0xFF
    

class PVProperty(IntFlag):
    """ Properties for PV operation/access mode. """
    ACC_BLOCKING        = 0b00000000_00000001
    ACC_NON_BLOCKING    = 0b00000000_00000010
    LOOKUP_LOCAL        = 0b00000000_00000100
    LOOKUP_GLOBAL       = 0b00000000_00001000
    PUT_FULL_OVERWRITE  = 0b00000000_00010000
    PUT_FULL_BLOCK      = 0b00000000_00100000
    PUT_FULL_ERROR      = 0b00000000_01000000
    GET_EMPTY_BLOCK     = 0b00000000_10000000
    GET_EMPTY_ERROR     = 0b00000001_00000000
    

class PVFieldType(EnumInfo):
    """ gc_PVFieldType - Field types of numeric PVs (gc_PV_FIELD_* entries). """
    VALUE = 1  # PV value with meta functionalities.
    ORIG  = 2  # Original PV value without meta functionalities
    SIM   = 3  # Simulation value of PV. Requires simulation to be available (does not have to be active).
    MIN   = 4  # Minimum value of  PV. Requires min boundary to be available (does not have to be active).
    MAX   = 5  # Maximum value of PV. Requires max boundary to be available (does not have to be active).
    

class ErrorCodes(EnumInfo):
    """ Gamma error codes (default return codes of API functions). """
    SUCCESS = 0 
    
    COM_INVALID_ARGUMENT            =   -1
    COM_INTERNAL_ERROR              =   -2
    COM_MALLOC_FAILED               =   -3
    COM_NOT_IMPLEMENTED             =   -4
    COM_STRING_TRUNCATED            =   -5
    COM_IO_ERROR                    =   -6
    COM_VALUE_TRUNCATION            =   -7
    COM_BAD_STATE                   =   -8
    COM_DEAD_CONNECTION             =   -9
    COM_TIMED_OUT_RPC               =  -10
    COM_SHM_INVALID                 =  -11
    COM_HIGH_LEVEL_INTERNAL_ERROR   =  -12
    COM_SESSION_IS_DEAD             =  -13
    
    ATTACH_MISSING                  = -100
    ATTACH_ALREADY                  = -101
    ATTACH_FAILED                   = -102
    ATTACH_CORRUPTED                = -103
    DETACH_DONE_BUT_CON_DEAD        = -104
    
    PV_INVALID_SYNTAX               = -200
    PV_NAME_TOO_LONG                = -201
    PV_LOCK_FAILED                  = -202
    PV_UNLOCK_FAILED                = -203
    PV_SIM_VALUE_SET_FAILED         = -204
    PV_SIM_VALUE_GET_FAILED         = -205
    PV_INVALID_DATA_TYPE            = -206
    PV_META_OP_NOT_AVAILABLE        = -207
    PV_BOUND_REJECTED               = -208
    PV_NO_COMMON_LOCK               = -209
    PV_DATA_TYPE_MISMATCH           = -210
    PV_CLOSE_DONE_BUT_CORRUPTION    = -211
    PV_FIFO_EMPTY                   = -212
    PV_FIFO_FULL                    = -213
    PV_TYPE_INVALID_OPERATION       = -214
    PV_FIFO_WOULD_BLOCK             = -215
    PV_SIG_ALREADY_ACTIVATED        = -216
    PV_SIG_ALREADY_DEACTIVATED      = -217
    
    SERVICE_SYSTEM_NOT_FOUND        = -300
    SERVICE_DUPLICATED_NAME         = -301
    SERVICE_OBJECT_NOT_EXIST        = -302
    SERVICE_NO_SUCH_HANDLE          = -303
    SERVICE_BAD_BROWSING_STATE      = -304
    SERVICE_OUT_OF_MEMORY           = -305
    SERVICE_INTERNAL_ERROR          = -306
    
    TASK_CREATE_FAILED              = -400
    TASK_WAIT_FAILED                = -401
    TASK_WAIT_TIMEOUT               = -402
    TASK_KILL_FAILED                = -403
    TASK_SCHED_FINISHED             = -404
    
    SCHEDULER_INVALID_STATE               = -405
    SCHEDULER_USER_INIT_FUNCTION_FAILED   = -406
    SCHEDULER_USER_RUN_FUNCTION_FAILED    = -407
    SCHEDULER_USER_DEINIT_FUNCTION_FAILED = -408
    
    CLIENT_LIB_NOT_FOUND                  = -500
    CLIENT_SYM_NOT_FOUND                  = -501
    CLIENT_TIMED_OUT                      = -502
    CLIENT_SOCKET_WAS_CLOSED_BY_SERVER    = -503
    CLIENT_SOCKET_RECEIVE_FAILED          = -504
    CLIENT_SOCKET_NO_SERVER_PORT          = -505
    CLIENT_SERVER_IS_BUSY                 = -506


# #############################################################################
class DaqMeasurementStatus(EnumInfo):
    """ State machine states for DAQ task """
    M_INIT                          = 0  # --
    M_WAITING_FOR_CONFIG            = 1  # Logger status: M_WAITING_FOR_CONFIG
    M_CREATE_THREAD_GET_CONFIG      = 2  # Logger status: M_CREATE_THREAD_GET_CONFIG
    M_WAITING_FOR_CONFIGDATA        = 3  # Logger status: M_WAITING_FOR_CONFIGDATA
    M_CREATE_THREAD_VALIDATE_CONFIG = 4  # Logger status: M_CREATE_THREAD_VALIDATE_CONFIG
    M_SETUP_CONFIGURATION           = 5  # Logger status: M_SETUP_CONFIGURATION
    M_WAITING_FOR_RUN_INFO          = 6  # --
    M_WAITING_FOR_RUN               = 7  # Logger status: M_WAITING_FOR_RUN
    M_RUNNING_INFO                  = 8  # --
    M_RUNNING                       = 9  # Logger status: M_RUNNING
    M_RUNNING_STOPPED_INFO          = 10 # --
    M_RUNNING_STOPPED               = 11 # Logger status: M_RUNNING_STOPPED
    M_DEINIT                        = 12 # Logger status: M_DEINIT
    
    
# #############################################################################
class BrowsingType(EnumInfo):
    """ Wrapper for enum gc_BrowsingType (BROWSING_TYPE_*). See GaAPI.getPVs. """
    SYSTEM               =  0
    NODE                 =  1
    ACTION               =  2
    LOOP                 =  3
    TASK                 =  4
    IO                   =  5
    SCHEDULER            =  6
    MEMORY               =  7
    IO_INPUT             =  8
    IO_OUTPUT            =  9
    SCHEDULER_SLOT       = 10
    GROUP                = 11
    PV_ARRAY             = 12
    FIFO                 = 13
    NODE_ALIAS           = 14
    LOOP_ALIAS           = 15
    ACTION_ALIAS         = 16
    TASK_ALIAS           = 17
    SCHEDULER_ALIAS      = 18
    PV_ARRAY_ALIAS       = 19
    FIFO_ALIAS           = 20
    GROUP_ALIAS          = 21
    MEMORY_ALIAS         = 22
    SCHEDULER_SLOT_ALIAS = 23
    

# #############################################################################
# @cond DOXYGEN_IGNORE 
# #############################################################################
if __name__ == '__main__':  # pragma: no cover (contains only sample code)
    
    MESSAGE_MODE.printDefinedValues()
    LOG_LEVEL.printDefinedValues()
    
    DaqMeasurementStatus.printDefinedValues()

# @endcond DOXYGEN_IGNORE
# #############################################################################

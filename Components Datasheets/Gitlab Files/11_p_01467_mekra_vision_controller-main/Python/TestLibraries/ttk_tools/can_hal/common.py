#******************************************************************************
# -*- coding: utf-8 -*-
# File    : common.py
# Package : ttk_tools.can_hal
# Task    : Common CAN HAL definitions, classes and utility functions
#
# Copyright 2020 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver. | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0  | 03.06.2019 | MiJellen   | initial
# 1.1  | 04.06.2019 | JoTremmel  | refactoring, added CanHalDevice
# 1.2  | 10.11.2020 | JoTremmel  | refactoring, moved definition to common.py
#******************************************************************************
""" 
@package ttk_tools.can_hal.common
Common CAN HAL definitions, classes and utility functions
"""
from enum import IntEnum, IntFlag

from ttk_base.errors    import TTkException
from ttk_base.baseutils import EnumInfo


# #############################################################################
# Exceptions ---
# #############################################################################
class CanHalError(TTkException):
    """ Base class for CAN HAL exceptions. """


class CanHalApiError(CanHalError):
    """ Errors during HAL API access (wraps error codes). """
    def __init__(self, message, error_code, func_name=None):
        """ Parameters:
                message    - error message
                error_code - error code returned by API function, see HalErrors
                func_name  - name of API function that caused this error (if available)
        """
        try:
            # for nicer display later: wrap error code in IntEnum/EnumInfo if possible
            error_code = HalErrors(error_code)
        except ValueError:
            pass

        # getInfo also handles unknown error_codes
        error_info = f"[0x{error_code:04X}] {HalErrors.getInfo(error_code)}"
        info = f"{message}: {error_info}" if message else f"{error_info}"
        super().__init__(info)
        
        self.error_code = error_code
        self.func_name = func_name


class CanHalReadError(CanHalApiError):
    """ Error during read access.
        This class is used to represent read errors of all devices (each 
        device class has its own "read" error code.)
    """


class CanHalWriteError(CanHalApiError):
    """ Error during read access.
        This class is used to represent write errors of all devices (each 
        device class has its own "write" error code.)
    """


# #############################################################################
# Definitions ---
# #############################################################################
class DeviceType(EnumInfo):
    """ Device Type (CanHAl.h, tCanHalDeviceType). """
    # no device
    NoDevice                = 0x0000
    
    # PEAK
    PeakPCI                 = 0x0001
    PeakUSB                 = 0x0002
    PeakLAN                 = 0x0003
    PeakPCCARD              = 0x0004

    # Vector
    VectorCaseX             = 0x0020
    VectorAc2PCI            = 0x0021
    VectorCaseY             = 0x0022
    VectorCardXL            = 0x0023
    VectorCaseXL            = 0x0024
    VectorCaseXL_Log        = 0x0025
    VectorCanBoardXL        = 0x0026
    VectorCanBoardXL_PXI    = 0x0027
    VectorVN2600_2610       = 0x0028
    # kVectorVN2610           = 0x0029 # disabled in CanHal.h v1.7
    VectorVN3300            = 0x002A
    VectorVN3600            = 0x002B
    VectorVN7600            = 0x002C
    VectorCardXLE           = 0x002D
    VectorVN8900            = 0x002E
    VectorVN8950            = 0x002F
    VectorVN2640            = 0x0030
    VectorVN1610            = 0x0031
    VectorVN1630            = 0x0032
    VectorVN1640            = 0x0033
    VectorVN8970            = 0x0034
    VectorVN1611            = 0x0035
    VectorVN5610            = 0x0036
    VectorVN7570            = 0x0037
    
    # SYS TEC
    SystecUsb            = 0x0060


# #############################################################################
class CanBusState(IntFlag):
    """ CAN bus states (CanHal.h, tCanHalCanBusState). """
    NoError          = 0b000000000000
    ErrorPassive     = 0b000000000001
    ErrorBusOff      = 0b000000000010
    WarningLimitSet  = 0b000000000100
    Overrun          = 0b000000001000
    StuffError       = 0b000000010000
    FormatError      = 0b000000100000
    AcknowledgeError = 0b000001000000
    CrcError         = 0b000010000000
    ErrorFrame       = 0b000100000000
    RxBufferFull     = 0b001000000000
    TxBufferFull     = 0b010000000000
    HardwareError    = 0b100000000000


# #############################################################################
class ConfigFlag(IntFlag):
    """ Flags used during CAN configuration (CanHal.h, tCanHalCanConfig). """
    NoConfig                = 0b00000000    # kNoConfig
    ## enable acknowledge for CAN-interface
    ConfigAckOn             = 0b00000001    # kConfigAckOn
    ## enable receiving of messages
    ConfigReceiveOn         = 0b00000010    # kConfigReceiveOn
    ## enable sending of messages
    ConfigSendOn            = 0b00000100    # kConfigSendOn
    ## enable evaluation of bus statistics 
    ConfigBusStatisticsOn   = 0b00001000    # kConfigBusStatisticsOn
    ## enable evaluation of error frames
    ConfigErrorframeCheckOn = 0b00010000    # kConfigErrorframeCheckOn
    
    
# #############################################################################
class CanBitrate(IntEnum):
    """ Connection speed settings (CanHal.h, tCanHalBautrate), bits per s. """
    Bitrate1MBit   = 0x00
    Bitrate800kBit = 0x01
    Bitrate500kBit = 0x02
    Bitrate250kBit = 0x03
    Bitrate125kBit = 0x04
    Bitrate100kBit = 0x05
    Bitrate50kBit  = 0x06
    Bitrate20kBit  = 0x07
    Bitrate10kBit  = 0x08
  

# #############################################################################
class HalErrors(EnumInfo):
    """ HAL Error Codes (HalErrors.h, enum tHalError). """

    # Generic HAL errors [0x0001 - 0x001F]
    HalOk                          = 0x0000
    HalDriverNotAvailable          = 0x0001
    HalNoFreeHandles               = 0x0002
    HalNoFreeDevicListElement      = 0x0003
    HalUnknownSublayer             = 0x0004 # i.e. unsupported Sub-HAL
    HalTooManyAppsConnected        = 0x0005
    HalWrongMessageTypeForDevice   = 0x0006
    HalHdlNotInitialized           = 0x0007

    # Generic CAN errors [0x0101 - 0x011F]
    CanHalDriverNotAvailable       = 0x0101
    CanHalNoFreeHandles            = 0x0102
    CanHalNoFreeDeviceListElement  = 0x0103
    CanHalNoDriverAvailable        = 0x0104
    CanHalRxNoData                 = 0x0105
    
    # PEAK CAN specific errors [0x0120 - 0x013F]
    CanHalNoPeakDriver             = 0x0120
    CanHalPeakNoFunction           = 0x0121
    CanHalPeakHwInitError          = 0x0122
    CanHalPeakWrongMessageStatus   = 0x0123
    CanHalPeakReadError            = 0x0124
    CanHalPeakWriteError           = 0x0125
    CanHalPeakNoMessage            = 0x0126
    CanHalPeakDeviceIdReadError    = 0x0127
    CanHalPeakContrNumReadError    = 0x0128
    
    # Vector CAN specific errors [0x0140 - 0x015F]
    CanHalNoVectorDriver           = 0x0140
    CanHalVectorNoFunction         = 0x0141
    CanHalVectorInitDriverError    = 0x0142
    CanHalVectorNoDeviceFound      = 0x0143
    CanHalVectorDeviceInitError    = 0x0144
    CanHalVectorNoFreeHandle       = 0x0145
    CanHalVectorWriteError         = 0x0146
    CanHalVectorReadError          = 0x0147
    CanHalVectorNoMessage          = 0x0148
    CanHalVectorGetStateError      = 0x0149


    # SYS TEC CAN specific errors [0x0160 - 0x017F]
    CanHalNoSystecDriver           = 0x0160
    CanHalSystecNoFunction         = 0x0161
    CanHalSystecInitDriverError    = 0x0162
    CanHalSystecNoDeviceFound      = 0x0163
    CanHalSystecDeviceEnumError    = 0x0164
    CanHalSystecDeviceInitError    = 0x0165
    CanHalSystecHwInitError        = 0x0166
    CanHalSystecReadError          = 0x0167
    CanHalSystecWriteError         = 0x0168
    CanHalSystecNoMessage          = 0x0169
    CanHalSystecNoFreeHandle       = 0x016A
    

# #############################################################################
class MessageStatus(IntFlag):
    """ CAN Message Status (CanHal.h, tCanHalMessageStatus). """
    NoStatus        = 0b0000 # kNoMessageStatus
    RxMessage       = 0b0001 # kReceiveMessage
    TxMessage       = 0b0010 # kSendMessage
    RemoteRequest   = 0b0100 # kRemoteMessage   -> Remote Request Frame
    ExtendedID      = 0b1000 # kExtendedMessage -> Extended Identifier
    

# #############################################################################
if __name__ == "__main__":

    print(MessageStatus(0b101))
    ms = MessageStatus.RxMessage | MessageStatus.RemoteRequest
    print(ms)
    print(MessageStatus.RemoteRequest in ms)
    print(MessageStatus.ExtendedID in ms)
    
    
    #print(CanBaudrate(123))
    error_code = 292
    print(HalErrors(error_code)) 
    print(f"{HalErrors(error_code)}") 
    print(f"{HalErrors(error_code)!s}") 
    print(f"{HalErrors(error_code)!r}") 
    
    
    
    
    
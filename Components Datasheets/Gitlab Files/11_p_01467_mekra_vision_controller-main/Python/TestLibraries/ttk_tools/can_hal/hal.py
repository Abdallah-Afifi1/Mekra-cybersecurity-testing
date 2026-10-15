#******************************************************************************
# -*- coding: utf-8 -*-
# File    : hal.py
# Package : ttk_tools.can_hal
# Task    : CAN HAL Access (via CAN_HAL_32.dll / CAN_HAL_64.dll)
#
# Type    : Interface
# Python  : 3.6+
#
# Copyright 2020 - 2022 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver. | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 18.11.2019 | JoTremmel  | initial
# 1.0.1  | 30.05.2022 | JoTremmel  | comment cleanup, doxygen ignore markers
# 1.0.2  | 30.05.2022 | JoTremmel  | tweaks for minor/trivial review findings (#7140)
#******************************************************************************
"""
@package ttk_tools.can_hal._hal
Interface wrapper for CAN HAL access (via CAN_HAL_32.dll / CAN_HAL_64.dll) in
ttk_tools.can_hal._hal.

CAN HAL currently supports CAN interfaces by:
* PEAK-System Technik
* Vector Informatik
* SYS TEC electronic

Note:
    Windows device drivers for CAN devices have to be installed separately.
"""

# Errors ######################################################################
from ttk_tools.can_hal.common import CanHalError, CanHalApiError         # @UnusedImport
from ttk_tools.can_hal.common import CanHalReadError, CanHalWriteError   # @UnusedImport

# Enums #######################################################################
from ttk_tools.can_hal.common import DeviceType     # @UnusedImport
from ttk_tools.can_hal.common import CanBusState    # @UnusedImport
from ttk_tools.can_hal.common import CanBitrate     
from ttk_tools.can_hal.common import HalErrors      # @UnusedImport
from ttk_tools.can_hal.common import MessageStatus  # @UnusedImport

from ttk_tools.can_hal import _hal # @UnresolvedImport (compiled extension)


# #############################################################################
class CanMessage(_hal.CanMessage):
    """ CAN message data (CanHal.h, tCanHalCanMessage)."""
    
    # #########################################################################
    def __init__(self, can_id=None, dlc=None, data=None, tx=None, ext_id=None):
        """ Create an optionally pre-initialized CanMessage struct. 
            
            Parameters:
                can_id - ID of message, 11 bits (max 0x7FF) for standard, 
                         29 bits (max 0x1FFFFFFF) for extended identifiers.
                dlc    - data length code; length of message data in bytes [0..8]
                data   - payload data, either  
                            * as a byte/bytearray string or  
                            * as a list/tuple of byte values  
                tx     - True for Tx messages, False for Rx messages.
                         Sets corresponding bits to CanMessage.status.  
                         None: set no bits (in case an empty message is sufficient)
                ext_id - True: set "extended identifier" bit to `CanMessage.status`  
                         None: set bit automatically if `can_id` is larger than 
                         11 bits.
                         
            Note: Extended Identifiers
                If a `can_id` > 0x7FF is supplied and `ext_id` is False, the 
                supplied id will be truncated to 11 bits, as standard CAN 
                frames only contain the first 11-bit "Identifier A" header.
        
        """
        # fields in base structure: 
        self.can_id     = None
        self.length     = None
        self.payload    = None
        self.timestamp  = None
        self.status     = None
        
        super().___init__(can_id=can_id, dlc=dlc, data=data, tx=tx, ext_id=ext_id)
    
    # #########################################################################
    def getData(self):
        """ Get payload data as a list of byte values.
            Number of values depends on message length/dlc. 
            
            Note: Remote Requests
                RemoteRequest messages (RTR bit set in header) will not return 
                any data. 
                The length/DLC field indicates data length of the _requested_
                message (not the transmitted one)
        """
        return super().getData()
    
    # #########################################################################
    def getBytes(self):
        """ Get payload data as raw bytes string.
            Number of values depends on message length/dlc, see getData().
        """
        return super().getBytes()
    
    # #########################################################################
    def getSystemTimestamp(self):
        """ Get system time stamp of a received message in µs. 
            
            Time stamp is based on Window's QueryPerformanceCounter value at 
            time when message gets read from message queue.
            
            Note:
                Performance counter value is not synchronized to an external
                time reference, so the time stamps are only useful to check 
                intervals between messages.
                
            Returns a time stamp in µs.
        """
        return super().getSystemTimestamp()
    
    # #########################################################################
    def getHardwareTimestamp(self):
        """ Get hardware-based time stamp of a received message in µs. 
            Time stamp will be generated by CAN driver, any reference to an 
            external time base is driver/device dependent.
            
            Returns a time stamp in µs.
        """
        return super().getHardwareTimestamp()


# #############################################################################
# DLL Interface ---
# #############################################################################
class CanHal(_hal.CanHal):
    """ Low(-ish)-Level interface to CAN_HAL_(32/64).dll """
    
    # #########################################################################
    def init(self):
        """ CAN HAL init.
            Note:
                gets implicitly called at end of `__init__` 
        """
        super().init()
    
    # #########################################################################
    def deinit(self):
        """ CAN HAL deinit (also deinitializes any current devices). """
        super().deinit()
    
    # #########################################################################
    def initDevice(self, device_index, 
                         bit_rate_setting = CanBitrate.Bitrate1MBit,
                         rx_buffer_size   = 10,
                         tx_buffer_size   = 10,
                         config_flags     = None
        ):
        """ Initialize a connected CAN device. 
            Parameters:
                device_index      - index of connected device, see getDeviceList
                bit_rate_setting  - connection speed, see CanBitrate
                rx_buffer_size    - receive buffer size 
                tx_buffer_size    - transmit buffer size 
                config_flags      - optional ConfigFlag instance with set flags.  
                                    None: Use defaults
                
            Note: config_flags
                So far, it does not seem that those flags are actually used in 
                CAN_HAL
            
            Returns a CAN HAL device handle.
        """
        return super().initDevice(
            device_index, 
            bit_rate_setting = bit_rate_setting,
            rx_buffer_size   = rx_buffer_size,
            tx_buffer_size   = tx_buffer_size,
            config_flags     = config_flags
        )
        
        
    # #########################################################################
    def deinitDevice(self, device_hdl):
        """ De-initialize a CAN device. 
            Parameters:
                device_hdl - can device handle to deinit
        """
        super().deinitDevice(device_hdl)
    
    # #########################################################################
    def getDeviceList(self):
        """ Get a list of available CAN devices.
            Returns a list of DeviceListEntry items. 
        """
        return super().getDeviceList()
    
    # #########################################################################
    def getDeviceBusState(self, device_hdl):
        """ Get state of CAN bus the given device.
        
            Parameters:
                device_hdl  - handle of an initialized CAN device, see initDevice.
                
            Returns a CanBusState value.
        """
        return super().getDeviceBusState(device_hdl)
    
    # #########################################################################
    def getVersion(self):
        """ Get version of HAL.
            Returns a tuple: (major, minor, patch) version
        """
        return super().getVersion()
    
    # #########################################################################
    def sendMessage(self, can_message, device_hdl):
        """ Send a CAN message to the given device handle.
            Parameters:
                can_message - a filled CanMessage instance
                device_hdl  - handle of an initialized CAN device, see initDevice.
                
            Raises a CanHalWriteError for, well, read errors or a generic
            CanHalApiError for anything else.
            
        """
        super().sendMessage(
            can_message = can_message,
            device_hdl  = device_hdl
        )
    
    # #########################################################################
    def receiveMessage(self, device_hdl):
        """ Receive a CAN message from the given device handle.
            
            Parameters:
                device_hdl  - handle of an initialized CAN device, see initDevice.
                
            Returns a CanMessage instance or None if no message was waiting in 
            receive buffer
            Raises a CanHalReadError for, well, read errors or a generic
            CanHalApiError for anything else.
        """
        return  super().receiveMessage(device_hdl)
        

# #############################################################################
class CanHalDevice(_hal.CanHalDevice):
    """ CAN device connected to a CanHal instance"""
    
    # #########################################################################
    def __init__(self, can_hal, 
                 device_index     = 0,
                 bit_rate_setting = CanBitrate.Bitrate1MBit,
                 rx_buffer_size   = 10,
                 tx_buffer_size   = 10,
                 config_flags     = None
                 ):
        """ Parameters:
                can_hal           - parent CanHal instance
                device_index      - index of can device in CanHal, defaults
                                    to first device 
                bit_rate_setting  - connection speed, see CanBitrate
                rx_buffer_size    - receive buffer size 
                tx_buffer_size    - transmit buffer size 
                config_flags      - optional ConfigFlag instance with set flags.  
                                    None: Use defaults.  
                                    See CanHal.initDevice.
        """
        super().__init__(
            can_hal,
            device_index     = device_index,
            bit_rate_setting = bit_rate_setting,
            rx_buffer_size   = rx_buffer_size,
            tx_buffer_size   = tx_buffer_size,
            config_flags     = config_flags
        )
        
    # #########################################################################
    def deinit(self):
        """ Deinitialize this device on HAL """
        super().deinit()
    
    # #########################################################################
    def getBusState(self):
        """ Get state of CAN bus for this device.
            Returns a CanBusState value.
        """
        return super().getBusState()
    
    # #########################################################################
    def sendMessage(self, can_id, data, length=8, ext_id=None, feedback=False):
        """ Send a CAN message. 
            Parameters:
                can_id   - ID of message, 11 bits (max 0x7FF) for standard, 
                           29 bits (max 0x1FFFFFFF) for extended identifiers.
                data     - payload data, either  
                            * as a byte/bytearray string or  
                            * as a list/tuple of byte values  
                length   - length (data length code) of message data in bytes [0..8]
                ext_id   - True: set "extended identifier" bit to `CanMessage.status`  
                           None: set bit automatically if `can_id` is larger than 
                           11 bits. See CanMessage
                feedback - True: Print message info before sending to stdout
        """
        super().sendMessage(
            can_id   = can_id, 
            length   = length, 
            data     = data, 
            ext_id   = ext_id,
            feedback = feedback
        )
        
    # #########################################################################
    def sendCanMessage(self, can_message):
        """ Send a preconfigured CanMessage. 
            Parameters:
                can_message - an already configured CanMessage struct instance.
        """
        super().sendCanMessage(can_message)
        
    # #########################################################################
    def receiveMessage(self, timeout_s=2, step_s=0.100, feedback=False):
        """ Receive a message (get a pending message from receive buffer).
            
            Parameters:
                timeout_s - maximum time to wait for a message to appear in [s].  
                            0: return immediately after checking once.
                step_s    - wait time between checks for new messages in [s]
                feedback  - True: Print progress/status info to stdout
                
            Returns a CanMessage instance, or None if buffer was empty
        """
        return super().receiveMessage(
            timeout_s = timeout_s,
            step_s    = step_s, 
            feedback  = feedback
        )


# #############################################################################
# @cond DOXYGEN_IGNORE
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    import time
    
    hal = None
    try:
        hal = CanHal()
        print("HAL version:", str(hal.getVersion()))
        
        devices = hal.getDeviceList()
        if devices:
            print(f"{len(devices)} available devices(s): ")
            for index, device in enumerate(devices):
                print(f"[{index}] {device}")
                print("-" * 64)
        else:
            print("No devices detected")
        
        
        # find first free (i.e. not in use by other applications) device
        device_index = None
        for index, device in enumerate(devices):
            if device.is_free:
                device_index = index
                break
            
        if device_index is None:
            print("> No free/unused devices found")
        else:
            device = devices[device_index] 
            print(f"Connecting to device {device_index}: {device.DeviceType!s} 0x{device.DeviceNumber:X}...")
            
            dev = CanHalDevice(hal, device_index)
            print(dev.getBusState())
            
            print("Sending Standard Message...")
            dev.sendMessage(0x123, [1, 2, 3, 4, 5, 6, 7, 8])
            print("Sending Extended Message...")
            dev.sendMessage(0x20001, [0x47, 0x11])
            
            print(dev.getBusState())
            
            print("Receiving a Message (maybe)...")
            print(dev.receiveMessage(timeout_s=5, feedback=True))
            print(dev.getBusState())
            
            print("Receiving a Message (maybe)...")
            print(dev.receiveMessage(timeout_s=5, feedback=True))
            print(dev.getBusState())
            
            #time.sleep(0.100)
            print("Receiving Messages...")
            start_time = time.time()
            timeout = 10
            while True:
                msg = dev.receiveMessage(timeout_s=0, feedback=False)
                if msg is not None:
                    print()
                    print(msg)
                    # print(msg.getSystemTimestamp())
                    # print(msg.getHardwareTimestamp())
                else:
                    print(".", end="", flush=True)
                delta = time.time() - start_time
                if delta > timeout:
                    break
                #time.sleep(0.100)
                #time.sleep(0.010)
                time.sleep(0.001)
                
            print("\nstopped checking")
                 
            
    
    finally:
        if hal:
            # hal.deinit will also attempt to de-initialize all known devices
            hal.deinit()
    
    print("Done.")
# @endcond DOXYGEN_IGNORE
# #############################################################################


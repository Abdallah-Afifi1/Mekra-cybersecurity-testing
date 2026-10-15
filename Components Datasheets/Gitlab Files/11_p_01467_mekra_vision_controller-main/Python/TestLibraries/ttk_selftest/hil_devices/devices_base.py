#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : devices_base.py
# Package : ttk_selftest
# Task    : Wrapper classes for HIL device descriptions
# Python  : 3.8+
# Type    : Base implementation
# Copyright 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 10.09.2018 | C.Haas     | initial (derived from 
#                                  | selftest_hil_devices_base)
# 1.1.0  | 08.07.2020 | C.Haas     | Removed unused parameter of hilVarFactory
# 2.0.0  | 09.01.2024 | M. Jellen  | Python3 update
#******************************************************************************
"""
@package ttk_selftest.devices_base
Interface wrapper for HIL device descriptions.

"""
# Imports
from ttk_selftest.hil_devices._devices_base import HilDevice       as _HilDevice       # @UnresolvedImport (compiled extension)
from ttk_selftest.hil_devices._devices_base import GND             as _GND             # @UnresolvedImport (compiled extension)
from ttk_selftest.hil_devices._devices_base import DeviceContainer as _DeviceContainer # @UnresolvedImport (compiled extension)


# #############################################################################
# HIL device - Base class for HIL devices
# #############################################################################
class HilDevice(_HilDevice):
    """ Base HIL device container for a testable HIL device
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, fiu_channel_1, fiu_channel_2=None,
                 preconditions=None, wait_time_ms=None,
                 alias="", descr=""
                 ):
        """ HIL device initialization.
            
            Parameters:
                fiu_channel_1 - first fiu channel of the device
                fiu_channel_2 - (opt) second fiu channel of the device
                                default to None
                preconditions - (opt) preconditions that have to be set before
                                the device can be checked.
                                defaults to None
                                preconditions have to be specified as a list 
                                of dictionaries where each list element specifies one precondition.
                                Each dictionary consists of the keys "device"
                                and "value", where "value" specifies the value to
                                be set for the "device". 
                                Alternatively, functions can be called. In this case,
                                the keys "func", "set_func" or "reset_func" and optional arguments
                                have to be part of the dictionary. The functions
                                specified with "func" will be called when the preconditions
                                are set and reset, the functions specified
                                with "set_func" will only be called when preconditions are set,
                                the functions specified with "reset_func" will only be called
                                when preconditions are reset.
                                
                                Example: Set device Voltage to 13V and ClampSwitch to 1 
                                    preconditions = [
                                        {"device": Voltage, "value": 13},
                                        {"device": ClampSwitch, "value": 1},
                                    ]
                                
                                Example: function calls
                                    # For special cases, the preconditions may also contain function calls
                                    # (which might be useful to insert additional delays or similar):
                                    preconditions = [
                                        { "device": Voltage, "value": 1},
                                        { "func":   time.sleep,
                                            "args":   [1.0], # positional arguments
                                            "kwargs": {},    # keyword arguments
                                        },
                                        {"device": ClampSwitch, "value": 1},
                                        # or a simple call like this:
                                        { "func":  someCustomFunction,
                                        },
                                        ...
                                    ]
                wait_time_ms  - (opt) waiting time in milliseconds between
                                channel stimulation and channel check
                                defaults to 100ms
                alias         - (opt) device alias/name, defaults to the
                                last (non-default) entry in identifier
                                (i.e. signal model path)
                descr         - (opt) device description
        """
        _HilDevice.__init__(
            self, fiu_channel_1, fiu_channel_2,
            preconditions, wait_time_ms, alias, descr)
            

# #############################################################################
# GND channel - Base class for system ground channels
# #############################################################################
class GND(_GND):
    """ Base ground signal container for a testable ground signal
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, fiu_channel, preconditions=None, wait_time_ms=None,
                 alias="", descr=""):
        """ GND channel initialization
            
            Parameters:
                fiu_channel   - fiu channel of the ground signal
                preconditions - (opt) preconditions that have to be set before
                                the device can be checked.
                                defaults to None
                                preconditions have to be specified as a list 
                                of dictionaries where each list element specifies one precondition.
                                Each dictionary consists of the keys "device"
                                and "value", where "value" specifies the value to
                                be set for the "device". 
                                Alternatively, functions can be called. In this case,
                                the keys "func", "set_func" or "reset_func" and optional arguments
                                have to be part of the dictionary. The functions
                                specified with "func" will be called when the preconditions
                                are set and reset, the functions specified
                                with "set_func" will only be called when preconditions are set,
                                the functions specified with "reset_func" will only be called
                                when preconditions are reset.
                                
                                Example: Set device Voltage to 13V and ClampSwitch to 1 
                                    preconditions = [
                                        {"device": Voltage, "value": 13},
                                        {"device": ClampSwitch, "value": 1},
                                    ]
                                
                                Example: function calls
                                    # For special cases, the preconditions may also contain function calls
                                    # (which might be useful to insert additional delays or similar):
                                    preconditions = [
                                        { "device": Voltage, "value": 1},
                                        { "func":   time.sleep,
                                            "args":   [1.0], # positional arguments
                                            "kwargs": {},    # keyword arguments
                                        },
                                        {"device": ClampSwitch, "value": 1},
                                        # or a simple call like this:
                                        { "func":  someCustomFunction,
                                        },
                                        ...
                                    ]
                wait_time_ms  - (opt) waiting time in milliseconds between
                                      ground stimulation and ground check
                                      defaults to 100ms
                alias         - (opt) ground alias/name
                                      defaults is None
                descr         - (opt) ground description (e.g. used in report entries)
        
        """
        _GND.__init__(self, fiu_channel,
                      preconditions, wait_time_ms, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for the ground device: alias, FIU channel 
            plus description, if available.  
            
            Returns a formatted string.
        """
        return _GND.info(self)
        

# #############################################################################
# HIL device Container
# #############################################################################
class DeviceContainer(_DeviceContainer):
    """ Base class for  HIL device containers. """
    def __init__(self, context):
        """ Parameters:
                context           - parent context
        """
        _DeviceContainer.__init__(self, context)
    
    def iterDevices(self, device_type):
        """ Iterate over all devices of type "device_type".
            
            Parameters:
                device_type - type specification of the requested devices
            
            Usage:
                for dev in dev.iterDevices(AnalogOutput):
                    print dev
            
            Returns an iterator object.
        """
        return _DeviceContainer.iterDevices(self, device_type)

#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : analog_devices.py
# Package : ttk_selftest
# Task    : Wrapper classes for analog device descriptions
# Python  : 3.8+
# Type    : Base implementation
# Copyright 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 10.09.2018 | C.Haas     | initial (derived from 
#                                  | selftest_hil_devices_base)
# 2.0.0  | 09.01.2024 | M. Jellen  | Python3 update
#******************************************************************************
"""
@package ttk_selftest.hil_devices.analog_devices
Interface wrapper for analog device descriptions.

"""
# Imports
from ttk_selftest.hil_devices._analog_devices import AnalogChannel as _AnalogChannel  # @UnresolvedImport (compiled extension)
from ttk_selftest.hil_devices._analog_devices import AnalogInput   as _AnalogInput    # @UnresolvedImport (compiled extension)
from ttk_selftest.hil_devices._analog_devices import AnalogOutput  as _AnalogOutput   # @UnresolvedImport (compiled extension)


# #############################################################################
# Analog channel - Base class for analog channels
# #############################################################################
class AnalogChannel(_AnalogChannel):
    """ Base analog channel container for a testable analog channel
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, sig_channel, ref_channel,
                 max_value, min_value=0, abs_tol=0.05, rel_tol=0.01,
                 preconditions=None, wait_time_ms=None,
                 unit="", alias="", descr=""):
        """ Analog channel initialization.
            
            Parameters:
                context       - parent context
                base_path     - base path to analog channel subsystem
                sig_channel   - fiu channel of the analog channel
                                equals positive path of the analog signal
                ref_channel   - reference channel of the analog channel
                                equals ground path of analog signal 
                                can be either GND device or FiuChannel
                max_value     - maximum allowed physical value of the channel
                                at ECU connector
                min_value     - (opt) minimum allowed physical value of the
                                channel at the ECU connector
                                defaults to 0
                abs_tol       - (opt) absolute tolerance,
                                defaults to 0.05
                rel_tol       - (opt) relative tolerance,
                                defaults to 0.01 = 1%
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
                unit          - (opt) unit of the physical value
                                defaults to "V"
                alias         - (opt) channel alias/name, defaults to the
                                last (non-default) entry in identifier
                                (i.e. signal model path)
                descr         - (opt) channel description (e.g. used in report entries)
        
        """
        _AnalogChannel.__init__(self, context, base_path,
                                sig_channel, ref_channel, max_value, min_value,
                                abs_tol, rel_tol, preconditions, wait_time_ms,
                                unit, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this analog channel: alias, FIU channels, 
            minimum and maximum value plus description, if available.  
            
            Returns a formatted string.
        """
        return _AnalogChannel.info(self)
    
    # #########################################################################
    def getFormattedValue(self, value=None):
        """ Get a formatted representation of the SelfTestVariable for the given 
            value using the defined format string. An empty (or non-defined)
            format string will use the value's default string representation.
            
            Parameters:
                value     - value for which to get a string representation.  
                            If None, the last value (read or written) will be 
                            used instead (see self.last_value).
            
            Returns a formatted string representation. 
        """
        return _AnalogChannel.getFormattedValue(self, value)
        

# #############################################################################
# Analog channel - Base class for analog outputs
# #############################################################################
class AnalogOutput(_AnalogOutput):
    """ Base analog output container for a testable analog output
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, sig_channel, ref_channel,
                 max_value, min_value=0, abs_tol=0.05, rel_tol=0.01,
                 preconditions=None, wait_time_ms=None,
                 unit="", alias="", descr=""):
        """ Analog output initialization.
            
            Parameters:
                context       - parent context
                base_path     - base path to analog channel subsystem
                sig_channel   - fiu channel of the analog channel
                                equals positive path of the analog signal
                ref_channel   - reference channel of the analog channel
                                equals ground path of analog signal 
                                can be either GND device or FiuChannel
                max_value     - maximum allowed physical value of the channel
                                in V at ECU connector
                min_value     - (opt) minimum allowed physical value of the
                                channel at the ECU connector
                                default is 0
                abs_tol       - (opt) absolute tolerance,
                                defaults to 0.05
                rel_tol       - (opt) relative tolerance,
                                defaults to 0.01 = 1%
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
                unit          - (opt) unit of the physical value
                                defaults to "V"
                alias         - (opt) channel alias/name, defaults to the
                                last (non-default) entry in identifier
                                (i.e. signal model path)
                descr         - (opt) channel description (e.g. used in report entries)
        
        """
        _AnalogOutput.__init__(self, context, base_path,
                               sig_channel, ref_channel, max_value, min_value,
                               abs_tol, rel_tol, preconditions, wait_time_ms,
                               unit, alias, descr)
    
    # #########################################################################
    def set(self, value, *args, **kwargs):
        """ Function to set the SelfTestVariable of the channel
            
            Parameters:
                value - value to set
            
            Note:
                Any additional parameters will be forwarded to the write
                implementation of the variable instance
            
            Returns the original value before the set operation occurred.
        """
        return _AnalogOutput.set(self, value, *args, **kwargs)
    
    # #########################################################################
    def reset(self, verbosity=1):
        """ Function to reset the SelfTestVariable of the channel to its 
            initial value.
            
            Parameters:
                verbosity - verbosity of log output,  
                            0: silent,  
                            1: show calls to non-resettable variables  
                            2: show all reset calls  
            
            Returns the original value (which may be None if the variable has
            not been set before)
        """
        return _AnalogOutput.reset(self, verbosity=verbosity)
        

# #############################################################################
# Analog Input - Base class for analog inputs
# #############################################################################
class AnalogInput(_AnalogInput):
    """ Base analog input container for a testable analog input
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, sig_channel, ref_channel,
                 max_value, min_value=0, use_filter=False,
                 abs_tol=0.05, rel_tol=0.01,
                 preconditions=None, wait_time_ms=None,
                 unit="", alias="", descr=""):
        """ Analog input initialization.
            
            Parameters:
                context       - parent context
                base_path     - base path to analog channel subsystem
                sig_channel   - fiu channel of the analog channel
                                equals positive path of the analog signal
                ref_channel   - reference channel of the analog channel
                                equals ground path of analog signal 
                                can be either GND device or FiuChannel
                max_value     - maximum allowed physical value of the channel
                                at ECU connector
                min_value     - (opt) minimum allowed physical value of the
                                channel at the ECU connector
                                default is 0
                use_filter    - (opt) enable/disable usage of filtered value
                                False: use (normal) unfiltered value
                                True: use filtered value
                                defaults to unfiltered value (False)
                abs_tol       - (opt) absolute tolerance,
                                defaults to 0.05
                rel_tol       - (opt) relative tolerance,
                                defaults to 0.01 = 1%
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
                unit          - (opt) unit of the physical value
                                defaults to "V"
                alias         - (opt) channel alias/name, defaults to the
                                last (non-default) entry in identifier
                                (i.e. signal model path)
                descr         - (opt) channel description (e.g. used in report entries)
        
        """
        _AnalogInput.__init__(self, context, base_path,
                              sig_channel, ref_channel, max_value, min_value,
                              use_filter, abs_tol, rel_tol, preconditions,
                              wait_time_ms, unit, alias, descr)
    
    # #########################################################################
    def get(self):
        """ Function to get the current value of the SelfTestVariable depended
            of the filter setting.
            
            Parameters:
                None 
            
            Returns the current value of the filtered or unfiltered SelfTestVariable, 
            depended on the setting of the use_filter parameter of the object.
        """
        return _AnalogInput.get(self)

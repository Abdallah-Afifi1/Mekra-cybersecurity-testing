#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : digital_devices.py
# Package : ttk_selftest
# Task    : Wrapper classes for digital device descriptions
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
# 2.0.0  | 09.01.2024 | M. Jellen  | Python3 update
#******************************************************************************
"""
@package ttk_selftest.hil_devices.digital_devices
Interface wrapper for digital device descriptions.

"""
# Imports                    
from ttk_selftest.hil_devices._digital_devices import DigitalChannel as _DigitalChannel # @UnresolvedImport (compiled extension)
from ttk_selftest.hil_devices._digital_devices import DigitalInput   as _DigitalInput   # @UnresolvedImport
from ttk_selftest.hil_devices._digital_devices import DigitalOutput  as _DigitalOutput  # @UnresolvedImport
from ttk_selftest.hil_devices._digital_devices import PwmChannel     as _PwmChannel     # @UnresolvedImport
from ttk_selftest.hil_devices._digital_devices import PwmInput       as _PwmInput       # @UnresolvedImport
from ttk_selftest.hil_devices._digital_devices import PwmOutput      as _PwmOutput      # @UnresolvedImport
from ttk_selftest.hil_devices._digital_devices import Switch         as _Switch         # @UnresolvedImport
from ttk_selftest.hil_devices._digital_devices import C2DOutput      as _C2DOutput      # @UnresolvedImport


# #############################################################################
# Digital channel - Base class for digital channels
# #############################################################################
class DigitalChannel(_DigitalChannel):
    """ Base digital channel container for a testable digital channel
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, base_path, sig_channel, max_voltage,
                 preconditions=None, wait_time_ms=None, alias="", descr=""):
        """ Digital channel initialization.
            
            Parameters:
                base_path         - base path to digital channel subsystem
                sig_channel       - fiu channel of the digital channel
                max_voltage       - maximum physical voltage in V of the channel
                preconditions     - (opt) preconditions that have to be set before
                                    the device can be checked.
                                    default is None
                                    preconditions have to be specified as a list 
                                    of dictionaries where each list element specifies one precondition.
                                    Each dictionary consists of the keys "device"
                                    and "value", where "value" specifies the value to
                                    be set for the "device". 
                                    Alternatively, functions can be called. In this case,
                                    the keys "func", "set_func" or "reset_func" and optional arguments
                                    have to be part of the dictionary. The function
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    channel stimulation and channel check
                                    defaults to 100ms
                alias             - (opt) channel alias/name, defaults to the
                                    last (non-default) entry in identifier
                                    (i.e. signal model path)
                descr             - (opt) channel description (e.g. used in report entries)
        
        """
        _DigitalChannel.__init__(self, base_path, sig_channel, max_voltage,
                                 preconditions, wait_time_ms, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this digital channel: alias, FIU channel and
            maximum voltage plus description, if available.  
            
            Returns a formatted string.
        """
        return _DigitalChannel.info(self)
        

# #############################################################################
# Digital input - Base class for digital input channels
# #############################################################################
class DigitalInput(_DigitalInput):
    """ Base digital input container for a testable digital input
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, sig_channel, max_voltage,
                 threshold_voltage=None, preconditions=None,
                 wait_time_ms=None, alias="", descr=""):
        """ Digital input initialization.
            
            Parameters:
                context           - parent context
                base_path         - base path to digital input subsystem
                sig_channel       - fiu channel of the digital input channel
                max_voltage       - maximum physical voltage in V of the channel
                threshold_voltage - (opt) voltage threshold in V for high/low detection
                                    defaults to 2.5V (due to the threshold voltage
                                    of the digital signal conditioning card DSK)
                preconditions     - (opt) preconditions that have to be set before
                                    the device can be checked.
                                    default is None
                                    preconditions have to be specified as a list 
                                    of dictionaries where each list element specifies one precondition.
                                    Each dictionary consists of the keys "device"
                                    and "value", where "value" specifies the value to
                                    be set for the "device". 
                                    Alternatively, functions can be called. In this case,
                                    the keys "func", "set_func" or "reset_func" and optional arguments
                                    have to be part of the dictionary. The function
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    channel stimulation and channel check
                                    defaults to 100ms
                alias             - (opt) channel alias/name, defaults to the
                                    last (non-default) entry in identifier
                                    (i.e. signal model path)
                descr             - (opt) channel description (e.g. used in report entries)
        
        """
        _DigitalInput.__init__(self, context, base_path, sig_channel,
                               max_voltage, threshold_voltage, preconditions,
                               wait_time_ms, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this digital input channel: alias, FIU channel,
            maximum voltage and threshold voltage plus description, if available.  
            
            Returns a formatted string.
        """
        return _DigitalInput.info(self)
        

# #############################################################################
# Digital output - Base class for digital output channels
# #############################################################################
class DigitalOutput(_DigitalOutput):
    """ Base digital output container for a testable digital output
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, sig_channel, max_voltage,
                 max_low_voltage=None, min_high_voltage=None,
                 preconditions=None, wait_time_ms=None, alias="", descr=""):
        """ Digital output initialization.
            
            Parameters:
                context           - parent context
                base_path         - base path to digital output subsystem
                sig_channel       - fiu channel of the digital output channel
                max_voltage       - maximum physical voltage in V of the channel
                max_low_voltage   - (opt) maximum allowed voltage in V of state "Low"
                                    defaults to 0.5V
                min_high_voltage  - (opt) minimum allowed voltage in V of state "High"
                                    defaults to 90% of max_voltage
                preconditions     - (opt) preconditions that have to be set before
                                    the device can be checked.
                                    default is None
                                    preconditions have to be specified as a list 
                                    of dictionaries where each list element specifies one precondition.
                                    Each dictionary consists of the keys "device"
                                    and "value", where "value" specifies the value to
                                    be set for the "device". 
                                    Alternatively, functions can be called. In this case,
                                    the keys "func", "set_func" or "reset_func" and optional arguments
                                    have to be part of the dictionary. The function
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    channel stimulation and channel check
                                    defaults to 100ms
                alias             - (opt) channel alias/name, defaults to the
                                    last (non-default) entry in identifier
                                    (i.e. signal model path)
                descr             - (opt) channel description (e.g. used in report entries)
        
        """
        _DigitalOutput.__init__(self, context, base_path, sig_channel,
                                max_voltage, max_low_voltage, min_high_voltage,
                                preconditions, wait_time_ms, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this digital output channel: alias, FIU channel,
            maximum voltage, maximum voltage for state "Low" and
            minimum voltage for state "High" plus description, if available.  
            
            Returns a formatted string.
        """
        return _DigitalOutput.info(self)
        

# #############################################################################
# PWM channel - Base class for PWM channels
# #############################################################################
class PwmChannel(_PwmChannel):
    """ Base PWM channel container for a testable PWM channel
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, base_path, sig_channel, max_freq=None, 
                 abs_tol_freq=0.1, rel_tol_freq=0.05, abs_tol_dc = 5,
                 threshold_voltage=None, min_freq=None, preconditions=None,
                 wait_time_ms=None, alias="", descr=""):
        """ PWM channel initialization.
            
            Parameters:
                base_path         - base path to PWM channel subsystem
                sig_channel       - fiu channel of the PWM channel
                max_freq          - (opt) maximum frequency of the PWM channel
                                    defaults to "Inf"
                abs_tol_freq      - (opt) absolute frequency tolerance
                                    defaults to 0.1Hz
                rel_tol_freq      - (opt) relative frequency tolerance
                                    defaults to 0.05 = 5%
                abs_tol_dc        - (opt) absolute duty cycle tolerance
                                    defaults to 5%
                threshold_voltage - (opt) voltage threshold in V for high/low detection
                                    defaults to 2.5V (due to the threshold voltage
                                    of the iSystemReferenceCard iSRC)
                min_freq          - (opt) minimum frequency in Hz of the PWM channel
                                    defaults to 0Hz
                preconditions     - (opt) preconditions that have to be set before
                                    the device can be checked.
                                    default is None
                                    preconditions have to be specified as a list 
                                    of dictionaries where each list element specifies one precondition.
                                    Each dictionary consists of the keys "device"
                                    and "value", where "value" specifies the value to
                                    be set for the "device". 
                                    Alternatively, functions can be called. In this case,
                                    the keys "func", "set_func" or "reset_func" and optional arguments
                                    have to be part of the dictionary. The function
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    channel stimulation and channel check
                                    defaults to 100ms
                alias             - (opt) channel alias/name, defaults to the
                                    last (non-default) entry in identifier
                                    (i.e. signal model path)
                descr             - (opt) channel description (e.g. used in report entries)
        
        """
        _PwmChannel.__init__(self, base_path, sig_channel,
                             max_freq, abs_tol_freq, rel_tol_freq, abs_tol_dc,
                             threshold_voltage, min_freq, preconditions,
                             wait_time_ms, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this PWM channel: alias, FIU channel, 
            threshold voltage, minimum and maximum frequency
            plus description, if available.
            
            Returns a formatted string.
        """
        return _PwmChannel.info(self)
        

# #############################################################################
# PWM channel - Base class for PWM input channels
# #############################################################################
class PwmInput(_PwmInput):
    """ Base PWM input container for a testable PWM input
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, sig_channel, max_voltage, max_freq= None,
                 abs_tol_freq=0.1, rel_tol_freq=0.05, abs_tol_dc = 5,
                 threshold_voltage=None, min_freq=None, preconditions=None,
                 wait_time_ms=None, alias="", descr=""):
        """ PWM input initialization.
            
            Parameters:
                context           - parent context
                base_path         - base path to PWM channel subsystem
                sig_channel       - fiu channel of the PWM channel
                max_voltage       - maximum allowed physical voltage in V of the channel
                max_freq          - (opt) maximum frequency of the PWM channel
                                    defaults to "Inf"
                abs_tol_freq      - (opt) absolute frequency tolerance
                                    defaults to 0.1Hz
                rel_tol_freq      - (opt) relative frequency tolerance
                                    defaults to 0.05 = 5%
                abs_tol_dc        - (opt) absolute duty cycle tolerance
                                    defaults to 5%
                threshold_voltage - (opt) voltage threshold in V for high/low detection
                                    defaults to 2.5V
                min_freq          - (opt) minimum frequency in Hz of the PWM channel
                                    defaults to 0Hz
                preconditions     - (opt) preconditions that have to be set before
                                    the device can be checked.
                                    default is None
                                    preconditions have to be specified as a list 
                                    of dictionaries where each list element specifies one precondition.
                                    Each dictionary consists of the keys "device"
                                    and "value", where "value" specifies the value to
                                    be set for the "device". 
                                    Alternatively, functions can be called. In this case,
                                    the keys "func", "set_func" or "reset_func" and optional arguments
                                    have to be part of the dictionary. The function
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    channel stimulation and channel check
                                    defaults to 100ms
                alias             - (opt) channel alias/name, defaults to the
                                    last (non-default) entry in identifier
                                    (i.e. signal model path)
                descr             - (opt) channel description (e.g. used in report entries)
        
        """
        _PwmInput.__init__(self, context, base_path, sig_channel, max_voltage,
                           max_freq, abs_tol_freq, rel_tol_freq, abs_tol_dc,
                           threshold_voltage, min_freq, preconditions,
                           wait_time_ms, alias, descr)
                           

# #############################################################################
# PWM channel - Base class for PWM output channels
# #############################################################################
class PwmOutput(_PwmOutput):
    """ Base PWM output container for a testable PWM output
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, sig_channel, max_freq=None,
                 abs_tol_freq=0.1, rel_tol_freq=0.01, abs_tol_dc = 5,
                 threshold_voltage=None, min_freq=None, preconditions=None,
                 wait_time_ms=None, alias="", descr=""):
        """ PWM output initialization.
            
            Parameters:
                context           - parent context
                base_path         - base path to PWM channel subsystem
                sig_channel       - fiu channel of the PWM channel
                max_freq          - (opt) maximum frequency of the PWM channel
                                    defaults to "Inf"
                abs_tol_freq      - (opt) absolute frequency tolerance
                                    defaults to 0.1Hz
                rel_tol_freq      - (opt) relative frequency tolerance
                                    defaults to 0.01 = 1%
                abs_tol_dc        - (opt) absolute duty cycle tolerance
                                    defaults to 5%
                threshold_voltage - (opt) voltage threshold in V for high/low detection
                                    defaults to 2.5V
                min_freq          - (opt) minimum frequency in Hz of the PWM channel
                                    defaults to 0Hz
                preconditions     - (opt) preconditions that have to be set before
                                    the device can be checked.
                                    default is None
                                    preconditions have to be specified as a list 
                                    of dictionaries where each list element specifies one precondition.
                                    Each dictionary consists of the keys "device"
                                    and "value", where "value" specifies the value to
                                    be set for the "device". 
                                    Alternatively, functions can be called. In this case,
                                    the keys "func", "set_func" or "reset_func" and optional arguments
                                    have to be part of the dictionary. The function
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    channel stimulation and channel check
                                    defaults to 100ms
                alias             - (opt) channel alias/name, defaults to the
                                    last (non-default) entry in identifier
                                    (i.e. signal model path)
                descr             - (opt) channel description (e.g. used in report entries)
        
        """
        _PwmOutput.__init__(self, context, base_path, sig_channel,
                            max_freq, abs_tol_freq, rel_tol_freq, abs_tol_dc,
                            threshold_voltage, min_freq, preconditions,
                            wait_time_ms, alias, descr)
                            

# #############################################################################
# Switch - Base class for switches
# #############################################################################
class Switch(_Switch):
    """ Base switch container for a testable switch
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, identifier, on_channel,
                 off_channel = None, preconditions=None,
                 wait_time_ms=100, alias="", descr=""):
        """ Switch initialization.
            
            Parameters:
                context       - parent context
                identifier    - variable identifier: model path, CAN signal or C2DOutput 
                                should be C2DOuput, DigOut or CAN signal of
                                digital output any time
                on_channel    - fiu channel for on-state of the switch device
                off_channel   - (opt) fiu channel for off-state of the switch device
                preconditions - (opt) preconditions that have to be set before
                                the device can be checked.
                                default is None
                                preconditions have to be specified as a list 
                                of dictionaries where each list element specifies one precondition.
                                Each dictionary consists of the keys "device"
                                and "value", where "value" specifies the value to
                                be set for the "device". 
                                Alternatively, functions can be called. In this case,
                                the keys "func", "set_func" or "reset_func" and optional arguments
                                have to be part of the dictionary. The function
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
                alias         - (opt) channel alias/name, defaults to the
                                last (non-default) entry in identifier
                                (i.e. signal model path)
                descr         - (opt) channel description (e.g. used in report entries)
        
        """
        _Switch.__init__(self, context, identifier, on_channel, off_channel,
                         preconditions, wait_time_ms, alias, descr)
    
    # #########################################################################
    def set(self, value, *args, **kwargs):
        """ Function to set the switch according to its type
            
            Parameters:
                value - value to set
            
            Note:
                Any additional parameters will be forwarded to the write
                implementation of the variable instance
            
            Returns the original value before the set operation occurred.
        """
        return _Switch.set(self, value, *args, **kwargs)
    
    # #########################################################################
    def setState(self, state):
        """ Function to set the switch according to its type
            
            Parameters:
                state - named state to set
            
            Returns the previously set state (or the raw value if no matching 
            state was available).
        """
        # Set switch state
        return _Switch.setState(self, state)
    
    # #########################################################################
    def reset(self):
        """ Function to reset the switch according to its type to its 
            initial value.
            
            Parameters:
                None
            
            Returns the original value (which may be None if the variable has
            not been set before)
        """
        return _Switch.reset(self)
        

# #############################################################################
# iCAN2DIG Output - Base class for iCAN2DIG outputs
# #############################################################################
class C2DOutput(_C2DOutput):
    """ Base iCAN2DIG output container for a testable iCAN2DIG output
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path,
                 num_c2d_card, num_output, alias=""):
        """ iCAN2DIG output initialization.
            
            Parameters:
                context          - parent context
                base_path        - base path of the iCAN2DIG in the model
                                   (all required variables will be derived 
                                   from this path)
                num_c2d_card     - number of the iCAN2DIG
                num_output       - output number of the specified iCAN2DIG
                alias            - (opt) output alias/name
                                   defaults to the iCAN2DIG and output number
        """
        _C2DOutput.__init__(
            self, context, base_path, num_c2d_card, num_output, alias)
    
    # #########################################################################
    def setOutput(self):
        """ Function to set the output of the iCAN2DIG
            
            Parameter:
                None
            
            Returns:
                None
        """
        return _C2DOutput.setOutput(self)
    
    # #########################################################################
    def resetOutput(self):
        """ Function to reset the output of the iCAN2DIG
            
            Parameter:
                None
            
            Returns:
                None
        """
        return _C2DOutput.resetOutput(self)

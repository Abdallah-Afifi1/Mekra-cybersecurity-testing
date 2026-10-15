#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : components.py
# Package : ttk_selftest.hil_devices
# Task    : Wrapper classes for several hil component descriptions
# Python  : 3.8+
# Type    : Base implementation
# Copyright 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.  | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 10.09.2018 | C.Haas     | initial (derived from 
#                                  | selftest_hil_devices_base)
# 1.1.0  | 11.03.2022 | C.Haas     | Refixed review findings
# 2.0.0  | 09.01.2024 | M. Jellen  | Python3 update
#******************************************************************************
"""
@package ttk_selftest.hil_devices.components
Wrapper classes for several hil component descriptions.

"""
# Imports
from ttk_selftest.hil_devices._components import PowerSupply as _PowerSupply  # @UnresolvedImport (compiled extension)
from ttk_selftest.hil_devices._components import Load        as _Load         # @UnresolvedImport (compiled extension)
from ttk_selftest.hil_devices._components import iDigiRes    as _iDigiRes     # @UnresolvedImport (compiled extension)


# #############################################################################
# PowerSupply - Base class for Power Supplies
# #############################################################################
class PowerSupply(_PowerSupply):
    """ Base power supply container for a testable power supply
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, power_channel, gnd_channel,
                 base_path_cv_prog, base_path_cc_prog,
                 base_path_cv_mon, base_path_cc_mon,
                 max_voltage, max_current,
                 abs_tol_v=0.05, rel_tol_v=0.01, abs_tol_c=0.05, rel_tol_c=0.01,
                 preconditions=None, wait_time_ms=100, load_wait_time_ms=100,
                 alias="", model = "", descr=""):
        """ Power Supply initialization.
            
            Parameters:
                context           - parent context
                power_channel     - fiu channel of the positive output of the
                                    power supply
                gnd_channel       - ground device of the power supply
                                    equals negative output of the power supply
                                    must be a GND device
                base_path_cv_prog - base path to analog channel subsystem used
                                    for voltage programming
                base_path_cc_prog - base path to analog channel subsystem used
                                    for current programming
                base_path_cv_mon  - base path to analog channel subsystem used
                                    for voltage monitoring
                base_path_cc_mon  - base path to analog channel subsystem used
                                    for current monitoring
                max_voltage       - maximum output voltage of the power supply
                max_current       - maximum output current of the power supply
                abs_tol_v         - absolute tolerance for voltage programming/
                                    monitoring, defaults to 0.05 (V)
                rel_tol_v         - relative tolerance for voltage programming/
                                    monitoring, defaults to 0.01 = 1%
                abs_tol_c         - absolute tolerance for current programming/
                                    monitoring, defaults to 0.05 (A)
                rel_tol_c         - relative tolerance for current programming/
                                    monitoring, defaults to 0.01 = 1%
                preconditions     - (opt) preconditions that have to be set before
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    power supply stimulation and check
                                    defaults to 100ms
                load_wait_time_ms - (opt) waiting time after load stimulation
                                    necessary to unload inductive loads
                                    defaults to 100ms
                alias             - (opt) power supply alias/name
                                    defaults to ""
                model             - (opt) power supply model
                                    defaults to ""
                descr             - (opt) power supply description (e.g. used in report entries)
                                    defaults to ""
        
        """
        _PowerSupply.__init__(self, context, power_channel, gnd_channel,
                              base_path_cv_prog, base_path_cc_prog,
                              base_path_cv_mon, base_path_cc_mon,
                              max_voltage, max_current,
                              abs_tol_v, rel_tol_v, abs_tol_c, rel_tol_c,
                              preconditions, wait_time_ms, load_wait_time_ms,
                              alias, model, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for the Power Supply: alias, model, FIU channels, 
            minimum and maximum value plus description, if available.  
            
            Returns a formatted string.
        """
        return _PowerSupply.info(self)
    
    # #########################################################################
    def setVoltage(self, voltage):
        """ Function to set the target voltage of the power supply
            
            Parameters:
                voltage - target voltage in V to be set
            
            Returns the original voltage before the set operation occurred.
        """
        return _PowerSupply.setVoltage(self, voltage)
    
    # #########################################################################
    def setCurrent(self, current):
        """ Function to set the current limit of the power supply
            
            Parameters:
                current - current limit in A to be set
            
            Returns the original current limit before the set operation occurred.
        """
        return _PowerSupply.setCurrent(self, current)
        

# #############################################################################
# Load - Base class for loads
# #############################################################################
class Load(_Load):
    """ Base load container for a testable load and relevant associated 
        variables/values.
    """
    # #########################################################################
    def __init__(self, context, hs_channel, ls_channel,
                 max_voltage, max_current, load_resistance=None,
                 base_path_v_mon=None, gnd_v_mon=None,
                 abs_tol_v=0.1, rel_tol_v=0.1,
                 base_path_hs_c_mon=None, base_path_ls_c_mon=None, 
                 max_voltage_c=None, abs_tol_c=0.1, rel_tol_c=0.1, avg_c=0,
                 base_path_hs_pwm_mon=None, base_path_ls_pwm_mon=None,
                 max_pwm_freq=100000, min_pwm_freq=0,
                 base_path_hs_dig_mon=None, base_path_ls_dig_mon=None,
                 max_on_rate=100, preconditions=None, wait_time_ms=100,
                 alias="", model = "", descr=""):
        """ Load initialization.
            
            Parameters:
                context              - parent context
                hs_channel           - fiu channel of the load highside
                ls_channel           - fiu channel of the load lowside
                                       can be either GND device or FiuChannel
                max_voltage          - maximum voltage in V of the load
                max_current          - maximum current in A of the load
                load_resistance      - (opt) expected load resistance in Ohm if
                                       constant load resistance can be specified
                                       defaults to None
                base_path_v_mon      - (opt) base path to analog channel
                                       subsystem used for voltage monitoring
                                       defaults to None
                gnd_v_mon            - (opt) ground of the voltage monitoring
                                       defaults to lowside fiu channel of the load
                abs_tol_v            - (opt) absolute tolerance for voltage monitoring
                                       defaults to 0.1 (equals 100mV)
                rel_tol_v            - (opt) relative tolerance for voltage monitoring
                                       defaults to 0.1 (equals 10%)
                base_path_hs_c_mon   - (opt) base path to analog channel
                                       subsystem used for highside current monitoring
                                       defaults to None
                base_path_ls_c_mon   - (opt) base path to analog channel
                                       subsystem used for lowside current monitoring
                                       defaults to None
                max_voltage_c        - (opt) maximum voltage during test of current monitoring
                                       defaults to maximum voltage of the load
                abs_tol_c            - (opt) absolute tolerance for current monitoring
                                       defaults to 0.1 (equals 100mA)
                rel_tol_c            - (opt) relative tolerance for current monitoring
                                       defaults to 0.1 (equals 10%)
                avg_c                - (opt) averaging for current reference measurement
                                       this parameter will be used to configure the averaging
                                       of the current sensor on the iSystemReferenceCard
                                       defaults to 0
                base_path_hs_pwm_mon - (opt) base path to highside pwm channel
                                       subsystem used for highside pwm monitoring
                                       defaults to None
                base_path_ls_pwm_mon - (opt) base path to lowside pwm channel
                                       subsystem used for lowside pwm monitoring
                                       defaults to None
                max_pwm_freq         - (opt) maximum frequency in Hz of the PWM channel
                                       limited by measurement hardware to 100kHz
                                       defaults to 100kHz
                min_pwm_freq         - (opt) minimum frequency in Hz of the PWM channel
                                       defaults to 0Hz
                base_path_hs_dig_mon - (opt) base path to highside digital channel
                                       subsystem used for highside state monitoring
                                       defaults to None
                base_path_ls_dig_mon - (opt) base path to lowside digital channel
                                       subsystem used for lowside state monitoring
                                       defaults to None
                max_on_rate          - (opt) maximum "on"-rate of the load in percent
                                       defaults to 100 (%)
                preconditions        - (opt) preconditions that have to be set before
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
                wait_time_ms         - (opt) waiting time in milliseconds between
                                       stimulation and check
                                       defaults to 100ms
                alias                - (opt) load alias/name
                                       defaults to ""
                model                - (opt) load model
                                       defaults to ""
                descr                - (opt) load description
                                       (e.g. used in report entries)
                                       defaults to ""
        
        """
        _Load.__init__(self, context, hs_channel, ls_channel,
                       max_voltage, max_current, load_resistance,
                       base_path_v_mon, gnd_v_mon,
                       abs_tol_v, rel_tol_v,
                       base_path_hs_c_mon, base_path_ls_c_mon, max_voltage_c,
                       abs_tol_c, rel_tol_c, avg_c,
                       base_path_hs_pwm_mon, base_path_ls_pwm_mon,
                       max_pwm_freq, min_pwm_freq,
                       base_path_hs_dig_mon, base_path_ls_dig_mon,
                       max_on_rate, preconditions,
                       wait_time_ms, alias, model, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for the load: alias, FIU channels, 
            load resistance, maximum voltage, maximum current
            plus description, if available.  
            
            Returns a formatted string.
        """
        return _Load.info(self)
        

# #############################################################################
# iDigiRes - Base class for iDigiRes
# #############################################################################
class iDigiRes(_iDigiRes):
    """ Base iDigiRes container for a testable iDigiRes device
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, base_resistance, num_resistances,
                 hs_channel=None, ls_channel=None, resistors=None, 
                 min_power=0.25, resistor_powers=None,
                 preconditions=None, wait_time_ms=100, alias="", descr=""):
        """ iDigiRes initialization.
            
            Parameters:
                context           - parent context
                base_path         - base path to the iDigiRes in the model
                base_resistance   - base resistance value in Ohm that is 
                                    fitted on the iDigiRes
                num_resistances   - number of resistances fitted on the iDigiRes
                hs_channel        - (opt) highside (first) fiu channel of the iDigiRes
                                    defaults to None
                ls_channel        - (opt) lowside (second) fiu channel of the iDigiRes
                                    defaults to None
                resistors         - (opt) list of resistors fitted on the iDigiRes
                                    Length of the list must be equal to the
                                    specified number of resistances. The values
                                    have to be specified in increasing order,
                                    beginning with the smallest and
                                    ending with the largest resistor. If the
                                    parameter is not specified, the resistors
                                    will be calculated according to
                                    base_resistance and num_resistances.
                min_power         - (opt) minimum power value of all resistances
                                    defaults to 0.25 (W)
                resistor_powers   - (opt) list of resistor powers
                                    Length of the list must be equal to the
                                    specified number of resistances. The values
                                    have to be ordered according to the power of
                                    R, 2R, 4R... If the parameter is not specified,
                                    the values of all resistors will be set to
                                    the parameter min_power.
                preconditions     - (opt) preconditions that have to be set before
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
                wait_time_ms      - (opt) waiting time in milliseconds between
                                    channel stimulation and channel check
                                    defaults to 100ms
                alias             - (opt) channel alias/name, defaults to the
                                    base path of the iDigiRes in the model
                descr             - (opt) channel description (e.g. used in report entries)
                                    defaults to ""
        
        """
        return _iDigiRes.__init__(self, context, base_path, base_resistance,
                                  num_resistances, hs_channel, ls_channel,
                                  resistors, min_power, resistor_powers,
                                  preconditions, wait_time_ms, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this iDigiResl: alias, FIU channel(s),
            base resistance, number of resistance and minimum power plus
            description, if available.  
            
            Returns a formatted string.
        """
        return _iDigiRes.info(self)

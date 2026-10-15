#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : bus_devices.py
# Package : ttk_selftest
# Task    : Wrapper classes for bus device descriptions
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
@package ttk_selftest.hil_devices.bus_devices
Interface wrapper for bus device descriptions.

"""
# Imports
from ttk_selftest.hil_devices._bus_devices import CanChannel as _CanChannel  # @UnresolvedImport (compiled extension)


# #############################################################################
# CAN channel - Base class for CAN channels
# #############################################################################
class CanChannel(_CanChannel):
    """ Base CAN channel container for a testable CAN channel
        and relevant associated variables/values.
    """
    # #########################################################################
    def __init__(self, context, base_path, test_msg_name, test_msg_id,
                 test_msg_length, fiu_channel, bitrate, termination,
                 preconditions=None, wait_time_ms=None, alias="", descr=""):
        """ CAN channel initialization.
            
            Parameters:
                context           - parent context
                base_path         - base path to the CAN channel in the model
                test_msg_name     - name of the CAN message that will be used
                                    for the test of the channel
                test_msg_id       - ID of the CAN message to be used for the
                                    test of the channel
                test_msg_length   - length in byte of the CAN message to be
                                    used for the test of the channel
                fiu_channel       - fiu channel of the CAN channel
                bitrate           - bitrate of the CAN channel in kBit/s
                termination       - flag to specify the hardware termination of the channel
                                    TRUE: Channel is already fully terminated
                                    FALSE: Channel is not fully terminated
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
                                    base path of the CAN channel in the model
                descr             - (opt) channel description (e.g. used in report entries)
        
        """
        _CanChannel.__init__(self, context, base_path, test_msg_name, test_msg_id,
                             test_msg_length, fiu_channel, bitrate, termination,
                             preconditions, wait_time_ms, alias, descr)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this CAN channel: alias, FIU channel, 
            bitrate, and termination plus description, if available.  
            
            Returns a formatted string.
        """
        return _CanChannel.info(self)

#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : selftest_devices.py
# Package : ttk_selftest
# Task    : Wrapper classes for selftest device descriptions
# Python  : 3.8+
# Type    : Base implementation

# Author  : C.Haas
# Date    : 25.04.2019
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
@package ttk_selftest.hil_devices.selftest_devices
Interface wrapper for selftest device descriptions.

"""
# Imports
from ttk_selftest.hil_devices._selftest_devices import SRC as _SRC # @UnresolvedImport (compiled extension)


# #############################################################################
# iSystemReferenceCard device - Base class for iSRC
# #############################################################################
class SRC(_SRC):
    """ Base iSystemReferenceCard (iSRC) container
    """
    def __init__(self, context, base_path, node_id, psu, alias="", descr=""):
        """ iSystemReferenceCard initialization.
            
            Parameters:
                context   - parent context
                base_path - base path of CAN signals to communicate with iSRC
                node_id   - node id of the iSRC
                psu       - power supply unit, which is connected to the iSRC
                alias     - (opt) device alias/name,
                            defaults to "iSRC"
                descr     - (opt) device description
                            defaults to ""
        """
        _SRC.__init__(self, context, base_path, node_id, psu, alias, descr)
    
    # #########################################################################
    def setModeId(self, mode_id):
        """ Function to set mode of iSRC according to supplied mode id
            
            Parameters:
                mode_id - target mode id of iSRC
            
            Returns an info string.
        """
        return _SRC.setModeId(self, mode_id)
    
    # #########################################################################
    def setMode(self, mode):
        """ Function to set mode of iSRC 
            
            Parameters:
                mode - target mode of iSRC specified as 
                       instance of class _SrcMode
            
            Returns an info string.
        """
        return _SRC.setMode(self, mode)
    
    # #########################################################################
    def resetMode(self):
        """ Function to set iSRC in standby mode
            
            Parameters:
               None
            
            Returns an info string.
        """
        return _SRC.resetMode(self)
    
    # #########################################################################
    def hardReset(self):
        """ Function to perform a hard reset of the iSRC
            
            Parameters:
               None
            
            Returns a single [<info string>, <verdict>] test result entry.
        """
        return _SRC.hardReset(self)
    
    # #########################################################################
    def reqData(self, cycle_time = 0):
        """ Function to request data from iSRC and check the reception of the
            response message
            
            Parameters:
                cycle_time - (opt) cycle time in ms of measurement data 
                             provided by iSRC on CAN bus
                             default is one snapshot of measurement data
            
            Returns a single [<info string>, <verdict>] test result entry.
        """
        return _SRC.reqData(self, cycle_time)
    
    # #########################################################################
    def setAlert(self, **kwargs):
        """ Function to set the alert limit of iSRC for voltage and current
            measurements
            
            Parameter:
                kwargs - key words can be any of max_voltage,
                         current_limit_low, current_limit_mid or current_limit_high.
                         The corresponding value specifies the new limitation 
                         to be set for the associated measurement.
                         Unspecified limitations will be left unchanged.
                         Unit are:
                             max_voltage       : V
                             current_limit_low : A
                             current_limit_mid : A
                             current_limit_high: A
            
            Returns a single [<info string>, <verdict>] test result entry. 
        """
        return _SRC.setAlert(self, **kwargs)
    
    # #########################################################################
    def resetAlert(self):
        """ Function to reset the alert limit of iSRC for voltage and current
            measurements to their default values
            
            Parameter:
                None
            
            Returns a single [<info string>, <verdict>] test result entry. 
        """
        return _SRC.resetAlert(self)
    
    # #########################################################################
    def setTimeLimit(self, current_limit, time_limit):
        """ Function to configure the timebased limit of the iSRC.
            The iSRC will interrupt the connection if the specified current
            will be exceeded for the specified time.
            
            Parameter:
                current_limit - current limit in mA
                time_limit    - time limit in ms
            
            Returns a single [<info string>, <verdict>] test result entry. 
        """
        return _SRC.setTimeLimit(self, current_limit, time_limit)
    
    # #########################################################################
    def setSensorConfig(self, **kwargs):
        """ Function to set the sensor configuration of iSRC for voltage and 
            current measurements
            
            Parameter:
                kwargs - key words can be any of averaging_mode,
                         bus_vol_conv_time or shunt_vol_conv_time.
                         The supplied value must be valid and within the 
                         specified lookup tables.
            
            Returns a single [<info string>, <verdict>] test result entry. 
        """
        return _SRC.setSensorConfig(self, **kwargs)
    
    # #########################################################################
    def resetSensorConfig(self):
        """ Function to reset the sensor configuration of iSRC for voltage and 
            current measurements to their default values
            
            Parameter:
                None
            
            Returns a single [<info string>, <verdict>] test result entry.
        """
        return _SRC.resetSensorConfig(self)
    
    # #########################################################################
    def setVoltage(self, voltage):
        """ Function to set the output voltage of the iSRC.
            
            Parameter:
                voltage - target voltage in mV
            
            Returns a single [<info string>, <verdict>] test result entry. 
        """
        return _SRC.setVoltage(self, voltage)
    
    # #########################################################################
    def setPWM(self, frequency, duty_cycle):
        """ Function to set the PWM output of the iSRC.
            
            Parameter:
                frequency  - target frequency  in Hz
                duty_cycle - target duty cycle in % High
            
            Returns a single [<info string>, <verdict>] test result entry. 
        """
        return _SRC.setPWM(self, frequency, duty_cycle)
    
    # #########################################################################
    def getCurrentCheckVars(self):
        """ Function to get the current measurement variable and timestamp
            variable of the associated CAN message
            
            Parameters:
                None
            
            Returns a list [current_var, timestamp_var] consisting of the
            current measurement and timestamp variable of the iSRC if current
            measurement is possible for the recent mode. Otherwise both
            variables will be set None.
        """
        return _SRC.getCurrentCheckVars(self)
    
    # #########################################################################
    def getVoltageCheckVars(self):
        """ Function to get the voltage measurement variable and timestamp
            variable of the associated CAN message
            
            Parameters:
                None
            
            Returns a list [voltage_var, timestamp_var] consisting of the 
            voltage measurement and timestamp variable of the iSRC if voltage
            measurement is possible for the recent mode. Otherwise None will be
            returned.
        """
        return _SRC.getVoltageCheckVars(self)
    
    # #########################################################################
    def getPwmCheckVars(self):
        """ Function to get the PWM measurement variables and timestamp
            variable of the associated CAN message
            
            Parameters:
                None
            
            Returns a list [freq_var, dc_var, status_var, timestamp_var] 
            consisting of the PWM measurement and timestamp variable of the iSRC.
        """
        return _SRC.getPwmCheckVars(self)
    
    # #########################################################################
    def getCanCheckVars(self):
        """ Function to get the variables for CAN bus test, which are
                - message ID of received CAN message
                - message length of received CAN message
                - timestamp of iSRCs response message
            
            Parameters:
                None
            
            Returns a list [can_message_id, can_message_length, timestamp_var]
            consisting of the variables of the received message and the timestamp
            variable of the iSRC.
        """
        return _SRC.getCanCheckVars(self)
    
    # #########################################################################
    def getVoltageReferenceModes(self):
        """ Function to get the voltage reference modes
            
            Parameters:
                None
            
            Returns a list of all voltage reference (in order of ascending
            reference voltages)
        """
        return _SRC.getVoltageReferenceModes(self)
    
    # #########################################################################
    def getResistance(self, measurement_mode="Highside",
                      current_limit=1, voltage=None):
        """ Function to determine the wire/connection resistance.
            The resistance will be calculated as devision of voltage and
            current measured by the iSRC.
            For this, the PSU connected to the iSRC will be used as supply.
            Depending on the desired measurement mode (see parameter),
            the iSRC will be set to Highside measurement or Lowside measurement.
            Preconditions:
                1. In Highside measurement mode:
                   The wire/connection to be measured has to be switched
                   between EI1 and EI2. Moreover, the PSU ground has to be
                   connected to EI2. If the wire/connection to be measured
                   already has a connection to PSU ground, the connection to 
                   EI1 is sufficient.
                2. In Lowside measurement mode:
                   The wire/connection to be measurend has to be switched 
                   between EI2 and EI1. Moreover, the PSU output has to be
                   connected to EI2. If the wire/connection to be measured
                   already has a connection to PSU output, the connection to 
                   EI1 is sufficient.
                   As the supply voltage cannot be measured in Lowside
                   measurement mode, it has to be provided as parameter.
            Note:
                The calculated resistance may be influenced by connections of
                the test connection to the ground of the PSU in the HIL system.
                On one hand, this may leed to wrong resistance values.
                On the other hand, this can be used to measure connection
                resistance to the PSU ground.
            
            Parameters:
                measurement_mode - (opt) mode of the iSRC measurement that will
                                   be used to determine the resistance, can be
                                   "Highside" or "Lowside"
                                   defaults to "Highside"
                current_limit    - (opt) maximum allowed current while checking
                                   the resistance in A, defaults to 1A
                voltage          - (opt) voltage in V used for resistance calculation
                                   Parameter has to be given for Lowside measurement
                                   mode, defaults to measurement of the iSRC
                                   
            
            Returns a list [info, resistance] where
                "info" is a list of test result entrys and
                "resistance" is the wire/connection resistance in Ohm or None in
                case of missing response from iSRC
        """
        return _SRC.getResistance(self, measurement_mode, current_limit, voltage)
    
    # #########################################################################
    def getStatus(self):
        """ Function to get an updated status of the iSRC.
            
            Parameters:
                None
            
            Returns a single [<status string>, <verdict>] test result entry or
            None if no updated status message has been received. 
        """
        return _SRC.getStatus(self)
    
    # #########################################################################
    def configureCAN(self, bitrate, termination):
        """ Function to configure the second CAN channel of the iSRC.
            
            Parameter:
                bitrate     - target bitrate in kBit/s
                termination - flag to enable(True) or disable(False) the
                              120R termination of the second CAN channel
                              of the iSRC
            
            Returns a single [<info string>, <verdict>] test result entry. 
        """
        return _SRC.configureCAN(self, bitrate, termination)

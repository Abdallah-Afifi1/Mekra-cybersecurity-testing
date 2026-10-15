#******************************************************************************
# -*- coding: utf-8 -*-
# 
# File    : psu_ngp800.py
# Package : tools.rohde_schwarz
# Task    : Access to Rohde&Schwarz NGP800-series power supplies via VISA.
#           Provides TTk variable abstractions for outputs/measurements.
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 08.05.2025 | Tremmel   | initial, VISA identifiers based on previous 
#                                 | Rode_Schwarz_NGP822 module v1.2
# 1.1.0  | 19.05.2025 | Tremmel   | extended measurement VisaVars, added scpi 
#                                 | command error checks
# 1.2.0  | 23.06.2025 | Tremmel   | initial proof-of-concept for defining 
#                                 | arbitrary waveforms
#******************************************************************************
"""
@package tools.rohde_schwarz.psu_ngp822
Access to Rohde&Schwarz NGP800-series power supplies via VISA interface.
Specifically intended for NGP824 (4 output channels, 800W, 0..64V, 0..10A).
Provides TTk variable abstractions for outputs/measurements.

Requires package PyVisa
"""
import time
import datetime

import pyvisa

from tools.visa_variable import VisaVar, checkCommandErrors, checkedQuery, ScpiCommandError


# #############################################################################
# R&S NGP800 Series:
# 
#     Model     | outputs | max output |    voltage    |    current    
#   ––––––––––––+–––––––––+––––––––––––+–––––––––––––––+–––––––––––––––
#     NGP802    |    2    |    400 W   |     0..32 V   |    0..20A     
#     NGP804    |    4    |    800 W   |     0..32 V   |    0..20 A    
#     NGP814    |    4    |    800 W   | CH1+2 0..32 V | CH1+2 0..20 A 
#               |         |            | CH3+4 0..64 V | CH3+4 0..10 A 
#     NGP822    |    2    |    400 W   |     0..64 V   |    0..10 A    
#     NGP824    |    4    |    800 W   |     0..64 V   |    0..10 A     
#
# https://www.rohde-schwarz.com/de/produkte/messtechnik/dc-netzgeraete/rs-ngp800-netzgeraeteserie_63493-670592.html
# #############################################################################


       
        
        
#******************************************************************************
class NGP800Series:
    """ Access Rohde&Schwarz NGP800 series power supplies. """
    
    # #########################################################################
    def __init__(self, visa_address='TCPIP0::10.104.3.10::inst0::INSTR',
                       query_delay_s=None):
        """ Parameters:
                visa_address  - visa address string of device, e.g. 
                                  "TCPIP0::192.168.10.10::inst0::INSTR" 
                                  or a shortened
                                  "TCPIP0::10.104.3.10"
                                  
                query_delay_s - default delay for visa queries in [s], i.e.
                                the delay between write and read operations.
                                None: use default pyvisa resource delay 
                                See pyvisa.resources.Resource.query_delay
                                Note that Resource.query_delay defaults to 0.0
        """
        self._dev = None 
        self._address = str(visa_address)

        self._rm = pyvisa.ResourceManager()

        self.res_id = ""
        self.manufacturer = ""
        self.model = ""
        
        
        try:
            self._dev = self._rm.open_resource(self._address)
            if query_delay_s is not None:
                self._dev.query_delay = float(max(0.0, query_delay_s))
            
            self.res_id = self._dev.query('*IDN?', delay=0.0)
            # scpi99
            # "IEEE 488.2 is purposefully vague about the content of each of the 
            #  four fields in the response syntax. SCPI adds no further 
            #  requirement, but here are some suggestions:
            #
            #  Field 1, the Manufacturer field, should be identical for all 
            #           devices produced by a single company.
            #  Field 2, the Model field, should NOT contain the word “MODEL”.
            #  Field 4, the Firmware level field, should contain information
            #           about all separately revisable subsystems. 
            #           This information can be contained in single or multiple
            #           revision codes."
            id_parts = self.res_id.strip().split(",", maxsplit=2)
            if len(id_parts) >= 2:
                self.manufacturer = id_parts[0]
                self.model        = id_parts[1].upper()
                

            print("# #############################################################")
            print(f"# Connected to {self._address}:")
            print(f"# Device: {' '.join(id_parts[:-1])}")
            print(f"#         {id_parts[-1]}")
            print("# #############################################################")
            
        except pyvisa.VisaIOError as ex:
            print(f"> {self.__class__.__name__}: Failed to connect to {self._address!r}:")
            print(f"> {ex.description}\n")
            print("-- Available Resources: ---------------------------------------")
            for res in self._rm.list_resources():
                if res.startswith("ASRL"):
                    continue # all serial interfaces get added by default
                print(f"{res}")
                with self._rm.open_resource(res) as inst: 
                    print(f"↪ {inst.query('*IDN?').strip()}\n")
            raise
        
        # VisaVars ~~~~~~~~~~~~~~~~~~~~~--------------------------------------
        
        # Voltages ---
        # self.voltage_preset_ch1 = VisaVar(self._dev, get_cmd="INST OUT1;:VOLT?", set_cmd="INST OUT1;:VOLT {value:f}", alias="voltage_preset_ch1", unit="V", fmt="flt3")
        # self.voltage_preset_ch2 = VisaVar(self._dev, get_cmd="INST OUT1;:VOLT?", set_cmd="INST OUT1;:VOLT {value:f}", alias="voltage_preset_ch2", unit="V", fmt="flt3")
        # self.voltage_preset_ch3 = VisaVar(self._dev, get_cmd="INST OUT1;:VOLT?", set_cmd="INST OUT1;:VOLT {value:f}", alias="voltage_preset_ch3", unit="V", fmt="flt3")
        # self.voltage_preset_ch4 = VisaVar(self._dev, get_cmd="INST OUT1;:VOLT?", set_cmd="INST OUT1;:VOLT {value:f}", alias="voltage_preset_ch4", unit="V", fmt="flt3")        

        # Set/query voltage value of the selected channel
        # [SOURce:]VOLTage[:LEVel][:IMMediate][:AMPLitude] <arg0>[, <Channel list>]
        # [SOURce:]VOLTage[:LEVel][:IMMediate][:AMPLitude]? [<Channel list>]
        self.voltage_preset_ch1 = VisaVar(self._dev, get_cmd="VOLTage? (@1)", set_cmd="VOLTage {value:f}, (@1)", alias="voltage_preset_ch1", unit="V", fmt="flt3")
        self.voltage_preset_ch2 = VisaVar(self._dev, get_cmd="VOLTage? (@2)", set_cmd="VOLTage {value:f}, (@2)", alias="voltage_preset_ch2", unit="V", fmt="flt3")
        self.voltage_preset_ch3 = VisaVar(self._dev, get_cmd="VOLTage? (@3)", set_cmd="VOLTage {value:f}, (@3)", alias="voltage_preset_ch3", unit="V", fmt="flt3")
        self.voltage_preset_ch4 = VisaVar(self._dev, get_cmd="VOLTage? (@4)", set_cmd="VOLTage {value:f}, (@4)", alias="voltage_preset_ch4", unit="V", fmt="flt3")
        
        # MEASure[:SCALar][:VOLTage][:DC]? [<Channel list>]
        # Query currently measured voltage of the selected channel.
        self.voltage_ch1 = VisaVar(self._dev, get_cmd="MEASure:VOLTage? (@1)", alias="voltage_ch1", unit="V", fmt="flt3")
        self.voltage_ch2 = VisaVar(self._dev, get_cmd="MEASure:VOLTage? (@2)", alias="voltage_ch2", unit="V", fmt="flt3")
        self.voltage_ch3 = VisaVar(self._dev, get_cmd="MEASure:VOLTage? (@3)", alias="voltage_ch3", unit="V", fmt="flt3")
        self.voltage_ch4 = VisaVar(self._dev, get_cmd="MEASure:VOLTage? (@4)", alias="voltage_ch4", unit="V", fmt="flt3")

        self.voltage_ch1_min = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MIN? (@1)", alias="voltage_ch1_min", unit="V", fmt="flt3")
        self.voltage_ch2_min = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MIN? (@2)", alias="voltage_ch2_min", unit="V", fmt="flt3")
        self.voltage_ch3_min = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MIN? (@3)", alias="voltage_ch3_min", unit="V", fmt="flt3")
        self.voltage_ch4_min = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MIN? (@4)", alias="voltage_ch4_min", unit="V", fmt="flt3")
        self.voltage_ch1_avg = VisaVar(self._dev, get_cmd="MEASure:VOLTage:AVG? (@1)", alias="voltage_ch1_avg", unit="V", fmt="flt3")
        self.voltage_ch2_avg = VisaVar(self._dev, get_cmd="MEASure:VOLTage:AVG? (@2)", alias="voltage_ch2_avg", unit="V", fmt="flt3")
        self.voltage_ch3_avg = VisaVar(self._dev, get_cmd="MEASure:VOLTage:AVG? (@3)", alias="voltage_ch3_avg", unit="V", fmt="flt3")
        self.voltage_ch4_avg = VisaVar(self._dev, get_cmd="MEASure:VOLTage:AVG? (@4)", alias="voltage_ch4_avg", unit="V", fmt="flt3")
        self.voltage_ch1_max = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MAX? (@1)", alias="voltage_ch1_max", unit="V", fmt="flt3")
        self.voltage_ch2_max = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MAX? (@2)", alias="voltage_ch2_max", unit="V", fmt="flt3")
        self.voltage_ch3_max = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MAX? (@3)", alias="voltage_ch3_max", unit="V", fmt="flt3")
        self.voltage_ch4_max = VisaVar(self._dev, get_cmd="MEASure:VOLTage:MAX? (@4)", alias="voltage_ch4_max", unit="V", fmt="flt3")


        # Currents ---
        # [SOURce:]CURRent[:LEVel][:IMMediate][:AMPLitude] <arg0>[, <Channel list>]
        # [SOURce:]CURRent[:LEVel][:IMMediate][:AMPLitude]? [<Channel list>]
        # Set/query current value of the selected channel.
        self.current_preset_ch1 = VisaVar(self._dev, get_cmd="CURRent? (@1)", set_cmd="CURRent {value:f}, (@1)", alias="current_preset_ch1", unit="A", fmt="flt3")
        self.current_preset_ch2 = VisaVar(self._dev, get_cmd="CURRent? (@2)", set_cmd="CURRent {value:f}, (@2)", alias="current_preset_ch2", unit="A", fmt="flt3")
        self.current_preset_ch3 = VisaVar(self._dev, get_cmd="CURRent? (@3)", set_cmd="CURRent {value:f}, (@3)", alias="current_preset_ch3", unit="A", fmt="flt3")
        self.current_preset_ch4 = VisaVar(self._dev, get_cmd="CURRent? (@4)", set_cmd="CURRent {value:f}, (@4)", alias="current_preset_ch4", unit="A", fmt="flt3")

        # MEASure[:SCALar]:CURRent[:DC]? [<Channel list>]
        # Query currently measured current of the selected channel.
        self.current_ch1 = VisaVar(self._dev, get_cmd="MEASure:CURRent? (@1)", alias="current_ch1", unit="A", fmt="flt3")
        self.current_ch2 = VisaVar(self._dev, get_cmd="MEASure:CURRent? (@2)", alias="current_ch2", unit="A", fmt="flt3")
        self.current_ch3 = VisaVar(self._dev, get_cmd="MEASure:CURRent? (@3)", alias="current_ch3", unit="A", fmt="flt3")
        self.current_ch4 = VisaVar(self._dev, get_cmd="MEASure:CURRent? (@4)", alias="current_ch4", unit="A", fmt="flt3")

        self.current_ch1_min = VisaVar(self._dev, get_cmd="MEASure:CURRent:MIN? (@1)", alias="current_ch1_min", unit="A", fmt="flt3")
        self.current_ch2_min = VisaVar(self._dev, get_cmd="MEASure:CURRent:MIN? (@2)", alias="current_ch2_min", unit="A", fmt="flt3")
        self.current_ch3_min = VisaVar(self._dev, get_cmd="MEASure:CURRent:MIN? (@3)", alias="current_ch3_min", unit="A", fmt="flt3")
        self.current_ch4_min = VisaVar(self._dev, get_cmd="MEASure:CURRent:MIN? (@4)", alias="current_ch4_min", unit="A", fmt="flt3")
        self.current_ch1_avg = VisaVar(self._dev, get_cmd="MEASure:CURRent:AVG? (@1)", alias="current_ch1_avg", unit="A", fmt="flt3")
        self.current_ch2_avg = VisaVar(self._dev, get_cmd="MEASure:CURRent:AVG? (@2)", alias="current_ch2_avg", unit="A", fmt="flt3")
        self.current_ch3_avg = VisaVar(self._dev, get_cmd="MEASure:CURRent:AVG? (@3)", alias="current_ch3_avg", unit="A", fmt="flt3")
        self.current_ch4_avg = VisaVar(self._dev, get_cmd="MEASure:CURRent:AVG? (@4)", alias="current_ch4_avg", unit="A", fmt="flt3")
        self.current_ch1_max = VisaVar(self._dev, get_cmd="MEASure:CURRent:MAX? (@1)", alias="current_ch1_max", unit="A", fmt="flt3")
        self.current_ch2_max = VisaVar(self._dev, get_cmd="MEASure:CURRent:MAX? (@2)", alias="current_ch2_max", unit="A", fmt="flt3")
        self.current_ch3_max = VisaVar(self._dev, get_cmd="MEASure:CURRent:MAX? (@3)", alias="current_ch3_max", unit="A", fmt="flt3")
        self.current_ch4_max = VisaVar(self._dev, get_cmd="MEASure:CURRent:MAX? (@4)", alias="current_ch4_max", unit="A", fmt="flt3")

        # Power ---
        
        # MEASure[:SCALar]:POWer? [<Channel list>]
        # Query currently emitted power of the selected channel.
        self.power_ch1 = VisaVar(self._dev, get_cmd="MEASure:POWer? (@1)", alias="power_ch1", unit="W", fmt="flt3")
        self.power_ch2 = VisaVar(self._dev, get_cmd="MEASure:POWer? (@2)", alias="power_ch2", unit="W", fmt="flt3")
        self.power_ch3 = VisaVar(self._dev, get_cmd="MEASure:POWer? (@3)", alias="power_ch3", unit="W", fmt="flt3")
        self.power_ch4 = VisaVar(self._dev, get_cmd="MEASure:POWer? (@4)", alias="power_ch4", unit="W", fmt="flt3")
        
        self.power_ch1_min = VisaVar(self._dev, get_cmd="MEASure:POWer:MIN? (@1)", alias="power_ch1_min", unit="W", fmt="flt3")
        self.power_ch2_min = VisaVar(self._dev, get_cmd="MEASure:POWer:MIN? (@2)", alias="power_ch2_min", unit="W", fmt="flt3")
        self.power_ch3_min = VisaVar(self._dev, get_cmd="MEASure:POWer:MIN? (@3)", alias="power_ch3_min", unit="W", fmt="flt3")
        self.power_ch4_min = VisaVar(self._dev, get_cmd="MEASure:POWer:MIN? (@4)", alias="power_ch4_min", unit="W", fmt="flt3")
        self.power_ch1_avg = VisaVar(self._dev, get_cmd="MEASure:POWer:AVG? (@1)", alias="power_ch1_avg", unit="W", fmt="flt3")
        self.power_ch2_avg = VisaVar(self._dev, get_cmd="MEASure:POWer:AVG? (@2)", alias="power_ch2_avg", unit="W", fmt="flt3")
        self.power_ch3_avg = VisaVar(self._dev, get_cmd="MEASure:POWer:AVG? (@3)", alias="power_ch3_avg", unit="W", fmt="flt3")
        self.power_ch4_avg = VisaVar(self._dev, get_cmd="MEASure:POWer:AVG? (@4)", alias="power_ch4_avg", unit="W", fmt="flt3")
        self.power_ch1_max = VisaVar(self._dev, get_cmd="MEASure:POWer:MAX? (@1)", alias="power_ch1_max", unit="W", fmt="flt3")
        self.power_ch2_max = VisaVar(self._dev, get_cmd="MEASure:POWer:MAX? (@2)", alias="power_ch2_max", unit="W", fmt="flt3")
        self.power_ch3_max = VisaVar(self._dev, get_cmd="MEASure:POWer:MAX? (@3)", alias="power_ch3_max", unit="W", fmt="flt3")
        self.power_ch4_max = VisaVar(self._dev, get_cmd="MEASure:POWer:MAX? (@4)", alias="power_ch4_max", unit="W", fmt="flt3")

        # number of samples measured in the statistics for voltage/current/power
        self.samples_ch1 = VisaVar(self._dev, get_cmd="MEASure:STATistic:COUNt? (@1)", alias="samples_ch1")
        self.samples_ch2 = VisaVar(self._dev, get_cmd="MEASure:STATistic:COUNt? (@2)", alias="samples_ch2")
        self.samples_ch3 = VisaVar(self._dev, get_cmd="MEASure:STATistic:COUNt? (@3)", alias="samples_ch3")
        self.samples_ch4 = VisaVar(self._dev, get_cmd="MEASure:STATistic:COUNt? (@4)", alias="samples_ch4")
  


        # Temperatures ---
        # CALibration:TEMPerature?  # (channel list not available here)
        # Temperature of selected channel.
        self.temperature_ch1 = VisaVar(self._dev, get_cmd="INST OUT1;:CAL:TEMP?", alias="temperature_ch1", unit="°C", fmt="flt1")
        self.temperature_ch2 = VisaVar(self._dev, get_cmd="INST OUT2;:CAL:TEMP?", alias="temperature_ch2", unit="°C", fmt="flt1")
        self.temperature_ch3 = VisaVar(self._dev, get_cmd="INST OUT3;:CAL:TEMP?", alias="temperature_ch3", unit="°C", fmt="flt1")
        self.temperature_ch4 = VisaVar(self._dev, get_cmd="INST OUT4;:CAL:TEMP?", alias="temperature_ch4", unit="°C", fmt="flt1")
        
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Safety Limits ---
        # "With safety limits set in the instrument, the range of the output 
        #  voltage and/or output current can be limited. The safety limit prevents 
        #  inadvertently setting dangerous values for the connected DUT."
        #
        # See also channelSafetyLimitEnable() to enable limits
        # Note: if needed, there would also be lower voltage/current limits available 
        #
        # Note: Safety Limits vs OVP/OCP (overvoltage/overcurrent protection):
        # * Safety limits prevent setting of out-of-range values
        # * overvoltage/overcurrent protection disables the channel output
        #   if value is out-of-range
        
        # [SOURce:]VOLTage[:LEVel][:IMMediate]:ALIMit[:UPPer] <arg0>[, <Channel list>]
        # [SOURce:]VOLTage[:LEVel][:IMMediate]:ALIMit[:UPPer]? [<Channel list>]
        # Max value for upper safety limit.
        # Range: 0.000 to 32.050 (32V models)
        #        0.000 to 64.050 (64V models)
        # Increment:  0.001 / *RST:  32.050 or 64.050
        self.voltage_limit_ch1 = VisaVar(self._dev, get_cmd="VOLTage:ALIMit? (@1)", set_cmd="VOLTage:ALIMit {value:f}, (@1)", alias="voltage_limit_ch1", unit="V", fmt="flt3")
        self.voltage_limit_ch2 = VisaVar(self._dev, get_cmd="VOLTage:ALIMit? (@2)", set_cmd="VOLTage:ALIMit {value:f}, (@2)", alias="voltage_limit_ch2", unit="V", fmt="flt3")
        self.voltage_limit_ch3 = VisaVar(self._dev, get_cmd="VOLTage:ALIMit? (@3)", set_cmd="VOLTage:ALIMit {value:f}, (@3)", alias="voltage_limit_ch3", unit="V", fmt="flt3")
        self.voltage_limit_ch4 = VisaVar(self._dev, get_cmd="VOLTage:ALIMit? (@4)", set_cmd="VOLTage:ALIMit {value:f}, (@4)", alias="voltage_limit_ch4", unit="V", fmt="flt3")

        # [SOURce:]CURRent[:LEVel][:IMMediate]:ALIMit[:UPPer] <arg0>[, <Channel list>]
        # [SOURce:]CURRent[:LEVel][:IMMediate]:ALIMit[:UPPer]? [<Channel list>]
        # Max value for upper safety limit.
        # Range: 0.001 to 20.010. (32V models)
        #         0.001 to 10.010 (64V models)
        # Increment:  0.001 / *RST:  20.010 or 10.010
        self.current_limit_ch1 = VisaVar(self._dev, get_cmd="CURRent:ALIMit? (@1)", set_cmd="CURRent:ALIMit {value:f}, (@1)", alias="current_limit_ch1", unit="A", fmt="flt3")
        self.current_limit_ch2 = VisaVar(self._dev, get_cmd="CURRent:ALIMit? (@2)", set_cmd="CURRent:ALIMit {value:f}, (@2)", alias="current_limit_ch2", unit="A", fmt="flt3")
        self.current_limit_ch3 = VisaVar(self._dev, get_cmd="CURRent:ALIMit? (@3)", set_cmd="CURRent:ALIMit {value:f}, (@3)", alias="current_limit_ch3", unit="A", fmt="flt3")
        self.current_limit_ch4 = VisaVar(self._dev, get_cmd="CURRent:ALIMit? (@4)", set_cmd="CURRent:ALIMit {value:f}, (@4)", alias="current_limit_ch4", unit="A", fmt="flt3")

        # Overvoltage Protection ---
        # [SOURce:]VOLTage:PROTection[:STATe] on page 206
        # [SOURce:]VOLTage:PROTection:CLEar on page 206
        # [SOURce:]VOLTage:PROTection:TRIPped? on page 207
        #
        # [SOURce:]VOLTage:PROTection:LEVel <arg0>[, <Channel list>]
        # [SOURce:]VOLTage:PROTection:LEVel? [<Channel list>]

        # Maximum value for the overvoltage protection value
        # Range:  0.000 to 32.050 (32V models) or 
        #         0.000 to 64.050 (64V models).
        # *RST:  32.050 or 64.050
        # Default unit: V
        self.ovp_limit_ch1 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:LEVel? (@1)", set_cmd="VOLTage:PROTection:LEVel {value}, (@1)", alias="ovp_limit_ch1", unit="V", fmt="flt3")
        self.ovp_limit_ch2 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:LEVel? (@2)", set_cmd="VOLTage:PROTection:LEVel {value}, (@2)", alias="ovp_limit_ch2", unit="V", fmt="flt3")
        self.ovp_limit_ch3 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:LEVel? (@3)", set_cmd="VOLTage:PROTection:LEVel {value}, (@3)", alias="ovp_limit_ch3", unit="V", fmt="flt3")
        self.ovp_limit_ch4 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:LEVel? (@4)", set_cmd="VOLTage:PROTection:LEVel {value}, (@4)", alias="ovp_limit_ch4", unit="V", fmt="flt3")

        # [SOURce:]VOLTage:PROTection:TRIPped? [<Channel list>]
        # Query OVP state of the selected channel.
        self.ovp_state_ch1 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:TRIPped? (@1)", alias="ovp_state_ch1", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)
        self.ovp_state_ch2 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:TRIPped? (@2)", alias="ovp_state_ch2", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)
        self.ovp_state_ch3 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:TRIPped? (@3)", alias="ovp_state_ch3", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)
        self.ovp_state_ch4 = VisaVar(self._dev, get_cmd="VOLTage:PROTection:TRIPped? (@4)", alias="ovp_state_ch4", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)


        # Overcurrent Protection ---

        # FUSE:TRIPped? [<Channel list>]
        # Query OCP state of the selected channel.
        self.ocp_state_ch1 = VisaVar(self._dev, get_cmd="FUSE:TRIPped? (@1)", alias="ocp_state_ch1", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)
        self.ocp_state_ch2 = VisaVar(self._dev, get_cmd="FUSE:TRIPped? (@2)", alias="ocp_state_ch2", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)
        self.ocp_state_ch3 = VisaVar(self._dev, get_cmd="FUSE:TRIPped? (@3)", alias="ocp_state_ch3", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)
        self.ocp_state_ch4 = VisaVar(self._dev, get_cmd="FUSE:TRIPped? (@4)", alias="ocp_state_ch4", lookup={0: "not tripped", 1: "tripped"}, value_conv=int)

        # FUSE:DELay:INITial <arg0>[, <Channel list>]
        # FUSE:DELay:INITial? [<Channel list>]
        # initial fuse delay time once output turns on.
        
        # FUSE:DELay[:BLOWing] <arg0>[, <Channel list>]
        # FUSE:DELay[:BLOWing]? [<Channel list>]
        # fuse delay time.


    # #########################################################################
    def __del__(self):
        try:
            # final cleanup attempt
            self.close()
        except (AttributeError, NameError):
            # might already be gone
            pass
        
    def __str__(self):
        return (f"{self.__class__.__name__} Device:\n"
                f"    {self.res_id.strip() or 'n/a'}\n"
                f"    VISA Address: {self._address}")


    # #########################################################################
    def close(self):
        """ Close active resource/device connection. 
            Note: 
                This does _not_ close the PyVISA resource manager session, 
                as it is shared across all opened devices.
        """
        # self._dev.write('SYST:LOC')
        try:
            self._dev.write('SYSTem:LOCal') # return to manual (local) operation
            self._dev.close()
        except pyvisa.errors.InvalidSession:
            # session may already be (have been) closed
            pass

        # self._rm.close()
        # "Since the resource manager session is shared between instances this 
        #  will also terminate connections obtained from other ResourceManager 
        #  instances."
        # => closing the rm here would also invalidate any other opened device/resource

    # Common setting commands ---
    def clearStatus(self):
        """ Clear status registers.
            Sets the status byte (STB), the standard event register (ESR) and the
            EVENt part of the QUEStionable and the OPERation registers to zero. 
            The command does not alter the mask and transition parts of the registers. 
            It clears the output buffer.
        """
        self._dev.write("*CLS")

    def waitForReady(self):
        """ Prevent servicing of the subsequent commands until all preceding 
            commands have been executed and all signals have settled.
        """
        self._dev.write("*WAI")

    def storeInstrumentSettings(self, slot: int):
        """ Store current instrument settings under the specified slot number 
            in internal memory.
            Parameters:
                slot - memory slot number (range 0-9)
        """
        assert 0 <= slot <= 9
        self._dev.write(f"*SAV {slot:d}")
        checkCommandErrors(self._dev)

    def loadInstrumentSettings(self, slot: int):
        """ Load instrument settings from internal memory fslot number 
            in internal memory.
            Parameters:
                slot - memory slot number (range 0-9)
        """
        assert 0 <= slot <= 9
        self._dev.write(f"*RCL {slot:d}")
        checkCommandErrors(self._dev)

    # #########################################################################
    def resetStatistics(self, channel):
        """ Reset the minimum, maximum and average (_min/_max/_avg) statistic 
            values for voltage, current, and power measurements.
            
            Parameters:
                channel - specific channel number (1..4) to reset
                          None: reset all available channels
        """
        # MEASure[:SCALar]:STATistic:RESet [<Channel list>]
        return self._dev.write(f"MEASure:STATistic:RESet (@{channel})")
        checkCommandErrors(self._dev)
        
    def getSampleCount(self):
        """ Returns the number of samples measured in the statistics for 
            voltage/current/power
            Returns a tuple with counts, one value for each channel
        """
        channels = "1:4" if self.model in ("NGP804", "NGP814", "NGP824") else "1,2"
        return self._dev.query_ascii_values(
                         f"MEASure:STATistic:COUNt? (@{channels})",
                         delay=0, converter="d", container=tuple)
    
    # #########################################################################
    def systemDatetime(self, dt=None) -> datetime.datetime:
        """ Set/query device's current system datetime.
            Parameters:
                dt - a new datetime.datetime value to set or 
                     None: keep datetime as-is
            Returns the current device's system datetime
        """
        if dt is not None:
            self._dev.write(f"SYSTem:DATE {dt.year}, {dt.month}, {dt.day}")
            self._dev.write(f"SYSTem:TIME {dt.hour}, {dt.minute}, {dt.second}")
            checkCommandErrors(self._dev)
            
        sys_time = self._dev.query_ascii_values("SYSTem:TIME?", delay=0, converter="d")
        sys_date = self._dev.query_ascii_values("SYSTem:DATE?", delay=0, converter="d")
        
        # year, month, day, hour, minutes, seconds
        return datetime.datetime(*(sys_date + sys_time))
    
    def _updateSystemDatetime(self):
        """ Set device's datetime to the current system's date and time """
        # self.system_datetime = datetime.datetime(*time.localtime()[:6])
        self.systemDatetime(datetime.datetime(*time.localtime()[:6]))

       
    # #########################################################################
    def displayText(self, text=None):
        """ Show a text message box on the front display.
            Parameters        
                text - text string to show.
                       None (or empty string): clear any current message box
        """
        if text:
            # ensure strings are quoted (or contained spaces may cause issues)
            self._dev.write(f"DISPlay:TEXT {text!r}")
        else:
            self._dev.write(f"DISPlay:TEXT:CLEar")
        checkCommandErrors(self._dev)
    
    # #########################################################################
    def displayBrightness(self, value=None):
        """ Set/query display brightness. 
            Parameters:
                value - Brightness in range 0.0 to 1.0 (increment 0.1, *RST: 0.8). 
                        None: keep current brightness value
            Returns the current brightness value
        """
        if value is not None:
            value = round(max(0.0, min(value, 1.0)), 1)
            self._dev.write(f'DISP:BRIG {value:.1f}')
        value = float(checkedQuery(self._dev, "DISPlay:BRIGhtness?", delay=0))
        return value

    # #########################################################################
    def masterOutputEnable(self, enable=None):
        """ Set/query master output state. 
            
            Note:
                Enabling/disabling master output while any channels are active
                will cause PSU to omit a slight beep
        
            Parameters:
                enable - True: enable output, False: disable output 
                         None: keep current state
            Returns current output enabled state
        """
        # OUTPut:GENeral[:STATe] <arg0>
        # OUTPut:GENeral[:STATe]? 
        if enable is not None:
            self._dev.write(f'OUTPut:GENeral {int(bool(enable))}')
        state = bool(int(checkedQuery(self._dev, "OUTPut:GENeral?", delay=0)))
        return state
    
    # #########################################################################
    def channelOutputEnable(self, channel, enable=None):
        """ Set/query output state of a single channel.
        
            Note:
                Enabling/disabling a channel while master output is active,
                will cause PSU to omit a slight beep

            Parameters:
                channel - channel number (1..4, may be fewer with selected models)
                enable  - True: enable output, False: disable output
                          None: keep current output state
                          
            Returns the current channel output state
        """
        # OUTPut:SELect <arg0>[, <Channel list>]
        # OUTPut:SELect? [<Channel list>]
        # Note: scpi command could also set/query multiple output at once:
        # OUTPut:SEL? (@1,2,3,4)
        # OUTPut:SEL 0, (@1,2,3,4)
        # OUTPut:SEL 1, (@1,2,3,4)
        assert isinstance(channel, int) 
        if enable is not None:
            self._dev.write(f"OUTPut:SELect {int(bool(enable))}, (@{channel})")
        return bool(int(checkedQuery(self._dev, f"OUTPut:SELect? (@{channel})", delay=0)))
    

        
        


    # #########################################################################
    def channelSafetyLimitEnable(self, channel, enable=None):
        """ Set/query safety limit state of a single channel.
            Parameters:
                channel - channel number (1..4, may be fewer with selected models)
                enable  - True: activate limit, False: deactivate limit
                          None: keep current state
            Returns the current channel safety limit state
        """
        # [SOURce:]ALIMit[:STATe] <arg0>[, <Channel list>]
        # [SOURce:]ALIMit[:STATe]? [<Channel list>]
        assert isinstance(channel, int) 
        if enable is not None:
            self._dev.write(f"ALIMit:STATe {int(bool(enable))}, (@{channel})")
        return bool(int(checkedQuery(self._dev, f"ALIMit:STATe? (@{channel})", delay=0)))
    
    # #########################################################################
    def channelOVPEnable(self, channel, enable=None):
        """ Set/query overvoltage protection (OVP) state of the selected channel.
            Parameters:
                channel - channel number (1..4, may be fewer with selected models)
                enable  - True: activate OVP, False: deactivate OVP
                          None: keep current state
            Returns the current OVP state
        """
        # [SOURce:]VOLTage:PROTection[:STATe] <arg0>[, <Channel list>]
        # [SOURce:]VOLTage:PROTection[:STATe]? [<Channel list>]
        assert isinstance(channel, int) 
        if enable is not None:
            self._dev.write(f"VOLTage:PROTection {int(bool(enable))}, (@{channel})")
        return bool(int(checkedQuery(self._dev, f"VOLTage:PROTection? (@{channel})", delay=0)))
    
    def channelOVPClear(self, channel):
        """ Reset OVP state of the selected channel. If an OVP event has 
            occurred before, the reset also erases the message on the display.
            Parameters: 
                channel - channel number (1..4, depending on specific model)
        """
        # [SOURce:]VOLTage:PROTection:CLEar [<Channel list>]
        self._dev.write(f"VOLTage:PROTection:CLEar (@{channel})")
        checkCommandErrors(self._dev)
        
    # #########################################################################
    def channelOCPEnable(self, channel, enable=None):
        """ Set/query overcurrent protection (OCP) state of the selected channel.
            Parameters:
                channel - channel number (1..4, may be fewer with selected models)
                enable  - True: activate OCP, False: deactivate OCP
                          None: keep current state
            Returns the current OCP state
        """
        # FUSE[:STATe] <arg0>[, <Channel list>]
        # FUSE[:STATe]? [<Channel list>]
        assert isinstance(channel, int) 
        if enable is not None:
            self._dev.write(f"FUSE:STATe {int(bool(enable))}, (@{channel})")
        return bool(int(checkedQuery(self._dev, f"FUSE:STATe? (@{channel})", delay=0)))
    
    def channelOCPClear(self, channel):
        """ Reset OCP state of the selected channel. If an OCP event has 
            occurred before, the reset also erases the message on the display.
            Parameters: 
                channel - channel number (1..4, depending on specific model)
        """
        # FUSE:TRIPped:CLEar [<Channel list>]
        self._dev.write(f"FUSE:TRIPped:CLEar (@{channel})")
        checkCommandErrors(self._dev)
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Arbitrary Sequence - prrof-of-concept ---
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def defineSequence(self, points, channel=1, block=1, repetitions=1, hold_at_end=False):
        """ Define an arbitrary sequence.
            Note:
                still proof-of-concept.
                
            Parameters:
                points      - sequence of arbitrary points as a list/tuple of 
                              4-element tuples (voltage, current, time, interpolation)
                              See note
                channel     - output channel number (1..4, may be fewer with selected models)
                block       - sequence block number (1..8)
                repetitions - how often the defined sequence should be repeated.
                              range [0..65535]
                              0: repeat sequence infinitely
                hold_at_end - endpoint behavior.
                              True: hold last value at end of sequence ("HOLD")
                              False: deactivate output channel at end of sequence ("OFF")
                
            Note: Sequences
                * up to 1024 points can be defined
                * dwell time between 2 arbitrary points is [1ms .. 60ms]
                  according to ARBitrary:DATA, p221, NGP800_User_Manual_en_12.pdf,
                  but examples use 0.5 for "500ms", so maybe it is more like
                  [1ms..60s]
                * Each point is defined as a 4-tuple
                  (voltage_v, current_a, dwell_time_s, interpolation_mode)
                  * e.g. ARB:DATA 10,1,0.5,0
                    * Voltage1 = 10 V 
                    * Current1 = 1 A, 
                    * Time1 = 500 ms 
                    * Interpolation mode1 = 0 (disabled).
                  * ARB:DATA? -> 10.000, 1.000, 0.50, 1
                  
        """
        repetitions = int(repetitions)
        channel = int(channel)
        block = int(block)
        
        assert isinstance(points, (tuple, list))
        assert len(points) > 0 
        assert len(points) <= 1024, "max 1024 points supported"
        assert all(isinstance(p, (tuple, list)) and len(p) == 4 for p in points)
        assert 1 <= channel <= 4
        assert 1 <= block <= 8
        assert 0 <= repetitions <= 65535

        self._dev.write(f"INST OUT{channel}")
        checkCommandErrors(self._dev)

        # flatten point data to a single sequence
        arb_seq = ",".join( ",".join(str(v) for v in p) for p in points)
        
        # Note: after clearing a sequence with ARBitrary:SEQuence:CLEar,
        # transferring ARB:BLOCK:DATA (with ARB:SEQuence:TRANsfer) seems to 
        # fail without also writing something (anything?) to ARB:DATA. 
        # Generated waveform follows data in BLOCK, though
        #self._dev.write(f"ARB:DATA {arb_seq}")
        self._dev.write(f"ARB:DATA 0,0,0,0")

        self._dev.write(f"ARB:BLOCK {block}")
        self._dev.write(f"ARB:BLOCK:DATA {arb_seq}")
        self._dev.write(f"ARB:BLOCK:REP {int(repetitions)}")
        self._dev.write(f"ARB:SEQ:REP 1")
        self._dev.write(f"ARB:SEQ:BEH:END {'HOLD' if hold_at_end else 'OFF'}")
        checkCommandErrors(self._dev)
        
        
        # ARBitrary:REPetitions <arg0>            # 0..65535 (0: infinite)
        # ARBitrary:REPetitions? 
        # Sets or queries the repetition rate of the defined arbitrary waveform 
        # for the previous selected channel.
        #
        # ARBitrary:SEQuence:REPetitions <arg0>   # 0..65535 (0: infinite)
        # ARBitrary:SEQuence:REPetitions? 
        # Sets or queries the number of repetitions of the arbitrary sequence.
        #
        # ARBitrary:BLOCk:REPetitions <arg0>      # 0..65535 (0: infinite)
        # ARBitrary:BLOCk:REPetitions? 
        # Sets or queries the number of repetitions of the block of arbitrary data.

        
        
        # transfer arbitrary points to channel
        self._dev.write("ARBitrary:SEQuence:TRANsfer")
        checkCommandErrors(self._dev)
        
        
        print("ARB:DATA?      ", self._dev.query_ascii_values("ARB:DATA?", delay=0, container=tuple))
        print("ARB:BLOC:DATA?:", self._dev.query_ascii_values("ARB:BLOC:DATA?", delay=0, container=tuple))
        
    
    def runSequence(self, channel=1):
        """ run defined sequence (enable generator) on specified channel(s) 
            Parameters:
                channel - channel number (1..4) or a list of multiple channel numbers
        """
        if isinstance(channel, (list, tuple)):
            channel = ",".join(str(int(c)) for c in sorted(channel))
        self._dev.write(f"ARB ON, (@{channel})")
        checkCommandErrors(self._dev)
     
     
    def stopSequence(self, channel=(1, 2, 3, 4)):
        """ stop running sequence on specified channel(s) 
            Parameters:
                channel - channel number (1..4) or a list of multiple channel numbers
        """
        if isinstance(channel, (list, tuple)):
            channel = ",".join(str(int(c)) for c in sorted(channel))
        self._dev.write(f"ARB OFF, (@{channel})")
        try:
            checkCommandErrors(self._dev)
        except ScpiCommandError as ex:
            # trying to stop an already stopped sequence will show a "settings conflict"
            # [-221] Settings conflict;ARB OFF, (@1,2,3,4)
            # Not-stopping a runaway sequence would later prevent setting
            # of output voltages, though
            if not (len(ex.visa_errors) == 1 and ex.visa_errors[0].code == -221):
                # ignore settings conflicts, re-raise anything else
                raise
                
        
    def clearSequence(self):
        """ clear sequence on current channel """
        self._dev.write("ARBitrary:SEQuence:CLEar")
        checkCommandErrors(self._dev)
        
    def sequenceStatus(self, channel=(1, 2, 3, 4)):
        """ get sequence status (running/stopped) for one or more channels """
        if isinstance(channel, (list, tuple)):
            channel = ",".join(str(int(c)) for c in sorted(channel))
            return self._dev.query_ascii_values(f"ARB? (@{channel})", delay=0, converter="d", container=tuple)
        else:
            return int(checkedQuery(self._dev, f"ARB? (@{channel})"))


def testArbSeq(psu):
    psu.defineSequence(
        points = (
            (1, 1, 1, 0,), 
            (2, 1, 1, 0,), 
            (3, 1, 1, 0,),
            (4, 1, 1, 0,),
            (5, 1, 1, 0,),
            (4, 1, 1, 1,),
            (3, 1, 1, 1,),
            (2, 1, 1, 1,),
            (1, 1, 1, 1,),
            (0, 1, 1, 1,), 
        ), 
        channel=1, 
        repetitions=1, 
        hold_at_end=True)
    
    print("ARBitrary:STATe (channels 1..4):", checkedQuery(psu._dev, "ARBitrary:STATe? (@1,2,3,4)", delay=0))
    psu.runSequence()
    psu.channelOutputEnable(1, True)
    
    start_time = time.time()
    while time.time() - start_time < 10.0:
        print(psu.voltage_ch1.info())
        time.sleep(.1)
    
    print("ARBitrary:STATe (channels 1..4):", checkedQuery(psu._dev, "ARBitrary:STATe? (@1,2,3,4)", delay=0))

    psu.stopSequence()
    
    print("ARBitrary:STATe (channels 1..4):", checkedQuery(psu._dev, "ARBitrary:STATe? (@1,2,3,4)", delay=0))


# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    
    def showError():
        """ show error message if an error is active on device """
        code, msg = psu._dev.query(":SYSTem:ERRor?", delay=0).split(",", maxsplit=1)
        code = int(code)
        if code != 0:
            print(f"> Device Error: [{code}] {msg}")
        
    try:
        
        psu = NGP800Series(visa_address="TCPIP0::192.168.10.10")
        time.sleep(.5)
        print(psu)
        
        print(f"{psu.displayBrightness(.8) = }")
        psu.displayBrightness(.4)
        print(f"{psu.displayBrightness() = }")

        print(psu._dev.query_ascii_values("SYSTem:DATE?", delay=0, converter="d"))
        showError()
        print(psu.systemDatetime())
        print("-" * 80)
        
        
        # stop any still running arbitrary sequence
        psu.stopSequence(channel=(1, 2, 3, 4))
        
        # psu.ch1_output_enabled = True
        # psu.ch3_output_enabled = True
        #
        # print(f"{psu.ch1_output_enabled = }")
        # print(f"{psu.ch2_output_enabled = }")
        # print(f"{psu.ch3_output_enabled = }")
        #

        psu.masterOutputEnable(True)
        
        # psu.master_output_enable = True
        # showError()
        # print(f"{psu.master_output_enable = }")
        # showError()
        # psu.voltage_preset_ch1.set(2.22)
        # showError()
        # print(psu.voltage_preset_ch1.info())
        # showError()
        # print(psu.voltage_ch1.info())
        # showError()


        psu.voltage_preset_ch1.set(1.234)
        psu.channelOutputEnable(1, True)

        print(psu.voltage_preset_ch1.info())
        print(psu.voltage_ch1.info())

        print(psu.temperature_ch1.info())

        # print("Error: ", psu._dev.query(":SYSTem:ERRor?", delay=0))
        # print("Bad OUT:",  psu._dev.write("INST OUT42"))
        # print("Error: ", psu._dev.query(":SYSTem:ERRor?", delay=0))
        

        psu.channelOutputEnable(1, True)
        psu.channelOutputEnable(2, True)
        psu.channelOutputEnable(3, True)
        print(f"{psu.channelOutputEnable(1) = }")
        print(f"{psu.channelOutputEnable(2) = }")
        print(f"{psu.channelOutputEnable(3) = }")
        psu.channelOutputEnable(2, False)
        print(f"{psu.channelOutputEnable(1) = }")
        print(f"{psu.channelOutputEnable(2) = }")
        print(f"{psu.channelOutputEnable(3) = }")

        # try:
        #     psu.channelOutputEnable(5, False)
        # except Exception as ex:
        #     print(f"# This should fail:\n> {type(ex).__name__}: {ex}")
        # try:
        #     print(f"{psu.channelOutputEnable(5) = }")
        # except Exception as ex:
        #     print(f"# This should fail:\n> {type(ex).__name__}: {ex}")


        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # print("-" * 80)
        # for channel in range(1, 5):
        #     print(f"# Channel {channel}: ")
        #     print(f"{psu.channelSafetyLimitEnable(channel) = }")
        #     print(f"{psu.channelOVPEnable(channel) = }")
        #     print(f"{psu.channelOCPEnable(channel) = }")
        #
        #

        
        # print("-" * 80)
        # for name, element in vars(psu).items():
        #     if isinstance(element, VisaVar):
        #         print(f"psu.{name!s:<20} => {element.info():<40} # {element!r}")

        print(f"{psu.getSampleCount() = }")
        
        testArbSeq(psu)

        psu.displayText(None)
        showError()
        psu.close()
        
    except pyvisa.errors.VisaIOError as ex:
        print("-" * 120)
        print(f"> {type(ex).__name__}: {ex}")
    print("\nDone.")

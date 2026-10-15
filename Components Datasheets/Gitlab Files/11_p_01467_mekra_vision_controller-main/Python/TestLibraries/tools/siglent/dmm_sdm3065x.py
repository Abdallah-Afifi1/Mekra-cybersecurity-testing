#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : dmm_sdm3065x.py
# Package : tools.siglent
# Task    : Access to Siglent Technologies SDM3065X digital multimeters via VISA.
#           Provides TTk variable abstractions for outputs/measurements.
#
# See also:
#          * SDM Series Digital Multimeter - Programming guide 
#          * SDM3065X Digital Multimeter - Remote Manual 
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 22.05.2025 | Tremmel   | initial
# 1.1.0  | 27.05.2025 | Tremmel   | added temperature measurement 
# 1.1.0 | 05.08.2026  | EHu Li    | added configureCurrentDC(), readCurrentDC(),
#                        startCurrentLog() and fetchCurrentLog(). The MEASure
#                        queries of the VisaVars reconfigure the instrument on
#                        every call and take about 2 s per reading.
#******************************************************************************
"""
@package tools.siglent.dmm_sdm3065x
Access to Siglent Technologies SDM3065X digital multimeters via VISA.
Provides TTk variable abstractions for outputs/measurements.

Requires package PyVisa
"""
import time
import math

import pyvisa

from tools.visa_variable import VisaVar, checkedQuery# , checkCommandErrors 

from ttk_base.errors import TTkException

# #############################################################################
class OverloadError(TTkException):
    """ Value outside of currently selected range. 
        Display will show "overload".
    """

# #############################################################################
def valConv(value, factor=None):
    """ Value conversion for scpi float values with "overload" detection when 
        using manually set ranges.
        
        Note: overload condition
            "If the input signal is greater than can be measured on the specified 
             manual range, the instrument displays the word overload on the front 
             panel and returns "+9.90000000E+37" from the remote interface."
         
        Parameters:
            value  - scpi string value representing a float 
            factor - factor to apply to converted value 
                     (default VisaVar value_conv callback does not supply a factor)
        
        Returns a float representation or value, or NaN if a overload condition 
        has been detected.
    """
    print(f"[value] {value!r}")
    if isinstance(value, str) and value.strip("+-\n ") == "9.90000000E+37":
        # * a newline tends to get appended
        # * temperature measurements may also return "-9.90000000E+37"
        value = math.nan # or just use float("NaN")

        # Alternatively, we could raise a custom exception to make the 
        # out-of-range state even more obvious:
        # raise OverloadError("Value outside of selected range")
    else:
        value = float(value)
    if factor is not None:
        value *= factor
    return value


#******************************************************************************
class SDM3065X:
    """ Access Siglent SDM3065X digital multimeters. """
    
    # #########################################################################
    def __init__(self, visa_address='TCPIP0::10.104.3.20::inst0::INSTR',
                       query_delay_s=None, timeout_ms=4000,
                       temp_probe="RTD/PT1000"):
        """ Parameters:
                visa_address  - visa address string of device, e.g. 
                                  "TCPIP0::10.104.3.20::inst0::INSTR" 
                                  or a shortened
                                  "TCPIP0::10.104.3.20"
                                  
                query_delay_s - default delay for visa queries in [s], i.e.
                                the delay between write and read operations.
                                None: use default pyvisa resource delay 
                                See pyvisa.resources.Resource.query_delay
                                Note that Resource.query_delay defaults to 0.0
                timeout_ms    - timeout in [ms] for visa access.
                                None: use default pyvisa resource timeout 
                                
                temp_probe    - type of connected temperature probe in format 
                                "<type>/<transducer>". See Note

            
            Note: Temperature Probes
                Thermistor Probes: 
                    * <type>: RTD 
                    * <transducer>: {PT100|PT1000}
                Thermocouple Probes:
                    * <type>: THER 
                    * <transducer> {BITS90|EITS90|JITS90|KITS90|NITS90|RITS90|SITS90|TITS90} 
                
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
            
            if timeout_ms is not None:
                self._dev.timeout = max(0, timeout_ms) # timeout in [ms]
            
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
                
            self.clearStatus()

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
        
        # MEASure? queries:
        #     Select function, range and resolution in one command. 
        #     Remaining parameters are set to default values:
        #      * Autozero             off
        #      * Samples per Trigger: 1
        #      * Trigger Count:       1
        #      * Trigger Delay:       automatic
        #      * Trigger Source       immediate 
        #      * Trigger Slope        negative 
        #      * Math Functions       disabled 
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # DC Voltage (immediate) ---
        # MEASure[:VOLTage]:{AC|DC}? [{<range>|AUTO|MIN|MAX|DEF}] 
        # Query voltage measurement
        #
        # DC voltage measurement
        # autorange
        self.voltage = VisaVar(self._dev, get_cmd="MEASure:VOLTage:DC?", alias="voltage", unit="V", fmt="flt4", descr="Voltage (autorange)")

        # voltage ranges (SDM3055//SDM3065X)：  
        # <range> ： {200mV|2V|20V|200V|1000V(DC)/750V(AC)} ， Default :AUTO 
        self.voltage_200mV = VisaVar(self._dev, "MEASure:VOLTage:DC? 200mV", alias="voltage_200mV", unit="mV", fmt="flt4", 
                                     descr="DC Voltage (200mV range)", value_conv=lambda v: valConv(v, 1000.0))
        self.voltage_2V    = VisaVar(self._dev, "MEASure:VOLTage:DC? 2V",    alias="voltage_2V",    unit="V", fmt="flt4", 
                                     descr="DC Voltage (2V range)",    value_conv=valConv)
        self.voltage_20V   = VisaVar(self._dev, "MEASure:VOLTage:DC? 20V",   alias="voltage_20V",   unit="V", fmt="flt4", 
                                     descr="DC Voltage (20V range)",   value_conv=valConv)
        self.voltage_200V  = VisaVar(self._dev, "MEASure:VOLTage:DC? 200V",  alias="voltage_200V",  unit="V", fmt="flt4", 
                                     descr="DC Voltage (200V range)",  value_conv=valConv)
        # "if the input signal is greater than can be measured on the specified 
        # manual range, the instrument displays the word overload on the front 
        # panel and returns "+9.90000000E+37" from the remote interface."


        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # DC Current (immediate) ---
        # MEASure:CURRent:{AC|DC}?  [{<range>|AUTO|MIN|MAX|DEF}] 
        
        # Query current measurement
        # autorange
        self.current = VisaVar(self._dev, "MEASure:CURRent:DC?", alias="current", unit="A", fmt="flt4", 
                               descr="Current (autorange)")
        
        # Current ranges, SDM3065X: 
        # <range> ： {200uA|2mA|20mA|200mA|2A|10A|AUTO} ， Default: AUTO 
        # converted value as µA/mA/A as appropriate
        self.current_200uA = VisaVar(self._dev, "MEASure:CURRent:DC? 200uA", alias="current_200uA", unit="µA", fmt="flt2", 
                                     descr="Current (200 µA range)", value_conv=lambda v: valConv(v, 1000000.0))
        self.current_2mA   = VisaVar(self._dev, "MEASure:CURRent:DC? 2mA",   alias="current_2mA", unit="mA", fmt="flt2", 
                                     descr="Current (2 mA range)",   value_conv=lambda v: valConv(v, 1000.0))
        self.current_20mA  = VisaVar(self._dev, "MEASure:CURRent:DC? 20mA",  alias="current_20mA", unit="mA", fmt="flt2", 
                                     descr="Current (20 mA range)",  value_conv=lambda v: valConv(v, 1000.0))
        self.current_2A    = VisaVar(self._dev, "MEASure:CURRent:DC? 2A",    alias="current_2A", unit="A", fmt="flt4", 
                                     descr="Current (2 A range)",    value_conv=valConv)
        self.current_10A   = VisaVar(self._dev, "MEASure:CURRent:DC? 10A",   alias="current_10A", unit="A", fmt="flt4", 
                                     descr="Current (10 A range)",   value_conv=valConv)
        
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Temperature (immediate) ---
        # MEASure:TEMPerature?[{RTD|THER|DEFault}[,{<type>|DEFault}]] 
        # <probe_type>: {RTD|THER} ， default THER. 
        #               THER: Thermocouple, RTD: Thermistor
        # The default command can only choose the built-in sensor manufacturers. 
        # For RTD/Thermistor:    <type>:{ PT100|PT1000} 
        # For THER/Thermocouple: <type>:{BITS90|EITS90|JITS90|KITS90|NITS90|RITS90|SITS90|TITS90} 
        try:
            probe_type, transducer = temp_probe.strip().split("/")
        except IndexError:
            probe_type, transducer = "DEFault", "DEFault"
        assert probe_type.upper() in ("RTD", "THER", "DEFAULT", "DEF")
        
        self.temperatureUnit("C")
        self.temperature = VisaVar(self._dev, f"MEASure:TEMPerature? {probe_type}, {transducer}", alias="temperature", unit="°C", fmt="flt3", 
                                   descr="Temperature",  value_conv=valConv)
        
        
        
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
    def temperatureUnit(self, unit=None):
        """ Set/query unit used for temperature measurements.
            Parameters:
                unit - unit to use: "C": °C, "F": °F, "K": K
            Returns the currently used unit (C, F or K)
        """
        if unit is not None:
            unit = str(unit).strip().replace("°", "")
            self._dev.write(f"UNIT:TEMPerature {unit}")
        return checkedQuery(self._dev, "UNIT:TEMPerature?", delay=0)
            
    # #########################################################################
    def configureCurrentDC(self, current_range="2A", nplc=0.005, autozero=False):
        """ Configure a DC current measurement for repeated fast readings.

            MEASure? reconfigures function, range and trigger on every call, which
            costs more than a second. After this call readCurrentDC() only
            triggers and reads.

            Parameters:
                current_range - {200uA|2mA|20mA|200mA|2A|10A|AUTO}
                nplc          - integration time in power line cycles. Smaller is
                                faster and noisier.
                autozero      - False skips the zero reference between readings
        """
        self._dev.write("CONFigure:CURRent:DC %s" % current_range)
        self._dev.write("CURRent:DC:NPLC %s" % nplc)
        self._dev.write("TRIGger:SOURce IMMediate")

    # #########################################################################
    def readCurrentDC(self):
        """ Trigger and read one DC current value in [A].

            Requires a preceding configureCurrentDC().
            Returns NaN when the value is outside the configured range.
        """
        value = self._dev.query("READ?", delay=0)
        if isinstance(value, str) and value.strip("+-\n ") == "9.90000000E+37":
            return math.nan
        return float(value)
    
    # #########################################################################
    def startCurrentLog(self, samples):
        """ Start logging DC current readings into the instrument's memory.

            Returns immediately, the instrument samples on its own. Requires a
            preceding configureCurrentDC().

            Parameters:
                samples - number of readings to collect
        """
        self._dev.write("SAMPle:COUNt %d" % samples)
        self._dev.write("INITiate")

    # #########################################################################
    def fetchCurrentLog(self):
        """ Get the logged readings in [A] as a list.

            Blocks until the instrument has collected all of them.
            An out of range reading becomes NaN.
        """
        block = self._dev.query("FETCh?", delay=0)
        values = []
        for item in block.strip().split(","):
            item = item.strip()
            if not item:
                continue
            values.append(math.nan if item.strip("+-") == "9.90000000E+37"
                          else float(item))
        return values

            
    # #########################################################################
    def close(self):
        """ Close active resource/device connection. 
            Note: 
                This does _not_ close the PyVISA resource manager session, 
                as it is shared across all opened devices.
        """
        try:
            self._dev.close()
        except pyvisa.errors.InvalidSession:
            # session may already have been closed
            pass

        # self._rm.close()
        # "Since the resource manager session is shared between instances this 
        #  will also terminate connections obtained from other ResourceManager 
        #  instances."
        # => closing the rm here would also invalidate any other opened device/resource

    # #########################################################################
    # Common setting commands ---
    # (IEEE-488.2 Common Commands)
    def clearStatus(self):
        """ Clear Status. Clears event registers in all register groups. 
            Also clears the error queue.
        """
        self._dev.write("*CLS")

    def waitForReady(self):
        """ Wait until all preceding commands have been executed. """
        self._dev.write("*WAI")

        
    # #########################################################################
    def reset(self):
        """ Restore the machine's parameter configuration to the state 
            configuration when the power is up.
        """
        self._dev.write("SYSTem:PRESet")
        

# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    
    def showError():
        """ show error message if an error is active on device """
        code, msg = dmm._dev.query(":SYSTem:ERRor?", delay=0).split(",", maxsplit=1)
        code, msg = int(code), msg.strip()
        if code != 0:
            print(f"> Device Error: [{code}] {msg}")
        
    dmm = None
    try:
        
        dmm = SDM3065X(visa_address="TCPIP0::192.168.10.20") # , query_delay_s=.5
        time.sleep(.5)
        print(dmm)
        
        showError()
        
        print("-" * 80)
        for name, element in vars(dmm).items():
            if isinstance(element, VisaVar):
                print(f"dmm.{name!s:<20} => {element.info():<40} # {element!r}")
                #dmm.waitForReady() # makes no difference


        print(dmm.voltage_20V.info())
        print(dmm.voltage_20V.info())
        print(dmm.voltage_20V.info())
        print(dmm.voltage_20V.info())
        showError()
        
        
        # Command Summary 
        # [SENSe:]TEMPerature:NULL[:STATe] 
        # [SENSe:]TEMPerature:NULL:VALue 
        # [SENSe:]TEMPerature:NULL:VALue:AUTO 
        # [SENSe:]TEMPerature:TRANsducer? 
        # [SENSe:]TEMPerature:{UDEFine|MDEFine}:{THER|RTD}:TRANsducer:LIST? 
        # [SENSe:]TEMPerature:{UDEFine|MDEFine}:{THER|RTD}:TRANsducer 
        # [SENSe:]TEMPerature:{UDEFine|MDEFine}:{THER|RTD}:TRANsducer:POINt? 
        
        print("TEMPerature:TRANsducer? =>", checkedQuery(dmm._dev, "TEMPerature:TRANsducer?").strip())
        print("# Temperature: Thermistor Probes (RTD)")
        print("UDEFine:RTD:TRANsducer:LIST?  =>", checkedQuery(dmm._dev, "TEMPerature:UDEFine:RTD:TRANSducer:LIST?").strip())
        print("MDEFine:RTD:TRANsducer:LIST?  =>", checkedQuery(dmm._dev, "TEMPerature:MDEFine:RTD:TRANSducer:LIST?").strip())
        print("# Temperature: Thermocouple Probes (THER):")
        print("UDEFine:THER:TRANsducer:LIST? =>", checkedQuery(dmm._dev, "TEMPerature:UDEFine:THER:TRANSducer:LIST?").strip())
        print("MDEFine:THER:TRANsducer:LIST? =>", checkedQuery(dmm._dev, "TEMPerature:MDEFine:THER:TRANSducer:LIST?").strip())

        
    except pyvisa.errors.VisaIOError as ex:
        print("-" * 120)
        print(f"> {type(ex).__name__}: {ex}")
        
    finally:
        if dmm:
            dmm.close()
        
    print("\nDone.")

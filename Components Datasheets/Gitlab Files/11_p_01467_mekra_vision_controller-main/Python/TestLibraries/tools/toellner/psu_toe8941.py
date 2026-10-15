#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : psu_toe8941.py
# Package : tools.toellner
# Task    : Access to TOELLNER TOE 8941-series power supplies via VISA.
#           Provides TTk variable abstractions for outputs/measurements.
#
# Copyright 2026 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 06.07.2026 | Tremmel   | initial, modeled after tools.rhode_schwarz.psu_ngp800
# 1.1.0  | 06.07.2026 | Tremmel   | replaced guessed SCPI-99 commands with the
#                                 | actual command set extracted from TOELLNER's
#                                 | official LabView driver (TOE8950_LT_V6.1.2.llb)
# 1.2.0  | 06.07.2026 | Tremmel   | cross-checked against an independent in-house
#                                 | RS-232 driver for the same device
#                                 | (libraries/toellner8941.py); added confirmed
#                                 | VOLT:LIM/CURR:LIM ("Limitfunktion") commands
# 1.3.0  | 06.07.2026 | Tremmel   | cross-checked against tools.toellner.psu_toe8951
#                                 | (built from TOELLNER's official TOE8951 VEE
#                                 | driver, same "CIIL" command family): confirmed
#                                 | VOLT:PROT set command and added ovpEnable(),
#                                 | sensingEnable(), externalControlEnable()
#******************************************************************************
"""
@package tools.toellner.psu_toe8941
Access to TOELLNER TOE 8941-series power supplies via VISA interface.
Single-output, 200 W lab power supply, available in several voltage/current
variants (see table below). Provides TTk variable abstractions for
outputs/measurements.

Requires package PyVisa

Note: SCPI command set
    No official TOELLNER SCPI/remote-control reference manual for the
    TOE 894x/895x family was available. The command set used below was
    reverse-engineered by extracting the literal command strings embedded
    in TOELLNER's own official LabView instrument driver
    "TOE8950_LT_V6.1.2.llb" (a LabView VI Library, which is a National
    Instruments binary "RSRC" container - the command/query strings appear
    as plain-text constants inside it and were extracted directly, not
    guessed).

    This driver targets TOE895x/TOE8941 devices and explicitly lists
    "TOE8941" and "TOE895" among the device identification strings it
    matches against *IDN?, so the extracted commands should apply directly
    to TOE 8941 units.

    Findings relevant to this module:
      * TOELLNER instruments support more than one remote command language;
        the driver actively switches the device into its SCPI-compatible
        language ("SYST:LANG CIIL") right after connecting. This means the
        commands below are NOT necessarily full/standard SCPI-99 (no
        "[:LEVel][:IMMediate][:AMPLitude]" style long-forms were found) -
        they use short, direct mnemonics (e.g. "VOLT 5.0" rather than
        "VOLTage:LEVel:IMMediate:AMPLitude 5.0"). This module therefore
        sends "SYST:LANG CIIL" once on connect, mirroring the vendor driver.
      * The vendor driver only ever uses the SHORT mnemonic forms shown
        below (e.g. "SYST:ERR?", "SYST:LOC"). Whether the long spelled-out
        SCPI-99 forms (e.g. "SYSTem:ERRor?") are also accepted is unknown;
        if devices raise command errors, note that the shared
        tools.visa_variable.checkCommandErrors()/checkedQuery() helpers use
        the long form "SYSTem:ERRor?" for the error-queue query - this has
        not been confirmed to work on TOE 8941 hardware.
      * The vendor driver issues "*OPC?" (operation-complete query) after at
        least some set commands (e.g. after setting current) as a
        synchronization point. Consider calling operationComplete() after
        setting values if timing issues occur.
      * Commands NOT found anywhere in the extracted driver strings (and
        therefore NOT implemented here, to avoid presenting unverified
        functionality as working): store/recall of instrument settings
        (*SAV/*RCL), self-calibration (*CAL? or similar "Autocal" command),
        OVP enable/disable or OVP-clear, and setting the OVP trip level
        (only querying OVP level/state was found - see ovp_limit below).
      * "INST OUT1"/"INST OUT2" channel-selection commands exist in the
        driver for the dual-output TOE8950/TOE8952 variants but are not
        applicable to the single-output TOE 8941 and are intentionally not
        used here.

    A second, independent reference surfaced afterwards: an in-house RS-232
    (pyserial-based) driver for the very same TOE 8941 device
    (libraries/toellner8941.py). It corroborates *IDN?, SYST:REM/SYST:LOC,
    VOLT/VOLT?, CURR/CURR?, MEAS:VOLT?/MEAS:CURR?/MEAS:POW?, and additionally
    confirms two commands this module previously lacked evidence for:
      * VOLT:LIM / VOLT:LIM?   - the datasheet's separate "Limitfunktion"
        ("Einstellbereich Limit"), distinct from OVP (VOLT:PROT).
      * CURR:LIM / CURR:LIM?   - the equivalent limit for current.
    One discrepancy: that driver sends "OUTP ON"/"OUTP OFF" for the output
    state, while the vendor LabView driver used "OUTP 1"/"OUTP 0". Per SCPI
    boolean convention both forms are normally accepted as input (the
    queried response is always numeric), so this module keeps the numeric
    form used by the official vendor driver.

    That RS-232 driver also confirms TOE 8941 exposes a native serial
    interface with "\\r\\n"-terminated commands. If connecting via a VISA
    ASRL (serial/COM) resource instead of GPIB/USB/LAN, make sure to set
    matching write/read termination - this module does so automatically,
    see __init__().

    A third reference, tools.toellner.psu_toe8951 (built from TOELLNER's
    official Keysight VEE driver for the sibling TOE 8951, same "CIIL"
    command language), resolved two remaining gaps for this module:
      * VOLT:PROT <value>  is confirmed as a real SET command (the TOE 8951
        VEE driver uses it directly) - no longer just an inferred guess.
      * VOLT:PROT:STAT 0|1, SENS:VOLT:DET 0|1, and EXT 0|1 are all confirmed
        SET commands (UI toggles labeled "OVP", "Sensing", and "Extern" in
        the VEE driver), not just queries - see ovpEnable(), sensingEnable(),
        and externalControlEnable() below.

Note: connectivity of the specific unit used with this module
    The TOE 8941-80 unit this module targets is fitted with option
    TOE 8940/025 (USB interface, per the datasheet's ordering section).
    TOELLNER's USB option for this series is not confirmed to be a native
    USB-TMC device; given that the in-house driver referenced above talks to
    the same physical unit successfully over plain serial ("\\r\\n"-terminated
    ASCII commands via pyserial), the USB option most likely enumerates as a
    USB-to-serial virtual COM port rather than a USBTMC instrument. If so,
    connect via a VISA ASRL resource string for the assigned COM port (e.g.
    "ASRL5::INSTR"), NOT a "USB0::..." VISA resource string. Verify the
    actual COM port via Windows Device Manager once the unit is connected.
"""
import time

import pyvisa

from tools.visa_variable import VisaVar, checkCommandErrors, checkedQuery


# #############################################################################
# TOELLNER TOE 8941 Series:
#
#     Model         | voltage      |  current    | power (max)
#   ––––––––––––––––+––––––––––––––+–––––––––––––+––––––––––––
#     TOE 8941-20   |   0 .. 20 V  |  0 .. 20 A  |    200 W
#     TOE 8941-40   |   0 .. 40 V  |  0 .. 10 A  |    200 W
#     TOE 8941-60   |   0 .. 60 V  |  0 ..  7 A  |    200 W
#     TOE 8941-80   |   0 .. 80 V  |  0 ..  5 A  |    200 W
#     TOE 8941-130  |   0 .. 130 V |  0 ..  3 A  |    200 W
#
# All models: single output, autorange, output power adjustable 10..200 W,
# optional GPIB/USB/LAN interface (required for remote/SCPI control).
# https://www.toellner.de/
# #############################################################################


#******************************************************************************
class TOE8941:
    """ Access TOELLNER TOE 8941 series power supplies (single output). """

    # #########################################################################
    def __init__(self, visa_address='ASRL5::INSTR',
                       query_delay_s=None):
        """ Parameters:
                visa_address  - visa address string of device, e.g.
                                  "ASRL5::INSTR" for a device connected via
                                  its USB interface (option TOE 8940/025),
                                  which enumerates as a USB-to-serial virtual
                                  COM port rather than USB-TMC - substitute
                                  the actual COM port number assigned by
                                  Windows.
                                  Devices with the GPIB/LAN interface options
                                  would instead use e.g. "GPIB0::5::INSTR" or
                                  "TCPIP0::192.168.10.30::inst0::INSTR".

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

            if self._address.upper().startswith("ASRL"):
                # Native RS-232 interface uses "\r\n"-terminated commands
                # (confirmed via a separate in-house TOE 8941 serial driver,
                # libraries/toellner8941.py). VISA's default ASRL termination
                # may not match, so set it explicitly.
                self._dev.write_termination = '\r\n'
                self._dev.read_termination = '\r\n'

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

            # Switch the instrument into its SCPI-compatible command language.
            # Matches TOELLNER's own LabView driver, which sends this
            # unconditionally right after *IDN? on every connect.
            self._dev.write("SYST:LANG CIIL")
            self._dev.write("*CLS")

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

        # Voltage ---
        # VOLT <arg0>   / VOLT?
        # Set/query preset (setpoint) voltage of the output.
        # (confirmed: "TOE8950 Voltage.vi" writes ";:VOLT <value>")
        self.voltage_preset = VisaVar(self._dev, get_cmd="VOLT?", set_cmd="VOLT {value:f}", alias="voltage_preset", unit="V", fmt="flt3")

        # VOLT:AMPL? MIN / VOLT:AMPL? MAX
        # Query min/max settable voltage of the currently selected model.
        self.voltage_preset_min = VisaVar(self._dev, get_cmd="VOLT:AMPL? MIN", alias="voltage_preset_min", unit="V", fmt="flt3")
        self.voltage_preset_max = VisaVar(self._dev, get_cmd="VOLT:AMPL? MAX", alias="voltage_preset_max", unit="V", fmt="flt3")

        # MEAS:VOLT?
        # Query currently measured output voltage.
        self.voltage = VisaVar(self._dev, get_cmd="MEAS:VOLT?", alias="voltage", unit="V", fmt="flt3")

        # VOLT:LIM <arg0>   / VOLT:LIM?
        # Set/query the voltage "Limitfunktion" (soft cap on the settable
        # output voltage, distinct from OVP/VOLT:PROT below). Confirmed via
        # libraries/toellner8941.py (setVoltageLimit()/getVoltageLimit()).
        self.voltage_limit = VisaVar(self._dev, get_cmd="VOLT:LIM?", set_cmd="VOLT:LIM {value:f}", alias="voltage_limit", unit="V", fmt="flt3")

        # Current ---
        # CURR <arg0>   / CURR?
        # Set/query preset (setpoint) current of the output.
        # (confirmed: "TOE8950 Current.vi" writes ";:CURR <value>", followed by "*OPC?")
        self.current_preset = VisaVar(self._dev, get_cmd="CURR?", set_cmd="CURR {value:f}", alias="current_preset", unit="A", fmt="flt3")

        # CURR:AMPL? MIN / CURR:AMPL? MAX
        # Query min/max settable current of the currently selected model.
        self.current_preset_min = VisaVar(self._dev, get_cmd="CURR:AMPL? MIN", alias="current_preset_min", unit="A", fmt="flt3")
        self.current_preset_max = VisaVar(self._dev, get_cmd="CURR:AMPL? MAX", alias="current_preset_max", unit="A", fmt="flt3")

        # MEAS:CURR?
        # Query currently measured output current.
        self.current = VisaVar(self._dev, get_cmd="MEAS:CURR?", alias="current", unit="A", fmt="flt3")

        # CURR:LIM <arg0>   / CURR:LIM?
        # Set/query the current "Limitfunktion" (soft cap on the settable
        # output current). Confirmed via libraries/toellner8941.py
        # (setCurrentLimit()/getCurrentLimit()).
        self.current_limit = VisaVar(self._dev, get_cmd="CURR:LIM?", set_cmd="CURR:LIM {value:f}", alias="current_limit", unit="A", fmt="flt3")

        # Power ---
        # POW <arg0>   / POW?
        # Set/query preset output power limit (datasheet: "Einstellbare
        # Ausgangsleistung", adjustable 10..200 W).
        # (confirmed: "TOE8950 Power.vi" writes ";:POW <value>")
        self.power_preset = VisaVar(self._dev, get_cmd="POW?", set_cmd="POW {value:f}", alias="power_preset", unit="W", fmt="flt3")

        # POW:AMPL? MIN / POW:AMPL? MAX
        # Query min/max settable output power.
        self.power_preset_min = VisaVar(self._dev, get_cmd="POW:AMPL? MIN", alias="power_preset_min", unit="W", fmt="flt3")
        self.power_preset_max = VisaVar(self._dev, get_cmd="POW:AMPL? MAX", alias="power_preset_max", unit="W", fmt="flt3")

        # MEAS:POW?
        # Query currently emitted output power.
        self.power = VisaVar(self._dev, get_cmd="MEAS:POW?", alias="power", unit="W", fmt="flt3")

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Protection ---
        # "Einstellbarer Überspannungsschutz" (OVP)

        # VOLT:PROT <arg0>  / VOLT:PROT?
        # Set/query the overvoltage protection (OVP) trip level. The set
        # form is confirmed via tools.toellner.psu_toe8951 (same command
        # family); use ovp_limit.set(value) or ovpEnable()/VOLT:PROT:STAT
        # separately to enable/disable OVP itself.
        self.ovp_limit = VisaVar(self._dev, get_cmd="VOLT:PROT?", set_cmd="VOLT:PROT {value:f}", alias="ovp_limit", unit="V", fmt="flt3")

        # VOLT:PROT? MIN / VOLT:PROT? MAX
        # Query min/max settable OVP trip level.
        self.ovp_limit_min = VisaVar(self._dev, get_cmd="VOLT:PROT? MIN", alias="ovp_limit_min", unit="V", fmt="flt3")
        self.ovp_limit_max = VisaVar(self._dev, get_cmd="VOLT:PROT? MAX", alias="ovp_limit_max", unit="V", fmt="flt3")

        # VOLT:PROT:STAT?  (query - confirmed; use ovpEnable() for the
        # confirmed VOLT:PROT:STAT 0|1 set form, see below)
        self.ovp_state = VisaVar(self._dev, get_cmd="VOLT:PROT:STAT?", alias="ovp_state", lookup={0: "not tripped/off", 1: "tripped/on"}, value_conv=int)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Misc status queries (queries confirmed present in the driver; the
        # matching set commands are confirmed via tools.toellner.psu_toe8951,
        # see sensingEnable()/externalControlEnable() below)

        # SENS:VOLT:DET?
        # Remote/4-wire sensing input state ("Sensing"). Meaning confirmed
        # via tools.toellner.psu_toe8951 (UI toggle labeled "Sensing" in
        # that device's VEE driver) - use sensingEnable() to set it.
        self.sense_voltage_detector = VisaVar(self._dev, get_cmd="SENS:VOLT:DET?", alias="sense_voltage_detector", lookup={0: "disabled", 1: "enabled"}, value_conv=int)

        # EXT:STAT?
        # External analog control state ("Extern"). Exact semantics beyond
        # the UI toggle label are not documented; likely enables/disables
        # control of voltage/current via the analog interface's external
        # control voltages. Use externalControlEnable() to set it.
        self.external_status = VisaVar(self._dev, get_cmd="EXT:STAT?", alias="external_status", lookup={0: "disabled", 1: "enabled"}, value_conv=int)

        # OUTP:TRAC?
        # Output tracking state. Primarily relevant for dual-output
        # TOE8950/TOE8952 variants; likely fixed/not applicable on the
        # single-output TOE 8941.
        self.output_tracking = VisaVar(self._dev, get_cmd="OUTP:TRAC?", alias="output_tracking", value_conv=str)

        # STAT:QUES:EVEN?
        # Questionable status event register.
        self.questionable_status = VisaVar(self._dev, get_cmd="STAT:QUES:EVEN?", alias="questionable_status", value_conv=str)

        # STAT:QUES:INST:ISUM1:EVEN?
        # Questionable status summary for output 1 (the only output on
        # TOE 8941).
        self.questionable_status_output1 = VisaVar(self._dev, get_cmd="STAT:QUES:INST:ISUM1:EVEN?", alias="questionable_status_output1", value_conv=str)


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
        try:
            self._dev.write('SYST:LOC') # return to manual (local) operation
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
        """ Clear status registers. (*CLS) """
        self._dev.write("*CLS")

    def reset(self):
        """ Reset the instrument to its power-up default state. (*RST) """
        self._dev.write("*RST")
        checkCommandErrors(self._dev)

    def operationComplete(self):
        """ Query the operation-complete flag (*OPC?), i.e. block until all
            previously issued overlapped commands have finished executing.
            TOELLNER's own driver issues this after at least some set
            commands (e.g. after setting the current) as a synchronization
            point - call this after setting values if timing issues occur.
            Returns True once pending operations have completed.
        """
        return bool(int(checkedQuery(self._dev, "*OPC?", delay=0)))

    def remoteEnable(self):
        """ Switch the instrument into remote control mode. (SYST:REM) """
        self._dev.write("SYST:REM")

    def localEnable(self):
        """ Switch the instrument back into manual (local) front-panel
            control mode. (SYST:LOC)
        """
        self._dev.write("SYST:LOC")

    # #########################################################################
    def outputEnable(self, enable=None):
        """ Set/query output state.

            Parameters:
                enable - True: enable output, False: disable output ("Output
                         ON/OFF", drops voltage/current to 0 V / 0 A)
                         None: keep current state
            Returns the current output enabled state
        """
        # OUTP 1 / OUTP 0   (confirmed: "TOE8950 Output.vi"; the alternative
        # form "OUTP ON"/"OUTP OFF" is also confirmed working, see
        # libraries/toellner8941.py enableOutput()/disableOutput())
        # OUTP?
        if enable is not None:
            self._dev.write(f'OUTP {int(bool(enable))}')
        return bool(int(checkedQuery(self._dev, "OUTP?", delay=0)))

    # #########################################################################
    def ovpEnable(self, enable=None):
        """ Set/query overvoltage protection (OVP) state.
            (VOLT:PROT:STAT 0|1 / VOLT:PROT:STAT?, confirmed via
            tools.toellner.psu_toe8951 - UI toggle labeled "OVP" in that
            device's VEE driver)

            Note:
                It is not separately confirmed whether writing 0 here also
                clears an already-tripped state (no distinct "CLEar"
                command was found) - if OVP has tripped, writing 0 then 1
                is a reasonable approach to test/attempt a reset.

            Parameters:
                enable - True: activate OVP, False: deactivate OVP
                         None: keep current state
            Returns the current OVP state
        """
        if enable is not None:
            self._dev.write(f"VOLT:PROT:STAT {int(bool(enable))}")
        return bool(int(checkedQuery(self._dev, "VOLT:PROT:STAT?", delay=0)))

    # #########################################################################
    def sensingEnable(self, enable=None):
        """ Set/query the remote/4-wire sensing input state ("Sensing").
            (SENS:VOLT:DET 0|1 / SENS:VOLT:DET?, confirmed via
            tools.toellner.psu_toe8951)

            Parameters:
                enable - True: enable sensing input, False: disable it
                         None: keep current state
            Returns the current sensing state
        """
        if enable is not None:
            self._dev.write(f"SENS:VOLT:DET {int(bool(enable))}")
        return bool(int(checkedQuery(self._dev, "SENS:VOLT:DET?", delay=0)))

    # #########################################################################
    def externalControlEnable(self, enable=None):
        """ Set/query external analog control mode ("Extern").
            (EXT 0|1 / EXT:STAT?, confirmed via tools.toellner.psu_toe8951)

            Note:
                Exact semantics are not documented beyond the toggle's UI
                label; likely enables/disables control of voltage/current
                via the analog interface's external control voltages
                ("Schnelle Analogsteuerung" in the datasheet).

            Parameters:
                enable - True/False
                         None: keep current state
            Returns the current external-control state
        """
        if enable is not None:
            self._dev.write(f"EXT {int(bool(enable))}")
        return bool(int(checkedQuery(self._dev, "EXT:STAT?", delay=0)))

    # #########################################################################
    def senseAveragingEnable(self, enable=None):
        """ Set/query measurement averaging ("Sense Averaging").
            Parameters:
                enable - True: enable averaging, False: disable averaging
                         None: keep current state
            Returns the current averaging state
        """
        # SENS:AVER ON / SENS:AVER OFF   (confirmed in driver)
        # SENS:AVER?
        if enable is not None:
            self._dev.write(f"SENS:AVER {'ON' if enable else 'OFF'}")
        return checkedQuery(self._dev, "SENS:AVER?", delay=0).strip()

    # #########################################################################
    def slewRate(self, mode=None):
        """ Set/query the output voltage slew rate mode.
            Parameters:
                mode - "FAST" or "SLOW" (confirmed in driver:
                       "VOLT:SLEW:STAT FAST" / "VOLT:SLEW:STAT SLOW")
                       None: keep current setting
            Returns the current slew rate mode string.
        """
        if mode is not None:
            mode = str(mode).strip().upper()
            assert mode in ("FAST", "SLOW")
            self._dev.write(f"VOLT:SLEW:STAT {mode}")
        return checkedQuery(self._dev, "VOLT:SLEW:STAT?", delay=0).strip()


# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)

    def showError():
        """ show error message if an error is active on device """
        code, msg = psu._dev.query("SYST:ERR?", delay=0).split(",", maxsplit=1)
        code = int(code)
        if code != 0:
            print(f"> Device Error: [{code}] {msg}")

    try:

        psu = TOE8941(visa_address="ASRL5::INSTR") # substitute the actual COM port
        time.sleep(.5)
        print(psu)

        showError()

        psu.voltage_preset.set(5.0)
        psu.current_preset.set(1.0)
        psu.outputEnable(True)

        print(psu.voltage_preset.info())
        print(psu.voltage.info())
        print(psu.current_preset.info())
        print(psu.current.info())
        print(psu.power.info())

        print(f"{psu.outputEnable() = }")

        showError()

        psu.outputEnable(False)
        psu.close()

    except pyvisa.errors.VisaIOError as ex:
        print("-" * 120)
        print(f"> {type(ex).__name__}: {ex}")
    print("\nDone.")

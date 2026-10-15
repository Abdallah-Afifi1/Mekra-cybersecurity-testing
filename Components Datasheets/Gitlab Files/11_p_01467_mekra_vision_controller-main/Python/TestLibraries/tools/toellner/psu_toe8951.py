#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : psu_toe8951.py
# Package : tools.toellner
# Task    : Access to TOELLNER TOE 8951-series power supplies via VISA.
#           Provides TTk variable abstractions for outputs/measurements.
#
# Copyright 2026 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 06.07.2026 | Tremmel   | initial, modeled after tools.toellner.psu_toe8941;
#                                 | command set extracted from TOELLNER's official
#                                 | Keysight VEE driver (TOE8951-V7.00.vee)
#******************************************************************************
"""
@package tools.toellner.psu_toe8951
Access to TOELLNER TOE 8951-series power supplies via VISA interface.
Single-output, 400 W lab power supply, available in several voltage/current
variants (see table below). Provides TTk variable abstractions for
outputs/measurements.

Requires package PyVisa

Note: SCPI command set
    No official TOELLNER SCPI/remote-control reference manual for the
    TOE 895x family was available. As with tools.toellner.psu_toe8941 (see
    that module for the sibling single-output TOE 8941), the command set
    below was reverse-engineered from a real, official TOELLNER instrument
    driver - this time a Keysight/Agilent VEE program ("TOE8951-V7.00.vee",
    from the vendor-supplied "toe8951-v7.00.zip"). Unlike the LabView ".llb"
    binary used for TOE 8941, a ".vee" file is plain ASCII text, so the
    command strings below were read directly from the source rather than
    extracted from a binary blob - higher confidence than the TOE 8941
    findings.

    Findings:
      * Connection sequence (confirmed, sent as one combined command):
        "SYST:REM;:SYST:LANG CIIL;:*IDN?" - go to remote, switch to the
        SCPI-compatible "CIIL" command language, then query identity. This
        module replicates this exact sequence in __init__().
      * VOLT/CURR/POW <value>, VOLT?/CURR?/POW?, VOLT:AMPL?/CURR:AMPL?/
        POW:AMPL? MIN|MAX, MEAS:VOLT?/MEAS:CURR?/MEAS:POW?, OUTP 0|1, OUTP?
        - all directly confirmed, matching TOE 8941.
      * VOLT:PROT <value>  - confirmed as a SET command here (unlike
        TOE 8941, where only the query was found in the LabView driver).
        This resolves that earlier ambiguity for the whole TOE 895x/894x
        "CIIL" family.
      * VOLT:PROT:STAT 0|1  - confirmed as a SET command (toggle labeled
        "OVP" in the VEE UI), in addition to the query. Modeled here as
        ovpEnable() - likely also clears a tripped state when set to 0,
        though this is not separately confirmed (no distinct "CLEar"
        command was found).
      * SENS:VOLT:DET 0|1  - confirmed as a SET command (toggle labeled
        "Sensing" in the VEE UI). This clarifies the previously undocumented
        meaning of this query in the TOE 8941 module: it toggles the
        (remote/4-wire) sensing input on or off.
      * EXT 0|1  - confirmed as a SET command (toggle labeled "Extern" in
        the VEE UI), paired with the EXT:STAT? query. Likely enables/
        disables external analog control of voltage/current via the analog
        interface ("Schnelle Analogsteuerung" in the datasheet) - exact
        semantics not documented beyond the toggle's UI label.
      * STAT:QUES:COND?  - confirmed (the VEE driver queries the
        QUEStionable status CONDition register; TOE 8941's LabView driver
        instead queried the EVENt register - both registers are part of the
        standard SCPI status-reporting model and likely both exist here,
        but only COND? is directly confirmed for this module).
      * *IDN?, *RST, *OPC? - confirmed. No *CLS, *SAV/*RCL, *CAL, or any
        calibration/store-recall command was found in this driver either
        (same gap as TOE 8941) - NOT implemented here.
      * VOLT:LIM / CURR:LIM ("Limitfunktion", confirmed via the sibling
        TOE 8941 in-house serial driver, see psu_toe8941.py) were not
        present in this specific VEE program, but the TOE 8951 datasheet
        lists the identical "Einstellbereich Limit" feature with the same
        per-model ranges as the voltage/current setpoints, and both devices
        share the same "CIIL" command language - so these are included here
        too, carried over from the confirmed TOE 8941 finding rather than
        independently confirmed for TOE 8951.
      * No channel-selection ("INST OUT1"/"INST OUT2") commands were found;
        this module targets the single-output TOE 8951 only (not the
        dual-output TOE 8952).
      * No Arbiträrfunktion (arbitrary waveform, option TOE 9151) command
        syntax was found anywhere in this driver - see note below.

Note: Arbiträrfunktion (option TOE 9151) - NOT IMPLEMENTED
    The datasheet describes this option in detail (1000 steps/points, data
    per step = voltage/current/step-time, step time 10 ms..100 s in 5 ms
    steps, up to 10 blocks with individual repeat counts 1..65535 or
    infinite, internal/external trigger, burst function), but neither the
    TOE 8951 VEE driver nor the TOE 8941 LabView driver expose any command
    for it - there is currently zero evidence for its SCPI syntax. Rather
    than guessing at a multi-parameter feature with no grounding at all,
    this module deliberately leaves it unimplemented. If this functionality
    is needed, get the TOELLNER TOE 895x remote-control/programmer's manual,
    or determine the command syntax empirically against a real unit (e.g.
    by comparing SYST:ERR? after trying plausible ARBitrary:... mnemonics).
"""
import time

import pyvisa

from tools.visa_variable import VisaVar, checkCommandErrors, checkedQuery


# #############################################################################
# TOELLNER TOE 8951 Series (single-output; see tools.toellner.psu_toe8941 for
# the electrically near-identical TOE 8941, and the TOE 8951 datasheet for
# the dual-output sibling TOE 8952, not covered by this module):
#
#     Model         | voltage      |  current    | power (max)
#   ––––––––––––––––+––––––––––––––+–––––––––––––+––––––––––––
#     TOE 8951-20   |   0 .. 20 V  |  0 .. 40 A  |    400 W
#     TOE 8951-40   |   0 .. 40 V  |  0 .. 20 A  |    400 W
#     TOE 8951-60   |   0 .. 60 V  |  0 .. 14 A  |    400 W
#     TOE 8951-80   |   0 .. 80 V  |  0 .. 10 A  |    400 W
#     TOE 8951-130  |   0 .. 130 V |  0 ..  6 A  |    400 W
#
# All models: single output, autorange, output power adjustable 20..400 W,
# RS 232 standard, optional GPIB/USB interface (required for remote/SCPI
# control other than RS 232), optional Arbiträrfunktion (TOE 9151).
# https://www.toellner.de/
# #############################################################################


#******************************************************************************
class TOE8951:
    """ Access TOELLNER TOE 8951 series power supplies (single output). """

    # #########################################################################
    def __init__(self, visa_address='ASRL5::INSTR',
                       query_delay_s=None):
        """ Parameters:
                visa_address  - visa address string of device, e.g.
                                  "ASRL5::INSTR" for a device connected via
                                  RS 232 (standard interface) or via its
                                  optional USB interface (option
                                  TOE 8951/025), which - as with TOE 8941 -
                                  likely enumerates as a USB-to-serial
                                  virtual COM port rather than USB-TMC
                                  (not confirmed; verify actual COM port via
                                  Windows Device Manager). Substitute the
                                  actual COM port number assigned by
                                  Windows.
                                  A device with the GPIB interface option
                                  would instead use e.g. "GPIB1::4::INSTR"
                                  (the vendor VEE driver's own default
                                  address).

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
                # Native RS 232 interface uses "\r\n"-terminated commands
                # (confirmed via the sibling TOE 8941 in-house serial driver,
                # see psu_toe8941.py). VISA's default ASRL termination may
                # not match, so set it explicitly.
                self._dev.write_termination = '\r\n'
                self._dev.read_termination = '\r\n'

            # Confirmed connect sequence from TOELLNER's own VEE driver:
            # go to remote, switch to the SCPI-compatible "CIIL" command
            # language, then query identity - all as one combined command.
            self.res_id = self._dev.query('SYST:REM;:SYST:LANG CIIL;:*IDN?', delay=0.0)
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

        # Voltage ---
        # VOLT <arg0>   / VOLT?     (confirmed)
        # Set/query preset (setpoint) voltage of the output.
        self.voltage_preset = VisaVar(self._dev, get_cmd="VOLT?", set_cmd="VOLT {value:f}", alias="voltage_preset", unit="V", fmt="flt3")

        # VOLT:AMPL? MIN / VOLT:AMPL? MAX   (confirmed; vendor driver queries
        # both in one combined command "VOLT:AMPL? MIN;AMPL? MAX" - issued
        # here as two separate queries for consistency with the VisaVar
        # one-value-per-command model used throughout this codebase)
        self.voltage_preset_min = VisaVar(self._dev, get_cmd="VOLT:AMPL? MIN", alias="voltage_preset_min", unit="V", fmt="flt3")
        self.voltage_preset_max = VisaVar(self._dev, get_cmd="VOLT:AMPL? MAX", alias="voltage_preset_max", unit="V", fmt="flt3")

        # MEAS:VOLT?   (confirmed)
        # Query currently measured output voltage.
        self.voltage = VisaVar(self._dev, get_cmd="MEAS:VOLT?", alias="voltage", unit="V", fmt="flt3")

        # VOLT:LIM <arg0>   / VOLT:LIM?
        # Set/query the voltage "Limitfunktion" (soft cap on the settable
        # output voltage, distinct from OVP/VOLT:PROT below). NOT found in
        # this driver - carried over from the confirmed TOE 8941 finding
        # (same command language family, same datasheet feature/ranges).
        self.voltage_limit = VisaVar(self._dev, get_cmd="VOLT:LIM?", set_cmd="VOLT:LIM {value:f}", alias="voltage_limit", unit="V", fmt="flt3")

        # Current ---
        # CURR <arg0>   / CURR?     (confirmed)
        # Set/query preset (setpoint) current of the output.
        self.current_preset = VisaVar(self._dev, get_cmd="CURR?", set_cmd="CURR {value:f}", alias="current_preset", unit="A", fmt="flt3")

        # CURR:AMPL? MIN / CURR:AMPL? MAX   (confirmed)
        self.current_preset_min = VisaVar(self._dev, get_cmd="CURR:AMPL? MIN", alias="current_preset_min", unit="A", fmt="flt3")
        self.current_preset_max = VisaVar(self._dev, get_cmd="CURR:AMPL? MAX", alias="current_preset_max", unit="A", fmt="flt3")

        # MEAS:CURR?   (confirmed)
        # Query currently measured output current.
        self.current = VisaVar(self._dev, get_cmd="MEAS:CURR?", alias="current", unit="A", fmt="flt3")

        # CURR:LIM <arg0>   / CURR:LIM?
        # Set/query the current "Limitfunktion". NOT found in this driver -
        # carried over from the confirmed TOE 8941 finding (see voltage_limit
        # above).
        self.current_limit = VisaVar(self._dev, get_cmd="CURR:LIM?", set_cmd="CURR:LIM {value:f}", alias="current_limit", unit="A", fmt="flt3")

        # Power ---
        # POW <arg0>   / POW?     (confirmed)
        # Set/query preset output power limit (datasheet: "Einstellbare
        # Ausgangsleistung", adjustable 20..400 W).
        self.power_preset = VisaVar(self._dev, get_cmd="POW?", set_cmd="POW {value:f}", alias="power_preset", unit="W", fmt="flt3")

        # POW:AMPL? MIN / POW:AMPL? MAX   (confirmed)
        self.power_preset_min = VisaVar(self._dev, get_cmd="POW:AMPL? MIN", alias="power_preset_min", unit="W", fmt="flt3")
        self.power_preset_max = VisaVar(self._dev, get_cmd="POW:AMPL? MAX", alias="power_preset_max", unit="W", fmt="flt3")

        # MEAS:POW?   (confirmed)
        # Query currently emitted output power.
        self.power = VisaVar(self._dev, get_cmd="MEAS:POW?", alias="power", unit="W", fmt="flt3")

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Protection ---
        # "Einstellbarer Überspannungsschutz" (OVP)

        # VOLT:PROT <arg0>   / VOLT:PROT?   (both confirmed as set+query here)
        self.ovp_limit = VisaVar(self._dev, get_cmd="VOLT:PROT?", set_cmd="VOLT:PROT {value:f}", alias="ovp_limit", unit="V", fmt="flt3")

        # VOLT:PROT? MIN / VOLT:PROT? MAX   (confirmed)
        self.ovp_limit_min = VisaVar(self._dev, get_cmd="VOLT:PROT? MIN", alias="ovp_limit_min", unit="V", fmt="flt3")
        self.ovp_limit_max = VisaVar(self._dev, get_cmd="VOLT:PROT? MAX", alias="ovp_limit_max", unit="V", fmt="flt3")

        # VOLT:PROT:STAT?   (query - confirmed; use ovpEnable() for the
        # confirmed VOLT:PROT:STAT 0|1 set form)
        self.ovp_state = VisaVar(self._dev, get_cmd="VOLT:PROT:STAT?", alias="ovp_state", lookup={0: "not tripped/off", 1: "tripped/on"}, value_conv=int)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Misc status queries

        # STAT:QUES:COND?   (confirmed)
        # Questionable status condition register (unlatched, real-time).
        self.questionable_status = VisaVar(self._dev, get_cmd="STAT:QUES:COND?", alias="questionable_status", value_conv=str)


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
            self._dev.write('SYST:LOC') # return to manual (local) operation - confirmed
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
    def reset(self):
        """ Reset the instrument to its power-up default state. (*RST,
            confirmed)
        """
        self._dev.write("*RST")
        checkCommandErrors(self._dev)

    def operationComplete(self):
        """ Query the operation-complete flag (*OPC?, confirmed), i.e. block
            until all previously issued overlapped commands have finished
            executing. Returns True once pending operations have completed.
        """
        return bool(int(checkedQuery(self._dev, "*OPC?", delay=0)))

    def remoteEnable(self):
        """ Switch the instrument into remote control mode. (SYST:REM,
            confirmed - also sent automatically in __init__())
        """
        self._dev.write("SYST:REM")

    def localEnable(self):
        """ Switch the instrument back into manual (local) front-panel
            control mode. (SYST:LOC, confirmed - also sent automatically by
            close())
        """
        self._dev.write("SYST:LOC")

    # #########################################################################
    def outputEnable(self, enable=None):
        """ Set/query output state. (OUTP 0|1 / OUTP?, confirmed)

            Parameters:
                enable - True: enable output, False: disable output ("Output
                         ON/OFF", drops voltage/current to 0 V / 0 A)
                         None: keep current state
            Returns the current output enabled state
        """
        if enable is not None:
            self._dev.write(f'OUTP {int(bool(enable))}')
        return bool(int(checkedQuery(self._dev, "OUTP?", delay=0)))

    # #########################################################################
    def ovpEnable(self, enable=None):
        """ Set/query overvoltage protection (OVP) state.
            (VOLT:PROT:STAT 0|1 / VOLT:PROT:STAT?, confirmed - UI toggle
            labeled "OVP" in the vendor VEE driver)

            Note:
                It is not separately confirmed whether writing 0 here also
                clears an already-tripped state (no distinct "CLEar"
                command was found in the driver) - if OVP has tripped,
                writing 0 then 1 is a reasonable approach to test/attempt a
                reset.

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
            (SENS:VOLT:DET 0|1 / SENS:VOLT:DET?, confirmed - UI toggle
            labeled "Sensing" in the vendor VEE driver)

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
            (EXT 0|1 / EXT:STAT?, confirmed - UI toggle labeled "Extern" in
            the vendor VEE driver)

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


# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)

    def showError():
        """ show error message if an error is active on device """
        code, msg = psu._dev.query("SYST:ERR?", delay=0).split(",", maxsplit=1)
        code = int(code)
        if code != 0:
            print(f"> Device Error: [{code}] {msg}")

    try:

        psu = TOE8951(visa_address="ASRL5::INSTR") # substitute the actual COM port
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

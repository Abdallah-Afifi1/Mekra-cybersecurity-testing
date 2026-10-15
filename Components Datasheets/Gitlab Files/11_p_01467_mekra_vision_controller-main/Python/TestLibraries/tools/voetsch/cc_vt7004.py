#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : cc_vt4007.py
# Package : tools.voetsch
# Task    : Access to Vötsch VT4007 climatic test chambers via Ethernet
#           and "S!MPAC 1.x" protocol
#           Provides TTk variable abstractions for outputs/measurements.
#
# See also:
#          * Simpati Simserv Manual Simpati_Simserv_gb.pdf
#          * Simpati Manual (simpati_en 4.06)
#          * Vötsch VT4002 climate chamber (same older protocol)
#            https://lampz.tugraz.at/~hadley/num/ch9/instruments/VT4002/
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 10.06.2025 | Tremmel   | initial
# 1.1.0  | 16.06.2025 | Tremmel   | added optional limit check to SimVar.set 
# 1.1.1  | 03.08.2026 | Ehu Li    | added reachTemperature(): sets the setpoint and waits
#                                 | until the temperature reaches target
#******************************************************************************
"""
@package tools.voetsch.ctc_vt4007
Access to Vötsch VT4007 climatic test chambers via Ethernet and "S!MPAC 1.x"
protocol.
Provides TTk variable abstractions for outputs/measurements.
"""
import time
import select
import socket
import re
import threading
import serial

from enum import IntEnum
from collections import namedtuple
from datetime import datetime


from ttk_base.errors import TTkException
from ttk_base._variables_base import VarBase

def extract_temperature(uart_line: str) -> float | None:
        
        
    match = re.search(r'Celsius\s+([-+]?\d+(?:\.\d+)?)', uart_line)
    if match:
        return float(match.group(1))
    return None

    
from threading import Lock

socTemp = None
socTemp_lock = Lock()

socTemp_ready = threading.Event()
def uart_logger(port, baudrate, stop_event):
    global socTemp
    ser = serial.Serial(port, baudrate, timeout=1)
    while not stop_event.is_set():
        if ser.in_waiting:
            line = ser.readline().decode(errors="ignore")
            uart_temp = extract_temperature(line)

            if uart_temp is not None:
                with socTemp_lock:
                    socTemp = uart_temp
                socTemp_ready.set()
                #print("was los", uart_temp)

    ser.close()

    
def get_latest_soc_temp() -> float | None:
    with socTemp_lock:
        return socTemp

    
stop_event = threading.Event()

uart_thread = threading.Thread(
    target=uart_logger,
    args=("COM5", 115200, stop_event),
    daemon=True
)

uart_thread.start()

current_socTemp = None

separator      = "¶"  # separator character ("¶", ascii 182)
end_of_command = "\r" # end of command (carriage return, ascii 13)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Note: S!MPATI/SimServ documentation suggests that 
#     "It is not possible to open a permanent connection to the server. 
#      Therefore a server can operate with a lot of clients.
#
#      For each command the following terminate is to be used: 
#        1.  Open connection 
#        2.  Send command 
#        3.  Read response 
#        4.  Close connection"
#
# However, both the previous implementation and other approaches:
#    * https://github.com/SengerM/VotschTechnik-climate-chamber-Python
#    * https://github.com/IzaakWN/ClimateChamberMonitor
# seem to use a single permanently opened socket for multiple queries.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


# #############################################################################
class CommandError(TTkException):
    """ Error during command/query (usually due to an error response) """
    ## response error codes 
    error_codes = {
         1: "Success", # "In a fault-free case a “1” is returned."
        -1: "Empty command string",
        -2: "Missing Chamber ID", 
        -3: "Invalid Chamber ID",
        -4: "Chamber not accessible",
        -5: "Unknown Command ID",
        -6: "Insufficient number or incorrect command parameters",
        -7: "No server (in server service command mode)",
    }
    def __init__(self, msg, error_code=None):
        if error_code is not None:
            info = self.error_codes.get(error_code, '<undefined>')
            msg = f"{msg}\nError {error_code}: {info}"
        super().__init__(msg)



# #############################################################################
class Command(IntEnum):
    """ Command / Function number values for S!MPAC 1.x / S!MPATI* 
        TCP/IP-Interface communication
    """
    GET_CHAMBER_NAME        = 10006 # => CHAMBER NAME
    GET_CHAMBER_TYPE        = 10007 # => VÖTSCH 10001, WEISS DMR 20001
    
    GET_ERROR_COUNT         = 17002 # => Number of ERRORS
    GET_OPERATING_STATUS    = 10012 # => PRESENT 0x1 / RUN 0x2 / WARNING 0x4 / ERROR 0x8
    GET_OPERATING_MODE      = 10010 # => DATA LOGGING 0x01 / MANUAL 0x02 / AUTOMATIC 0x04 / PAUSE 0x08 / BUSY 0x10

    # control values ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # basics:
    SET_SETPOINT                = 11001 # CV-Idx  Value
    GET_SETPOINT                = 11002 # CV-Idx  => SOLLWERT 
    # SET_ACTUAL_VALUE          = 11003 # 
    GET_ACTUAL_VALUE            = 11004 # CV-Idx  => ISTWERT 

    # CV-Idx: "Control variable index" (usually 1 for type "temperature")

    CV_GET_NAME                 = 11026 # CV-Idx  => NAME 
    CV_GET_UNIT                 = 11023 # CV-Idx  => EINHEIT
    CV_GET_INPUT_LIMIT_MIN      = 11007 # CV-Idx  => MIN
    CV_GET_INPUT_LIMIT_MAX      = 11009 # CV-Idx  => MAX
    CV_GET_WARNING_LIMIT_MIN    = 11016 # CV-Idx  => MIN
    CV_GET_WARNING_LIMIT_MAX    = 11017 # CV-Idx  => MAX
    CV_GET_ALARM_LIMIT_MIN      = 11014 # CV-Idx  => MIN
    CV_GET_ALARM_LIMIT_MAX      = 11015 # CV-Idx  => MAX
    
    # set values ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SV_GET_NAME                 = 13011 # CV-Idx  => NAME 
    SV_GET_UNIT                 = 13010 # CV-Idx  => EINHEIT 
    SV_GET_SETPOINT             = 13005 # CV-Idx  => SOLLWERT 
    SV_SET_SETPOINT             = 13006 # CV-Idx  Value
    SV_GET_INPUT_LIMIT_MIN      = 13002 # CV-Idx  => MIN 
    SV_GET_INPUT_LIMIT_MAX      = 13004 # CV-Idx  => MAX 
    
    # measurement values ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    MV_GET_NAME                 = 12019 # CV-Idx  => NAME
    MV_GET_UNIT                 = 12016 # CV-Idx  => EINHEIT
    MV_GET_ACTUAL_VALUE         = 12002 # CV-Idx  => ISTWERT
    MV_GET_WARNING_LIMIT_MIN    = 12010 # CV-Idx  => MIN
    MV_GET_WARNING_LIMIT_MAX    = 12011 # CV-Idx  => MAX
    MV_GET_ALARM_LIMIT_MIN      = 12008 # CV-Idx  => MIN
    MV_GET_ALARM_LIMIT_MAX      = 12009 # CV-Idx  => MAX
    
    # digital channels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SET_DIGITALOUT  = 14001  # DigiNr  0/1   
    GET_DIGITALOUT  = 14003  # DigiNr       => DIGITALOUT (0/1)
    # SET_DIGITALIN = 15001  # DigiNr  0/1   
    GET_DIGITALIN   = 15002  # DigiNr       => DIGITALIN (0/1)


    def info(self):
        try:
            msg = Command(self).name
        except ValueError:
            msg = "<undefined>"
        return f"{msg} [{self}]"
    

## command specification form use with SimVar
# cmd: command/function number, see Command
# args: tuple with arguments
# limits: limits for set operations; a tuple (min, max) or None 
CmdSpec = namedtuple("CmdSpec", ("cmd", "args", "limits"), defaults=((), None))

# #############################################################################
class SimVar(VarBase):
    """ Wrapper for variables accessed via Simpac/Simserv protocol. 
        Uses sendRequest in parent context for data exchange.
    """
    
    # #########################################################################
    def __new__(cls, context, get_cmd, *args, **kwargs): # @UnusedVariable args, kwargs
        """ Create a custom instance of the immutable str type, on which 
            VarBase is based.
            Parameters:
                context - parent context, see __init__
                get_cmd - variable identifier, see __init__
        """
        # allow "get_cmd" in place of default "identifier"
        s = str.__new__(cls, get_cmd.cmd)
        return s
    
    
    # #########################################################################
    def __init__(self, context, get_cmd, set_cmd=None,
                 timeout_ms=None, value_conv=float,
                 
                 unit="", alias="", descr="", 
                 lookup=None, default=None, resettable=True, fmt=None):
        """ Parameters:
                context     - parent context (here: a VT7004 instance with a 
                              sendRequest method) 
                get_cmd     - CmdSpec entry to get a single value 
                set_cmd     - CmdSpec entry to set a single value
                timeout_ms  - custom timeout for command request/response in [ms]
                              None: use default
                value_conv  - value conversion function (to convert string 
                              response to a numeric representation)
                              Defaults to float.
                              
                unit        - (optional) unit string for the variable
                alias       - (optional) alias name, defaults to last (non-
                              default) entry in the identifier model path
                descr       - description for the variable
                lookup      - lookup dictionary for states {value => "state name"}
                default     - manually defined default value for the variable.
                              Will be used as "reset" value instead of the 
                              original value before the first set operation 
                              if set to anything but None.
                resettable  - enable/disable reset() for this variable. If set
                              to False, a call to reset() will be ignored.
                fmt         - format string or keyword to use for value 
                              representation, e.g. "%.2f" or "hex"
        """
        VarBase.__init__(
            self, context, get_cmd, 
            unit=unit, alias=alias, descr=descr, 
            lookup=lookup, default=default, 
            resettable=resettable, fmt=fmt
        )

        self.context = context
        assert hasattr(self.context, "sendRequest")
        self._conv = value_conv 
        self._timeout_ms = None

        if isinstance(timeout_ms, (int, float)) and timeout_ms > 0:
            self._timeout_ms = timeout_ms
        
        self._get_cmd = get_cmd
        self._set_cmd = set_cmd
        
        if self._set_cmd and self._set_cmd.limits:
            assert self._set_cmd.limits[0] <= self._set_cmd.limits[-1], \
                   "limits have to be specified in ascending order"
    
    # #########################################################################
    def get(self, *args, **kwargs):         # @UnusedVariable: *args, **kwargs
        """ Get the current value.
            Note: 
                Any specified parameters will be discarded 
            Returns the current value.
        """

        res_values = self.context.sendRequest(
            self._get_cmd.cmd,
            *self._get_cmd.args,
            timeout_ms = self._timeout_ms
        )
        ## last value of get/set operation
        self.last_value = self._conv(res_values[0])
        # basic response: first response value contains the read value
        return self.last_value
    
    # #########################################################################
    def set(self, value, *args, **kwargs):  # @UnusedVariable: *args, **kwargs
        """ Set a new value.
            Parameters:
                value - value to set
            Note:
                Any additional parameters will be discarded
            Returns the original value before the set operation occurred. 
        """
        if self._set_cmd is None:
            raise RuntimeError(f"Setting not is available for {self.alias}")
        
        prev_value = self.get()
        
        limits = self._set_cmd.limits
        if limits and len(limits) >= 2:
            if not (limits[0] <= value <= limits[-1]):
                raise ValueError(
                    f"Value {value!r} out of range for {Command.info(self._set_cmd.cmd)}. "
                    f"Expected range is [{limits[0]} .. {limits[-1]}]")
        
        # basic setter: first arguments specify target (e.g. output index, 
        # control value type), followed by the value to be set
        args = list(self._set_cmd.args) + [value]
        
        self.context.sendRequest(
            self._set_cmd.cmd,
            *args,
            timeout_ms = self._timeout_ms
        )
        
        if self.orig_value is None:
            ## original/reset value
            self.orig_value = prev_value
        
        # update last_value to the value that should be set 
        self.last_value = value
        
        return prev_value



# #############################################################################
class VT7004:
    """ Access Vötsch VT7004 temperature / climate test chambers. """

    MIN_TEMPERATURE = -72.0
    MAX_TEMPERATURE = 180.0

    # #########################################################################
    def __init__(self, ip_addr, port=2049, chamber_idx=1, timeout_ms=2000):
        """ Parameters:
                ip_addr     -  IP address of climate chamber
                port        -  Communication port of climate chamber. 
                               Default port for simpac 1.x communication is 2049
                chamber_idx - index of climate chamber (usually 1 for the first chamber)
                timeout_ms  - default request timeout in [ms]
                
        """
        self.ip_addr     = str(ip_addr)
        self.port        = int(port)
        self.chamber_idx = int(chamber_idx)
        self.timeout_ms  = abs(timeout_ms)

        ## close connection after each request (and re-open it as needed)
        # => SimServ documentation notes that "It is not possible to open
        #    a permanent connection to the server"
        # See note above
        self._close_connection_after_response = False

        self._socket = None
        self._connect()


        print("#" * 80)
        print(f" Vötsch VT7004 on {ip_addr}:{port}")
        try:
            values = self.sendRequest(Command.GET_CHAMBER_NAME )
        except CommandError as ex:
            print(f"> {ex}")
            self._disconnect()
        else:
            print(f"# {values[0]} ")
        print("#" * 80)


        # Variables ~~~~~~~~~~~~~~~~~~~~~--------------------------------------
        self.temperature_setpoint = SimVar(self, 
            get_cmd=CmdSpec(cmd=Command.GET_SETPOINT, args=[1]), # 1 => control value: temperature
            set_cmd=CmdSpec(cmd=Command.SET_SETPOINT, args=[1], limits=(self.MIN_TEMPERATURE, self.MAX_TEMPERATURE)),
            alias="temperature_setpoint", unit="°C", fmt="flt1", 
            descr="Temperature Setpoint")
        
        self.temperature = SimVar(self, 
            get_cmd=CmdSpec(cmd=Command.GET_ACTUAL_VALUE, args=[1]), # 1 => control value: temperature
            alias="temperature", unit="°C", fmt="flt1", 
            descr="Actual, current temperature of chamber")
    
    
    # #########################################################################
    def __del__(self):
        try:
            self.close() # final cleanup attempt
        except (AttributeError, NameError):
            pass # might already be gone
        
    def __str__(self):
        return (f"{self.__class__.__name__} Device @ {self.ip_addr}:{self.port}")


    # #########################################################################
    def _connect(self):
        """ connect to chamber """
        if not self._socket:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.ip_addr, self.port))
            self._socket.setblocking(0)
        
    def _disconnect(self):
        """ disconnect from chamber """
        if self._socket:
            self._socket.close()
            self._socket = None
        
    # #########################################################################
    def close(self):
        """ Close active connection """
        self._disconnect()

    # #########################################################################
    def sendRequest(self, cmd, *args, timeout_ms=None):
        """ Send a request and wait for a response
            Parameters:
                command    - "command/function number" see Command enum.
                *args      - list of command arguments (protocol uses 4 arguments max)
                timeout_ms - request timeout in [ms] (keyword-only)
                             None: use default delay from class member .timeout_ms
                
            Returns a tuple of string values (up to 4, according to documentation).
            Values are still strings, as decoding/type depends on the used command.
        """
        if timeout_ms is None:
            timeout_ms = self.timeout_ms 
            

        # build request
        
        # Request format:
        # <command> [sr] <chamber-index> [sr] <arg1> [sr] <arg2> [sr] <arg3> [sr] <arg4> [cr]
        # * [sr] - separator (¶)
        # * [cr] - end of command (\r)
        # * up to 4 arguments can be present, depending on used command
        parts = [str(cmd), str(self.chamber_idx)]
        parts.extend(str(arg) for arg in args)
        request = f"{separator.join(parts)}{end_of_command}"

        self._connect()
        
        # send request
        self._socket.sendall(request.encode("latin-1", errors="replace"))
        

        # wait for response to arrive
        ready_to_read, \
        _ready_to_write, \
        _in_error = select.select([self._socket],  # rlist
                                  [],              # wlist
                                  [],              # xlist
                                  timeout_ms)
        # Note: select.select() takes no keyword arguments
        if not ready_to_read:
            # a timeout occurred
            raise TimeoutError(f"Timeout occurred during {Command.info(cmd)}")


        values = []
        
        # response format:
        # <error-code> [sr] <value1> [sr] <value2> [sr] <value3> [sr] <value4> [cr]
        # * [sr] - separator (¶, same as in request)
        # * [cr] - end of command (\r, same as in request)
        # * up to 4 response values can be present [0..4]
        # * if an actual error code (i.e. not 1) is present, the response 
        #   should contain no additional values. 
        #    * i.e. <error-code> [cr]

        # receive response        
        # 2k buffer is more than enough to fit all relevant response message types
        
        response = self._socket.recv(2048) 
        # chunks = [b'']
        # while b"\r" not in chunks[-1] and len(chunks) < 2048:
        #     chunks.append(self._socket.recv(1))
        # response = b''.join(chunks)
        
        response = response.decode("latin-1", errors="replace") 
        response = response.rstrip(end_of_command)
        
        parts = response.split(separator)
        try:
            error_code = int(parts[0])
            if error_code != 1: # 1: "no error"
                raise CommandError(f"Command {Command.info(cmd)} failed.", 
                                   error_code=error_code)
                
            # otherwise we should have a valid response
            values = parts[1:]
            # ensure that at least the defined max. 4 values are present 
            # (for convenience during later processing)
            while len(values) < 4:
                values.append(None)
            
        except ValueError:
            # unable to decode error/status
            raise CommandError(f"Invalid response: {response!r}")
        
        finally:
            if self._close_connection_after_response:
                # simpac documentation insists on this order:
                #   1. Open connection 
                #   2. Send command 
                #   3. Read response 
                #   4. Close connection 
                self._disconnect()
        return tuple(values)
        
            
    # #########################################################################
    def manualMode(self, enabled=None):
        """ Set/query manual mode (by accessing digital out 1)
        
            Note:
                Setting digital out 1 to active is apparently necessary for 
                setting temperatures.
                
            Parameters
                enabled - True: enable manual mode
                          False : disable manual mode
                          None: keep mode as-is, just return current state
            Returns the current manual mode state
        """
        if enabled is not None:
            # set state of digital out 1 (only returns an success/error response)
            self.sendRequest(Command.SET_DIGITALOUT, 1, int(bool(enabled)))
        
        res_values = self.sendRequest(Command.GET_DIGITALOUT, 1)
        return bool(int(res_values[0]))


    # #########################################################################
    def getCurrentTemp(self):
        return self.temperature.get()
    def reachTemperature(self, target_temperature, target_accuracy=1.0,
                         timeout_s=90*60, poll_interval_s=60):
        """ Set a target temperature and wait until it is reached once.

            Parameters:
                target_temperature - desired target temperature in [°C]
                target_accuracy    - accuracy/tolerance for target temperature in [°C]
                timeout_s          - timeout in [s] for operation.
                                     A TimeoutError will be raised if the
                                     temperature has not been reached.
                poll_interval_s    - delay in [s] between two temperature readings

            Returns the elapsed time in [s] and the reached temperature in [°C].
        """
        # enable the climate chamber (via digital channel 1 ("Start"))
        self.manualMode(True)

        print(f"# Setting temperature {target_temperature:.1f} °C")
        self.temperature_setpoint.set(target_temperature)

        tolerance = abs(target_accuracy)
        start_time = time.time()

        while True:
            temperature = self.temperature.get()
            delta_s = time.time() - start_time

            if abs(temperature - target_temperature) < tolerance:
                print(f"# Target temperature reached after {delta_s:.1f}s")
                return delta_s, temperature

            if delta_s > timeout_s:
                print(f"...timeout after {delta_s:.1f}s")
                raise TimeoutError(
                    f"Timeout after {delta_s:.1f}s while waiting for "
                    f"temperature to reach {target_temperature:.1f} °C")

            print(f"{temperature:5.1f} ", end="", flush=True)
            time.sleep(poll_interval_s)
    
    
    
    def gotoTemperature(self, target_temperature, target_accuracy=0.2, 
                          settling_time_s=60, timeout_s=45*60):
        """ Set a target temperature and wait until is has been reached.

            Parameters:
                target_temperature - desired target temperature in [°C]
                target_accuracy    - accuracy/tolerance for target temperature in [°C]
                settling_time_s    - duration in [s]; how long the actual temperature
                                     has to stay within target±tolerance to be 
                                     considered as "settled"
                timeout_s          - timeout in [s] for operation. 
                                     A TimeoutError will be raised if temperature
                                     has not settled within timeout_s.
            
        """
        # enable the climate chamber (via digital channel 1 ("Start"))
        self.manualMode(True)

        print(f"# Setting temperature {target_temperature:.1f} °C")
        # set the new target temperature
        self.temperature_setpoint.set(target_temperature)

        stability_counter = 0
        tolerance = abs(target_accuracy)
        
        # wait until we reach the target temperature
        start_time = time.time()
        print(f"# Waiting for temperature to settle...")
        width = 0
        while True:
            delta_s = time.time() - start_time
            temperature = self.temperature.get()

            fmt_temp = f"{temperature:5.1f} "
            width += len(fmt_temp)
            print(fmt_temp, end="", flush=True)
            if width > 120:
                print()
                width = 0
                       
            # if we are within the target range increase the counter
            if abs(temperature - target_temperature) < tolerance:
                stability_counter += 1

                # done if the value is stable for long enough
                if stability_counter >= settling_time_s:
                    print("...ok")
                    print(f"# Target temperature reached after {delta_s:.1f}s")
                    break
            else:
                stability_counter = 0

            if delta_s > timeout_s:
                print(f"...timeout after {delta_s:.1f}s")
                raise TimeoutError(
                    f"Timeout after {delta_s:.1f}s while waiting for "
                    f"temperature to reach/settle at {target_temperature:.1f} °C")

            time.sleep(1)
            
    def gotoTemperatureContinuousData(self, target_temperature, count, power_supply, multimeter, target_accuracy=0.5, 
                          settling_time_s=60, timeout_s=45*60):
        """ Set a target temperature and wait until is has been reached.

            Parameters:
                target_temperature - desired target temperature in [°C]
                target_accuracy    - accuracy/tolerance for target temperature in [°C]
                settling_time_s    - duration in [s]; how long the actual temperature
                                     has to stay within target±tolerance to be 
                                     considered as "settled"
                timeout_s          - timeout in [s] for operation. 
                                     A TimeoutError will be raised if temperature
                                     has not settled within timeout_s.
            
        """
        delay = 30
        # enable the climate chamber (via digital channel 1 ("Start"))
        self.manualMode(True)

        print(f"# Setting temperature {target_temperature:.1f} °C")
        # set the new target temperature
        self.temperature_setpoint.set(target_temperature)

        stability_counter = 0
        tolerance = abs(target_accuracy)
        
        # wait until we reach the target temperature
        start_time = time.time()
        print(f"# Waiting for temperature to settle...")
        width = 0
        
        data = []
        
        while True:
            delta_s = time.time() - start_time
            temperature = self.temperature.get()

            fmt_temp = f"{temperature:5.1f} "
            width += len(fmt_temp)
            print(fmt_temp, end="", flush=True)
            if width > 120:
                print()
                width = 0
                
            zeit = str(str(datetime.now()).split(" ", 1)[1]).split(".")[0]
            spannung = float(str(power_supply.voltage_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
            strom = float(str(power_supply.current_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
            leistung = float(str(power_supply.power_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
            ccTemperature = round(self.getCurrentTemp(), 3)
            
            pt1000 = float(str(multimeter.temperature.info().split(" ", 1)[1]).split(" ", 1)[0])
            data.append([zeit, spannung, strom, leistung, ccTemperature, pt1000])
            print(zeit, spannung, strom, leistung, ccTemperature, pt1000)
            """
            pt1000 = 0.0
            data.append([zeit, spannung, strom, leistung, ccTemperature, pt1000])
            print(zeit, spannung, strom, leistung, ccTemperature, pt1000)
            """
            # if we are within the target range increase the counter
            
            #in case of camera failing (indicated by drop in leistung below 3W)
            #loop is ended 
            if leistung < 3:
                print("Leistung below 3W")
                return data
            
            if abs(temperature - target_temperature) < tolerance:
                #waiting for chip temp to be below 50 before starting
                #with further measurements
                if count == 0 and pt1000 > 150:
                    stability_counter = 0
                else:
                    stability_counter += 1

                # done if the value is stable for long enough
                if stability_counter >= settling_time_s:
                    print("...ok")
                    print(f"# Target temperature reached after {delta_s:.1f}s")
                    return data
            else:
                stability_counter = 0

            #if delta_s > timeout_s:
            #    print(f"...timeout after {delta_s:.1f}s")
            #    raise TimeoutError(
            #        f"Timeout after {delta_s:.1f}s while waiting for "
            #        f"temperature to reach/settle at {target_temperature:.1f} °C")

            #time.sleep(1)
            time.sleep(delay)

    def gotoTemperatureContinuousData2(self, target_temperature, count, power_supply, multimeter, target_accuracy=0.5, 
                          settling_time_s=60, timeout_s=45*60):
        """ Set a target temperature and wait until is has been reached.

            Parameters:
                target_temperature - desired target temperature in [°C]
                target_accuracy    - accuracy/tolerance for target temperature in [°C]
                settling_time_s    - duration in [s]; how long the actual temperature
                                     has to stay within target±tolerance to be 
                                     considered as "settled"
                timeout_s          - timeout in [s] for operation. 
                                     A TimeoutError will be raised if temperature
                                     has not settled within timeout_s.
            
        """
        delay = 30
        # enable the climate chamber (via digital channel 1 ("Start"))
        self.manualMode(True)

        print(f"# Setting temperature {target_temperature:.1f} °C")
        # set the new target temperature
        self.temperature_setpoint.set(target_temperature)

        stability_counter = 0
        tolerance = abs(target_accuracy)
        
        # wait until we reach the target temperature
        start_time = time.time()
        print(f"# Waiting for temperature to settle...")
        width = 0
        
        data = []
    
        while True:
            delta_s = time.time() - start_time
            temperature = self.temperature.get()

            fmt_temp = f"{temperature:5.1f} "
            width += len(fmt_temp)
            print(fmt_temp, end="", flush=True)
            if width > 120:
                print()
                width = 0
                
            zeit = str(str(datetime.now()).split(" ", 1)[1]).split(".")[0]
            spannung = float(str(power_supply.voltage_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
            strom = float(str(power_supply.current_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
            leistung = float(str(power_supply.power_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
            ccTemperature = round(self.getCurrentTemp(), 3)
            pt1000 = float(str(multimeter.temperature.info().split(" ", 1)[1]).split(" ", 1)[0])
            socTemp = get_latest_soc_temp()
            data.append([zeit, spannung, strom, leistung, ccTemperature, pt1000, socTemp])
            print(zeit, spannung, strom, leistung, ccTemperature, pt1000, socTemp)
            """
            pt1000 = 0.0
            data.append([zeit, spannung, strom, leistung, ccTemperature, pt1000])
            print(zeit, spannung, strom, leistung, ccTemperature, pt1000)
            """
            # if we are within the target range increase the counter
            
            #in case of camera failing (indicated by drop in leistung below 3W)
            #loop is ended 
            if leistung < 3:
                print("Leistung below 3W")
                stop_event = threading.Event()
                return data
            
            if abs(temperature - target_temperature) < tolerance:
                #waiting for chip temp to be below 50 before starting
                #with further measurements
                if count == 0 and pt1000 > 150:
                    stability_counter = 0
                else:
                    stability_counter += 1

                # done if the value is stable for long enough
                if stability_counter >= settling_time_s / delay:
                    print("...ok")
                    print(f"# Target temperature reached after {delta_s:.1f}s")
                    stop_event = threading.Event()
                    return data
            else:
                stability_counter = 0

            #if delta_s > timeout_s:
            #    print(f"...timeout after {delta_s:.1f}s")
            #    raise TimeoutError(
            #        f"Timeout after {delta_s:.1f}s while waiting for "
            #        f"temperature to reach/settle at {target_temperature:.1f} °C")

            #time.sleep(1)
            time.sleep(delay)

# #############################################################################
if __name__ == "__main__":
    cmd = Command.CV_GET_INPUT_LIMIT_MAX
    print(f"{cmd}", cmd, cmd.info(), Command(cmd).info())
    
   
    try:
        cc = VT7004(ip_addr="192.168.10.40")
        
        # print(cc.get_nominal_temperature())
        # print(cc.get_actual_temperature())
        
        print(f"{cc.manualMode(True) = }")
        print(f"{cc.manualMode() = }")
        for value in range(21):
            print()
            cc.temperature_setpoint.set(value)
            print(cc.temperature_setpoint.info())
            print(cc.temperature.info())
            
        #cc.gotoTemperature(180, settling_time_s=2)
        cc.gotoTemperature(+40, settling_time_s=2)
        cc.gotoTemperature(-10, settling_time_s=2)
        
        print(f"{cc.manualMode(False) = }")
        print(f"{cc.manualMode() = }")
        
    finally:
        cc.close()
    
    print("Done.")
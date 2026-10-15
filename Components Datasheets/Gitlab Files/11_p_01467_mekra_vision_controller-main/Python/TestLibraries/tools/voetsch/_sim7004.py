#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : _sim4007.py
# Package : tools.voetsch
# Task    : Basis protocol simulation for Vötsch VT4007 climatic test chambers
#           ("S!MPAC 1.x"/simserv protocol)
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 16.06.2025 | Tremmel   | moved protocol simulation to separate module
#******************************************************************************
"""
@package tools.voetsch._sim4007
Basis protocol simulation for Vötsch VT4007 climatic test chambers
(using "S!MPAC 1.x"/simserv protocol)

Supported commands:
    * GET_DIGITALOUT/SET_DIGITALOUT
    * GET_SETPOINT/SET_SETPOINT 
    * GET_ACTUAL_VALUE 
        * primarily for control value type 1 (temperature)
        * reported value will change over time to approach its 
          corresponding SETPOINT value

"""
import time
from tools.voetsch.cc_vt7004 import Command
from tools.voetsch.cc_vt7004 import separator, end_of_command


DATA = {
    "ACTUAL_VALUE#1": 20.0, # default "actual" temperature (control value type 1)
}
DATA_LAST_CHANGED = {
}

ACTUAL_VALUE_INCR = .4 # increment per second (e.g. 0.4 °C/s)
ACTUAL_VALUE_DECR = .2 # decrement per second (e.g. 0.2 °C/s)


# #############################################################################
def handleSimpacCommand(request):
    """ handle a Simpac request/command
        Parameters:
            request - a Simpac request string
        Returns a Simpac response string
    """
    data = request.rstrip(end_of_command)
    parts = data.split(separator)
    print(f"-> {parts!r}")

    response = "-1\r" # "Empty command string "
    res_success = "1\r" # "success"
    try:
        cmd, chamber_idx, arg1, arg2, arg3, arg4 = (parts + [None] * 6)[:6]
        cmd = int(cmd)
        chamber_idx = int(chamber_idx) if chamber_idx is not None else 0
        
        print("[command]", Command.info(cmd))
        print("[chamber]", chamber_idx)
        print("[args]   ", ", ".join(str(a) for a in (arg1, arg2, arg3, arg4) if a is not None))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if cmd == Command.SET_DIGITALOUT: 
            # arg1: port index 
            # arg2: value to set
            DATA[f"DIGITALOUT#{arg1}"] = int(arg2)
            DATA_LAST_CHANGED[f"DIGITALOUT#{arg1}"] = time.time()
            response = res_success
            
        elif cmd == Command.GET_DIGITALOUT:
            # arg1: port index
            value = DATA.get(f"DIGITALOUT#{arg1}", 0)
            response = f"1¶{value}\r"
            
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        elif cmd == Command.SET_SETPOINT:
            # arg1: control value type (1: temperature, 2: depends...)
            # arg2: value to set
            DATA[f"SETPOINT#{arg1}"] = int(arg2)
            DATA_LAST_CHANGED[f"SETPOINT#{arg1}"] = time.time()
            response = res_success
            
        elif cmd == Command.GET_SETPOINT:
            # arg1: control value type (1: temperature, 2: depends...)
            value = DATA.get(f"SETPOINT#{arg1}", 0)
            response = f"1¶{value}\r"
            
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            
        elif cmd == Command.GET_ACTUAL_VALUE:
            # arg1: control value type (1: temperature, 2: depends...)
            value = DATA.get(f"ACTUAL_VALUE#{arg1}", 0)
            
            timestamp = time.time()
            setpoint_changed = DATA_LAST_CHANGED.get(f"SETPOINT#{arg1}", timestamp)
            setpoint_value   = DATA.get(f"SETPOINT#{arg1}", value)
            
            print(f"# actual: {value}, target {setpoint_value}")
            delta_value = setpoint_value - value
            delta_time = max(0, timestamp - setpoint_changed)
            
            
            if delta_value > 0.001: # value below setpoint
                print(f"# => incrementing...")
                value_change = delta_time * abs(ACTUAL_VALUE_INCR) # increment/s
                value = min(setpoint_value, value + value_change)

            elif delta_value < 0.001: # value above setpoint
                print(f"# => decrementing...")
                value_change = delta_time * abs(ACTUAL_VALUE_DECR) # decrement/s
                value = max(setpoint_value, value - value_change)
            
            DATA[f"ACTUAL_VALUE#{arg1}"] = value
            response = f"1¶{value:.3f}\r"
            
        elif cmd == Command.GET_CHAMBER_NAME:
            response = f"1¶Simserv7004-Mock\r"
            
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        else:
            response = "-5\r" # "Unknown Command-ID"
            
    except Exception as ex:
        print(f"> {type(ex).__name__}: {ex}")
        response = "-6\r" # invalid command parameters  
    
    print("[data]")
    for name, value in DATA.items():
        print(f"  {name:<16} -> {value}")
        
    return response
     
        
# #############################################################################
if __name__ == "__main__":
    print("Done.")
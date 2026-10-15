#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : debugger.py
# Package : ttk_tools.pyocd
# Task    : Access to PyOCD sessions
# Type    : Interface
# Python  : 3.8+
#
# Copyright 2022, 2023 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 24.02.2022 | J.Tremmel | interface to pyocd._debugger v1.1.0
#******************************************************************************
""" 
@package ttk_tools.pyocd.debugger
Access to PyOCD session, provides attaching to running controllers and 
read/write of variables via debug symbols.

Requirements:
    * installed pyocd package:  
      pip install pyocd
      
Notes:
    * some dependencies might be missing:
        * ModuleNotFoundError: No module named 'importlib_metadata'
          pip install importlib-metadata
          
    * debugger target might not be supported in the base release, e.g. 
      "Target type stm32f407vgtx not recognized"
      See https://github.com/pyocd/pyOCD/blob/master/docs/target_support.md
      for how to install additional target support.
        * additional target packs can be installed:  
          pyocd pack install stm32f407vgtx  
          pyocd pack install stm32h743zitx  
        
    * ST-Link-Firmware has to be recent-ish
        *  V2.J37.M26 seems to work 
        
"""
import os

# "Target type stm32f407vgtx not recognized"
# See https://github.com/pyocd/pyOCD/blob/master/docs/target_support.md
# for how to install additional target support.

# pyocd pack install stm32f407vgtx
# (many warnings later...)
# > Downloading packs (press Control-C to cancel):
# >    Keil.STM32F4xx_DFP.2.16.0

# ST-Link-Firmware has to be recent-ish
# (got errors with stock firmware on STM32F4DISCOVERY dev board)
# V2.J37.M26 seem to work so far

from ttk_tools.pyocd import _debugger # @UnresolvedImport (compiled extension)
from ttk_tools.pyocd._debugger import SymbolNotFound  # @UnresolvedImport @UnusedImport, for interface parity


# #############################################################################
class Debugger(_debugger.Debugger):
    """ Wrapper for a PyOCD session and utility methods.
        Debugger session will be connected to running system in "attach" mode.
     """
    
    # #########################################################################
    def __init__(self, elf_file_path):
        """ Note:
                Currently connects to the first detected probe
            
            Parameters:
                elf_file_path  - path to ELF file with debug symbols 
        """
        super().__init__(elf_file_path)
 
    # #########################################################################
    def connect(self):
        """ Connect to target (open session) """
        super().connect()
        
    # #########################################################################
    def disconnect(self):
        """ Disconnect from target (close session). """
        super().disconnect()
    
    # #########################################################################
    def getAddress(self, symbol):
        """ Get memory address of an object on the ELF symbol table.
            
            Parameters:
                symbol - symbol name string
                
            Note:
                PyOCD's symbol provider can only resolve base addresses 
                (start address of arrays, structs, ...)
                
            Returns a memory address (or raises a SymbolNotFound exception)
        """
        return super().getAddress(symbol)
         
    # #########################################################################
    def read_uint8(self, addr):
        """ Read uint8 value at `addr`. """
        return super().read_uint8(addr)
    
    def read_uint16(self, addr):
        """ Read uint16 value at `addr`. """
        return super().read_uint16(addr)

    def read_uint32(self, addr):
        """ Read uint32 value at `addr`. """
        return super().read_uint32(addr)
    
    def read_uint64(self, addr): 
        """ Read uint64 value at `addr`. Not supported on 32bit SOCs.
        """
        return super().read_uint64(addr)
    
    # #########################################################################
    def read_sint8(self, addr):
        """ Read sint8 value at `addr`. """
        return super().read_sint8(addr)
    
    def read_sint16(self, addr):
        """ Read sint16 value at `addr`. """
        return super().read_sint16(addr)
    
    def read_sint32(self, addr):
        """ Read sint32 value at `addr`. """
        return super().read_sint32(addr)
    
    def read_sint64(self, addr): 
        """ Read sint64 value at `addr`. Not supported on 32bit SOCs. """
        return super().read_sint64(addr)
        
    # #########################################################################
    def read_float32(self, addr):
        """ Read 32bit float value ("single") at `addr`."""
        return super().read_float32(addr)
    
    def read_float64(self, addr): 
        """ Read 64bit float value ("double") at `addr`. 
            Not supported on 32bit SOCs. 
        """
        return super().read_float64(addr)
    
    
    # #########################################################################
    def write_uint8(self, addr, value):
        """ Write uint8 `value` to `addr`. """
        super().write_uint8(addr, value)
    
    def write_uint16(self, addr, value):
        """ Write uint16 `value` to `addr`. """
        super().write_uint16(addr, value)

    def write_uint32(self, addr, value):
        """ Write uint32 `value` to `addr`. """
        super().write_uint32(addr, value)
    
    def write_uint64(self, addr, value): 
        """ Write uint64 `value` to `addr`. Not supported on 32bit SOCs. """
        super().write_uint64(addr, value)
        

    # #########################################################################
    def write_sint8(self, addr, value):
        """ Write sint8 `value` to `addr`. """
        super().write_sint8(addr, value)
    
    def write_sint16(self, addr, value):
        """ Write sint16 `value` to `addr`. """
        super().write_sint16(addr, value)
    
    def write_sint32(self, addr, value):
        """ Write sint32 `value` to `addr`. """
        super().write_sint32(addr, value)
    
    def write_sint64(self, addr, value): 
        """ Write sint64 `value` to `addr`. Not supported on 32bit SOCs. """
        super().write_sint64(addr, value)

    # #########################################################################
    def write_float32(self, addr, value):
        """ Write 32bit float `value` ("single") to `addr`.
            Note: Not supported on 32bit SOCs.
        """
        super().write_float32(addr, value)
        
    def write_float64(self, addr, value): 
        """ Write 64bit float `value` ("double") to `addr`.
            Not supported on 32bit SOCs.
        """
        super().write_float64(addr, value)


# #############################################################################
# @cond DOXYGEN_IGNORE 
# #############################################################################
if __name__ == '__main__':  # pragma: no cover (contains only sample code)
    import time
    from pyocd.core.helpers import ConnectHelper
    ConnectHelper.list_connected_probes()
    print()
    
    elf_path = r"D:\temp\Debugger Test\STM32F4_DebuggerTest\Debug\STM32F4_DebuggerTest.elf"
    #elf_path = r"D:\temp\Debugger Test\TIM_TimeBase\SW4STM32\STM32H743ZI-Nucleo\Debug\TIM_TimeBase.elf"
    
    d = Debugger(elf_path)
    try:
        d.connect()

        symbol = "uwTick"
        symbol = "u32testVar" # counts up if button is pressed


        addr = d.symbol_provider.get_symbol_value(symbol)
        if addr is None:
            print(f"> Symbol {symbol!r} n/a in {os.path.basename(elf_path)}")
        else:
            for i in range(32):
                time.sleep(0.1)
                print(f"[{i:03d}] {symbol}:", d.read_uint32(addr))
        
        # addr = d.symbol_provider.get_symbol_value("s32testVar")
        # print(d.read_sint32(addr))
        # d.write_sint32(addr, -4711)
        # print(d.read_sint32(addr))
        #
        # addr = d.symbol_provider.get_symbol_value("f32testVar")
        # print(d.read_float32(addr))
        # d.write_float32(addr, 123.456789)
        # print(d.read_float32(addr))
        #

        print("# Symbols:")
        for key, sym in sorted(d.symbol_provider._symbols.symbol_dict.items()):
            
            if sym.type == "STT_OBJECT":
                if sym.size > 0:
                    #print(f"  {key:<24} --> {sym}")
                    print(f"  {key:<24} --> {sym.name} @ 0x{sym.address:08X} | {sym.size} Bytes")
                else:
                    # size 0: some frame start addresses
                    print(f"# {key:<40} --> {sym.name} @ 0x{sym.address:08X} | {sym.size} Bytes")
                    
            elif sym.type == "STT_FUNC":
                # functions: ignore
                pass
            else:
                # just in case
                print(f"  {key:<24} -->", sym)
    finally:
        d.disconnect()
        
    print("Done.")
    
    # https://github.com/pyocd/pyOCD/issues/1148
    # Memory Transfer Fault connecting to STM32H743ZI2 #1148 
    
    
# @endcond DOXYGEN_IGNORE
# #############################################################################

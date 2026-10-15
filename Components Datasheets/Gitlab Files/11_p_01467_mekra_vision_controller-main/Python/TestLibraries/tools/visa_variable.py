#******************************************************************************
# -*- coding: utf-8 -*-
# File   : visa_variable.py
# Package: tools
# Task   : 
# Python : 3
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 12.05.2025 | JoTremmel  | initial
# 1.1.0  | 19.05.2025 | JoTremmel  | added scpi command error handling
#******************************************************************************
"""
@package tools.visa_variable
Base classes for abstracted variables using a VISA interface 
"""
from collections import namedtuple

from pyvisa import VisaIOError
from pyvisa.constants import VI_ERROR_TMO

from ttk_base.errors import TTkException
from ttk_base._variables_base import VarBase


## An error entry (from SYSTem:ERRor[:NEXT]?)
#     SYSTem:ERRor?  => -113,"Undefined header;foobar"
#  => ScpiError(code=-113, msg="Undefined header;foobar")
#
# SCPI - Volume 1 - Syntax and Style - scpi-99.pdf
# 21.8 :ERRor Subsystem
# "The <Error/event_number> is a unique integer in the range [-32768, 32767]. 
#  All positive numbers are instrument-dependent. 
#  All negative numbers are reserved by the SCPI standard with certain 
#  standard error/event codes described in this document. 
#  The value, zero, is also reserved to indicate that no error or event 
#  has occurred."
# 
# "The second parameter of the full response is a quoted string containing 
#  an <Error/event_description> followed by optional <Device-dependent info> 
#  text. Each <Error/event_number> has a unique and fixed <Error/event_description> 
#  associated with it."
ScpiError = namedtuple('ScpiError', ['code', 'msg'])

# #############################################################################
class ScpiCommandError(TTkException):
    """ Command errors reported by the connected device.
        See ScpiError
    """
    def __init__(self, visa_errors: list):
        """ Parameters:
                visa_errors - list of ScpiError tuples (at least one), 
                              with the most recent error first
        """
        assert len(visa_errors) > 0
        self.visa_errors = tuple(visa_errors)
       
        ## use most recent error as primary message
        super().__init__(self.visa_errors[0].msg)
    
    @property
    def _all_messages(self):
        info = []
        for error in self.visa_errors:
            info.append(f"[{error.code}] {error.msg}")
        return "\n".join(info)
        
        
    def __str__(self):
        return self._all_messages

# #############################################################################
def checkCommandErrors(dev):
    """ Check error/event queue of device and raise a ScpiCommandError 
        exception if errors are present.
        Parameters:
            dev       - pyvisa device resource
    """
    scpi_errors = []
    while True:
        info = dev.query("SYSTem:ERRor?", delay=0)
        # Note: Siglent DMM does not support SYST:ERR:ALL?)
        code, msg = info.split(",", maxsplit=1)
        # whitespace after the comma separator is optional 
        # msg may also contain a trailing newline
        code, msg = int(code), msg.strip('" \r\n\t') 
        if code == 0: # defined "No Error"
            break
        # Note: msg could be further divided into 
        #       "<error/event descr>;<device dependent info>"
        #       or even
        #       "<error/event descr>;<device dependent info>;<date time>"
        #       (additional info are all optional, though)
        scpi_errors.append(ScpiError(code, msg))
        
    if scpi_errors:
        raise ScpiCommandError(scpi_errors)
           
def checkedQuery(dev, command, delay=None):
    """ Device/instrument query (write + read) with explicit error check 
        after command write.
        Parameters:
            command - scpi command/message to send
            delay   - custom delay in [s] between write and read
                      None: use default delay from pyvisa resource   
                      
        Returns a string response.
    """
    # Note: pyvisa's query() convenience function is literally just 
    #       * write(command) 
    #       * an optional query_delay (via time.sleep) and  
    #       * read() 
    #       See pyvisa.resources.messagebased
    # However, if a query (a write that requires a following read) did _not_ 
    # cause an error, reading the error queue before trying to read the original
    # response will cause the query to be interrupted (i.e. -410 Query interrupted)
    
    response = None
    try:
        response = dev.query(command, delay=delay)
    except VisaIOError as ex:
        if ex.error_code == VI_ERROR_TMO: # timeout
            # try to raise a more specific error
            checkCommandErrors(dev)
            # or fall back to timeout if no error entry was found  
            raise
        
        else:
            # re-raise all non-timeout errors
            raise
    else:
        # just in case a query caused an error but still provided a response
        checkCommandErrors(dev)
        
    return response
    



# #############################################################################
class VisaVar(VarBase):
    """ Simple wrapper for VISA/SCPI-based variables.
        Uses a PyVISA Resource instance for variable access.
    """
    
    # #########################################################################
    def __new__(cls, context, get_cmd, *args, **kwargs): # @UnusedVariable args, kwargs
        """ Create a custom instance of the immutable str type.
            
            Parameters:
                context - parent context, see __init__
                get_cmd - variable identifier, see __init__
        """
        # allow "get_cmd" in place of default "identifier"
        s = str.__new__(cls, get_cmd)
        return s
    
    
    # #########################################################################
    def __init__(self, context, get_cmd, set_cmd=None,
                 query_delay=None, value_conv=float,
                 
                 unit="", alias="", descr="", 
                 lookup=None, default=None, resettable=True, fmt=None):
        """ Parameters:
                context     - parent context (here: a VISA resource instance,
                              optionally a parent with a VISA resource instance 
                              as member ._dev) 
                get_cmd     - VISA command to get a single value 
                set_cmd     - VISA command to set a single value
                query_delay - delay in [s] for VISA queries (enforced time between write and read)
                              None: use default delay configured for device/resource
                value_conv  - value conversion function (to convert scpi string 
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
        self._dev = getattr(context, "_dev", context)

        assert hasattr(self._dev, "write")
        assert hasattr(self._dev, "query")
        # Note: pyvisa's query() convenience function is literally just 
        #       * write(command) 
        #       * an optional query_delay (via time.sleep) and  
        #       * read() 
        
        self._conv = value_conv 
        
        self._query_delay = None
        if isinstance(query_delay, (int, float)) and query_delay > 0:
            self._query_delay = query_delay

        
        self._get_cmd = get_cmd
        self._set_cmd = set_cmd
    
    # #########################################################################
    def get(self, *args, **kwargs):         # @UnusedVariable: *args, **kwargs
        """ Get the current value.
            
            Note: 
                Any specified parameters will be discarded 
            
            Returns the current value.
        """
        # self.last_value = float(self._dev.query(self._get_cmd, delay=self._query_delay))
        ## last value of get/set operation
        self.last_value = self._conv(checkedQuery(self._dev, self._get_cmd, 
                                                  delay=self._query_delay))
        return self.last_value
    
    # #########################################################################
    def set(self, value, *args, **kwargs):  # @UnusedVariable: *args, **kwargs
        """ Set a value to the SCPI/VISA variable.
            
            Parameters:
                value - value to set
            
            Note:
                Any additional parameters will be discarded
            Returns the original value before the set operation occurred. 
        """
        if self._set_cmd is None:
            raise RuntimeError(f"Setting not is available for {self.alias}")
        
        # TODO: make get-before-set optional?
        prev_value = self.get()
        self._dev.write(self._set_cmd.format(value=value)) 
        checkCommandErrors(self._dev)
        
        if self.orig_value is None:
            ## original/reset value
            self.orig_value = prev_value
        
        # update last_value to the value that should be set 
        self.last_value = value
        
        return prev_value



    
# #############################################################################
if __name__ == '__main__': # pragma: no cover (main contains only sample code)
    pass


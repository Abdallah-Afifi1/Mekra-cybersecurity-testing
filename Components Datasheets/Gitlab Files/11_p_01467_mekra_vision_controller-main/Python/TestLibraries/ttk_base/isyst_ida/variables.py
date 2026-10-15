#******************************************************************************
# -*- coding: utf-8 -*-
# File    : variables.py
# Package : ttk_base.isyst_ida
# Task    : Base classes for HIL variables using iDA Testware
#
#           This serves as "interface" to precompiled modules in delivery 
#           to enable code-completion in PyDev.
#
# Type    : Interface
#
# Copyright 2021 - 2023 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Author    | Description
#------------------------------------------------------------------------------
# 1.0.0  | 08.12.2021 | J.Tremmel | initial
# 1.1.0  | 04.07.2023 | J.Tremmel | package name updated
# 1.1.1  | 26.09.2023 | J.Tremmel | fixed package name in header
#******************************************************************************
"""
@package ttk_base.isyst_ida.variables
Wrapper classes for iDA-Testware-based HIL variables to provide a unified 
interface and containers to group variables into sets.

This serves as "interface" to the precompiled module in delivery to permit 
better code-analysis and code-completion in PyDev.
"""
from ttk_base.isyst_ida import _variables # @UnresolvedImport (compiled extension)


# #############################################################################
class Var(_variables.Var):
    """ Simple wrapper for iDA Testware "HIL" application variables. """
    # #########################################################################
    def __init__(self, context, identifier, unit="", alias="", descr="", 
                 lookup=None, default=None, resettable=True, fmt=None):
        """ iDA-Variable initialization.
            
            Parameters:
                context     - parent context (here: an IdaTestware or MwAppRpc instance) 
                identifier  - variable identifier: model path 
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
        _variables.Var.__init__(
            self, context, identifier, 
            unit=unit, alias=alias, descr=descr, 
            lookup=lookup, default=default, 
            resettable=resettable, fmt=fmt
        )
    
    # #########################################################################
    def get(self, *args, **kwargs):
        """ Get the current value of the application / model variable.
            
            Note: 
                Any specified parameters will be discarded (iDA's read 
                implementation does not handle any additional parameters)
            
            Returns the current value.
        """
        return _variables.Var.get(self, *args, **kwargs)
    
    # #########################################################################
    def set(self, value, *args, **kwargs):
        """ Set a value to the application / model variable. 
            
            Parameters:
                value - value to set
            
            Note:
                Any additional parameters will be discarded (iDA's write 
                implementation does not support any additional parameters)
            
            Returns the original value before the set operation occurred.
        """
        return _variables.Var.set(self, value, *args, **kwargs)
    
    # #########################################################################
    def getState(self):
        """ Get a textual state for the variable's current data. This uses 
            the lookup values supplied in constructor.
            
            Returns a textual state description (if available) or the unmapped 
            value (if no matching state was found).
        """
        return _variables.Var.getState(self)
    
    # #########################################################################
    def setState(self, state):
        """ Set a textual state to the variable. This uses the lookup values 
            supplied in constructor.
            Fallback (if no matching state text was found) will be the
            unmapped input state.
            
            Parameters:
                state - named state to set
            
            Returns the previously set state (if possible, otherwise the 
            previous unmapped value, see getState)
        """
        return _variables.Var.setState(self, state)
    
    # #########################################################################
    def reset(self, verbosity=1):
        """ Reset the variable to its initial value (default value specified
            in constructor or value before the first set() call).
            
            Parameters:
                verbosity - verbosity of log output.  
                            0: silent,  
                            1: show calls to non-resettable variables  
                            2: show all reset calls  
            
            Returns the original value (which may be None if the variable has
            not been set before)
        """
        return _variables.Var.reset(self, verbosity)
    
    # #########################################################################
    def info(self):
        """ Get an info string for this variable (alias and current value plus 
            unit and lookup value, if available). 
            
            Example:
                >>> print voltage_var.info()
                MW-Var Name: 12 V
                >>> print status_var.info()
                Status Var Name: 1 (valid)
            
            Returns a formatted string.
        """
        return _variables.Var.info(self)
        

# #############################################################################
# Container
# #############################################################################
class VarContainer(_variables.VarContainer):
    """ Base class for iDA Testware "HIL" variable containers. """
    
    # #########################################################################
    def __init__(self, ida):
        """ Parameters:
                ida  -  IdaTestware (or MwAppRpc) instance (will be used 
                        in constructors of iDA-based HIL variables)
        """
        _variables.VarContainer.__init__(self, ida)
    
    # #########################################################################
    def resetAll(self, verbosity=1, recursion_depth=4):
        """ Call reset() on all contained variables that support it. 
            
            Info:
                Variables will be reset in an arbitrary order (first found, 
                first reset).
                It might therefore be preferable to mark all variables used in 
                DUT's startup/shutdown sequences (like power supply settings, 
                KL30, KL15, ...) as not "resettable" in order to get a more
                predictable behavior. 
            
            Parameters:
                verbosity       - verbosity of debug/log messages.
                                    0: silent,
                                    1: plain info,
                                    2: +var names,
                                    3: overkill
                
                recursion_depth - how "deep" to recurse into lists/dictionary
                                  structures when looking for variables to 
                                  reset. 
        """
        _variables.VarContainer.resetAll(
            self, verbosity=verbosity, recursion_depth=recursion_depth
        )
        

# #############################################################################
# @cond DOXYGEN_IGNORE
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    pass
# @endcond DOXYGEN_IGNORE #####################################################

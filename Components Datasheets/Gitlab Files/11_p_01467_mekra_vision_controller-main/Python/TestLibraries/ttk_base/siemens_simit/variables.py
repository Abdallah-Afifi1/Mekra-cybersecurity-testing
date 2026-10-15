#******************************************************************************
# -*- coding: utf-8 -*-
# File    : variables.py
# Package : ttk_base.isyst_mw
# Task    : Base classes for variables using SIMIT SHM Coupling signals
#
#           This serves as "interface" to precompiled modules in delivery 
#           to enable code-completion in PyDev.
#
# Type    : Interface
#
# Copyright 2023 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Author    | Description
#------------------------------------------------------------------------------
# 1.0.0  | 14.07.2023 | J.Tremmel | initial
#******************************************************************************
"""
@package ttk_base.isyst_ida.variables
Wrapper classes for variables using SIMIT SHM Coupling signals to provide a 
unified interface and containers to group variables into sets.

This serves as "interface" to the precompiled module in delivery to permit 
better code-analysis and code-completion in PyDev.
"""
from ttk_base.siemens_simit import _variables # @UnresolvedImport (compiled extension)


# #############################################################################
class Var(_variables.Var):
    """ Simple wrapper for SIMIT SHM Coupling variables. """
    # #########################################################################
    def __init__(self, context, identifier, unit="", alias="", descr="", 
                 lookup=None, default=None, resettable=True, fmt=None):
        """ SIMIT-SHM-Variable initialization.
            
            Parameters:
                context     - parent context (here: a SimitShm instance, 
                              see ttk_tools.siemens.simit_shm) 
                identifier  - variable/signal identifier/name
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
                Any specified parameters will be discarded (the SimitSignal
                read implementation does not handle any additional parameters)
            
            Returns the current value.
        """
        return _variables.Var.get(self, *args, **kwargs)
    
    # #########################################################################
    def set(self, value, *args, **kwargs):
        """ Set a value to the application / model variable. 
            
            Parameters:
                value - value to set
            
            Note:
                Any additional parameters will be discarded (the SimitSignal 
                write implementation does not support any additional parameters)
            
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
        return _variables.Var.getState(self) # @UndefinedVariable (in compiled extension)
    
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
        return _variables.Var.setState(self, state) # @UndefinedVariable (in compiled extension)
    
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
        return _variables.Var.reset(self, verbosity) # @UndefinedVariable (in compiled extension)
    
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
        return _variables.Var.info(self) # @UndefinedVariable (in compiled extension)
        

# #############################################################################
# Container
# #############################################################################
class VarContainer(_variables.VarContainer):
    """ Base class for SIMIT SHM coupling signal variable containers. """
    
    # #########################################################################
    def __init__(self, simshm):
        """ Parameters:
                simshm  -  SimitShm instance (will be used in constructors of 
                           SimitSignal-based variables)
        """
        super().__init__(simshm)
    
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
    #pass
    from ttk_tools.siemens.simit_shm import SimitShm
        
    class SimitVars(VarContainer):
        def __init__(self, simshm):
            super().__init__(simshm)
            self.f32_OUT3 = Var(simshm, "f32_OUT3", fmt="flt2")

    try:
        shm = SimitShm("SIMIT_SHM")
        
        svars = SimitVars(shm)
        
        print(svars.f32_OUT3.info())
        svars.f32_OUT3.set(33.3)
        print(svars.f32_OUT3.info())
        svars.f32_OUT3.reset()
        print(svars.f32_OUT3.info())
        
        print(svars.s32_OUT2.info())
        svars.s32_OUT2.set(1024)
        print(svars.s32_OUT2.info())
        svars.s32_OUT2.reset()
        print(svars.f32_OUT3.info())
        
        # use a Python-incompatible signal name on-the-fly
        var = getattr(svars, "f32 OUT9 with a free-form name")
        print(var.info())
        var.set(1024)
        print(var.info())
        var.reset()
        print(var.info())
    finally:
        shm.exit()
    
# @endcond DOXYGEN_IGNORE #####################################################

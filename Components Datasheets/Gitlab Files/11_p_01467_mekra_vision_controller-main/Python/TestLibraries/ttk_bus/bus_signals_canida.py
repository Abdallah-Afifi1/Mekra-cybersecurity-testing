#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : bus_signals_canida.py
# Package : ttk_bus
# Task    : Wrapper classes for bus/interface signal descriptions.
#           Specific implementation for iDA-Blockset based CAN interfaces
# Type    : Interface
# Python  : 3.6+
#
# Copyright 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Author    | Description
#------------------------------------------------------------------------------
# 1.0.0  | 14.06.2024 | J.Tremmel | initial, interface to _bus_signals_canida v1.0.1
#******************************************************************************
"""
@package ttk_bus.bus_signals_canida
Interface wrapper bus/interface signal classes in ttk_bus._bus_signals_canida.
Specific implementation for iDA-Blockset based CAN interfaces

Convention:
    Signal directions are relative to the DUT:
      * Tx - transmitted by ECU => received from HIL
      * Rx - received by ECU <= transmitted from HIL
    
"""
from ttk_bus import _bus_signals_canida# @UnresolvedImport (compiled extension)

# #############################################################################
# hil-tx/ecu-rx messages - sample var names ---
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.cycle_counter
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.length                      DLC in Bytes
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.payload                     raw payload bytes
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.period                      currently active cycle time [ms]
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.timestamp                   tx time stamp 
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.trigger                     trigger/kickout flag
# others/optional: (may be used in selftest)
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.cycle_time                  only used in self-test to store "active" cycle time
#   CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.min_delay                   may be present, but currently not mapped to plugin

# Note: 
#    * there is no "enable" switch on a per-message level, set period to 0 instead
#    * selftest blocks use .cycle_time to store "enabled" cycle time to set to 
#      .period (and 0 to disable sending)

# hil-tx/ecu-rx signals - sample var names ---
# CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_EI_1.value        raw value sent to CAN plugin
# others/optional: (may be used in selftest)
# CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_EI_1.value_phy    physical value to write as raw to .value
# CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_EI_1.value_raw    raw value (usually same as .value)

# #############################################################################
# hil-rx/ecu-tx messages - sample var names ---
# CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.length                    dlc of message in Bytes
# CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.payload                   raw payload bytes [internal use]
# CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.timestamp                 rx time stamp 

# hil-rx/ecu-tx signals - sample var names ---
# CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.signals.State_Path_3_break.value       raw signal value from CAN plugin

# others/optional: (may be used in selftest)
# (but not really for 1-bit status values, only useful for values with non-default factor/offset
# CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.signals.State_Path_3_break.value_phy   physical representation of .value
# CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.signals.State_Path_3_break.value_raw   raw value == .value 

# #############################################################################
# CAN Message/PDU ~~~~~~~~~~~~~~~~~~---
# #############################################################################

# #############################################################################
class TxCanBusMessage(_bus_signals_canida.TxCanBusMessage):
    """ CAN Message/PDU ECU-Tx (ECU-Tx => HIL-Rx). """
    # #########################################################################
    def __init__(self, context, base_identifier=None, 
                 cycle_time=0, debounce_time=0,
                 alias="", descr='',
                 change_delay=None, timeout=None, recovery_time=None):
        """ Tx CAN Message data (ECU-Tx => HIL-Rx).
            
            Parameters:
                context          - parent iDA context 
                
                base_identifier  - base identifier to PDU/message.  
                                   Helper entries will be derived from this, 
                                   e.g. kickout or status variables (though this is mostly 
                                   relevant to messages sent to DUT, see RxCanBusMessage)  
                                   e.g. ecu-rx (hil-tx): "CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19"
                
                cycle_time        - cycle time in [ms]. Event-triggered messages 
                                    have a cycle time of 0 (similar to DBC value)
                debounce_time     - minimum debounce delay between events in [ms]
                
                alias             - Message alias/name
                descr             - (opt) Message description (may be used in report entries)
                
                change_delay      - (opt) delay to wait after a value change [ms], 
                                          defaults to 2x max(cycle_time, debounce_time)
                timeout           - (opt) detection time for timeout errors [ms], 
                                          defaults to 2x max(cycle_time, debounce_time)
                recovery_time     - (opt) time for recovery/"wiedergut" checks [ms]
                                          defaults to 2x max(cycle_time, debounce_time)
        """
        
        # Note: base class members added explicitly here (they will be updated 
        #       in base class' constructor) so automatic code completion may 
        #       find them even if the base class code cannot be analyzed.
        
        ## Message Rx time variable (in seconds)
        self.time_var = None
        
        ## Message payload data length
        self.length_var = None
        
        # Members inherited from CanBusMessage ################################
        # (see Note above)
        
        ## Parent context (a gaapi reference to resolve signal/variable paths)
        self.context = None
        ## Message alias name
        self.alias = None
        ## Message description text
        self.descr = None
        
        ## Base Bus path to Message/PDU helper variables 
        #  e.g. "CAN.<CAN_NAME>.HIL_RX.<MSG_NAME>"
        self.base_identifier = None
        
        # timings #############################################################
        ## cycle time of Message/PDU in [ms]
        self.cycle_time = None
        ## minimum debounce delay for event-triggered Messages/PDUs in [ms]
        self.debounce_time = None
        ## delay to wait after a value change [ms] 
        self.change_delay = None
        ## detection time for timeout errors [ms]
        self.timeout = None
        ## time for recovery/"wiedergut" checks [ms]
        self.recovery_time = None
        
        _bus_signals_canida.TxCanBusMessage.__init__(
            self, context=context, 
            base_identifier=base_identifier,
            
            cycle_time=cycle_time, debounce_time=debounce_time, 
            
            alias=alias, descr=descr, 
            
            change_delay=change_delay, timeout=timeout,
            recovery_time=recovery_time
        )
    
    # #########################################################################
    # Inherited from ResettableContainer
    # #########################################################################
    def reset(self, *args, **kwargs): # @UnusedVariable *args, **kwargs (just to tolerate optional parameters)
        """ Call reset() on all contained variables/signals that support it.
            Simple, non-recursive approach.
        """
        _bus_signals_canida.TxCanBusMessage.reset(self)
        

# #############################################################################
class RxCanBusMessage(_bus_signals_canida.RxCanBusMessage):
    """ CAN Message/PDU ECU-Rx (HIL-Tx => ECU-Rx).
        
        Extends the basic CanBusMessage with methods for 
        enableHilTx/disableHilTx and message kickout (trigger).
    """
    
    ## Configuration setting for new instances: 
    # Custom "hard" default values to use for internal real time system 
    # variables, so a reset() will always reset those variables to defined 
    # values (and not just those variables that were set/accessed). 
    # This might be helpful if "other" tests fail to properly clean up the
    # test environment after they are done.
    # 
    # Mapping: <variable name as string>: <default value>
    #
    # A value of None (or a missing variable name) enables normal/automatic 
    # reset behavior.
    #
    # Typical default values:
    # - Enable variables are usually default to "enabled"
    #    * 0: disabled
    #    * 1: enabled
    # - Message/PDU (Hil-TX) cycle time access: Default value depends on 
    #   configured cycle time (in [s]). Override standard behavior only if 
    #   absolutely necessary.
    # - Kickout/trigger variables: Triggers should auto-reset to 0 once the 
    #   PDU has been triggered. 0 is a safe default.
    cfg_custom_defaults = {
        "manual_enable_var":    None,
        "kickout_var":          None,
    }
    
    ## True: automatically initialize message's cycle time from the configured
    # cycle_time value (sets self.cycle_time_var to self.cycle_time during init)
    cfg_init_cycle_time = True
    
    
    # #########################################################################
    def __init__(self, context, base_identifier=None, 
                 cycle_time=0, debounce_time=0,
                 alias="", descr='',
                 change_delay=None, timeout=None, recovery_time=None):
        """ Rx CAN Message/PDU data (HIL-Tx => ECU-Rx).
            
            Parameters:
                context           - parent iDA context 
                
                base_identifier   - base identifier to PDU/message.  
                                    Helper entries will be derived from this, like kickout or status variables.
                                    e.g. ecu-rx (hil-tx) "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1"
                
                cycle_time        - cycle time in [ms]. Value will be used to 
                                    enable/disable sending of cyclic messages, 
                                    see cycle_time_var.  
                                    Event-triggered messages have a cycle time 
                                    of 0 (similar to DBC value)
                
                debounce_time     - minimum debounce delay between events in [ms]
                alias             - Message alias/name
                descr             - (opt) Message description (may be used in report entries)
                
                change_delay      - (opt) delay to wait after a value change [ms], 
                                          defaults to 2x max(cycle_time, debounce_time)
                timeout           - (opt) detection time for timeout errors [ms], 
                                          defaults to 2x max(cycle_time, debounce_time)
                recovery_time     - (opt) time for recovery/"wiedergut" checks [ms]
                                          defaults to 2x max(cycle_time, debounce_time)
        """
        # Note: base class members added explicitly here (they will be updated 
        #       in base class' constructor) so automatic code completion may 
        #       find them even if the base class code cannot be analyzed.
        
        ## HIL-Tx-enable/disable variable (only if set via enable_identifier)
        self.enable_var = None
        
        ## HIL-Tx-kickout/trigger variable
        self.kickout_var = None
        
        ## Message/PDU (Hil-Tx) cycle time access. Cycle time in [ms].
        # Note: This maps to the .period element of the current message
        self.cycle_time_var = None
        
        ## minimum delay between triggered messages in [ms], 
        # compare debounce delay in .debounce_time
        self.min_delay_var = None
        
        # Members inherited from CanBusMessage ################################
        # (see Note above)
        
        ## Parent context (a gaapi reference to resolve signal/variable paths)
        self.context = None
        ## Message alias name
        self.alias = None
        ## Message description text
        self.descr = None
        
        ## Base BusSystems path to Message/PDU helper variables below BusSystems
        #  e.g. "BusSystems.<CAN_NAME>.HIL_TX.<MSG_NAME>"
        self.base_identifier = None
        
        # timings #############################################################
        ## cycle time of Message/PDU in [ms]
        self.cycle_time = None
        ## minimum debounce delay for event-triggered Messages/PDUs in [ms]
        self.debounce_time = None
        ## delay to wait after a value change [ms] 
        self.change_delay = None
        ## detection time for timeout errors [ms]
        self.timeout = None
        ## time for recovery/"wiedergut" checks [ms]
        self.recovery_time = None
        
        # #####################################################################
        _bus_signals_canida.RxCanBusMessage.__init__(
            self, context, 
            
            base_identifier=base_identifier,        # base PV address/ident
            
            cycle_time=cycle_time, debounce_time=debounce_time, 
            alias=alias, descr=descr, 
            
            change_delay=change_delay, timeout=timeout,
            recovery_time=recovery_time
        )
    
    # #########################################################################
    def enableHilTx(self):
        """ (Re-)enable sending of this Message/PDU. """
        _bus_signals_canida.RxCanBusMessage.enableHilTx(self)

    # #########################################################################
    def disableHilTx(self):
        """ Disable (cyclic) sending of this Message/PDU. """
        _bus_signals_canida.RxCanBusMessage.disableHilTx(self)
    
    # #########################################################################
    def kickout(self, delay_ms=None):
        """ Trigger sending of this CAN-Message/PDU. 
            
            Parameters: 
                delay_ms - [ms] Delay to wait before clearing kickout/trigger 
                           variable again.
            
            Info: Default Delay:
               Delay defaults to 1/2 self.debounce_time (if explicitly set) 
               or alternatively to 1/2 self.change_delay.  
               Default delay will never be shorter than 5 ms.
        """
        _bus_signals_canida.RxCanBusMessage.kickout(self, delay_ms=delay_ms)
    
    # #########################################################################
    # Inherited from ResettableContainer
    # #########################################################################
    def reset(self, *args, **kwargs): 
        """ Call reset() on all contained variables/signals that support it.
            Simple, non-recursive approach.
        """
        _bus_signals_canida.RxCanBusMessage.reset(self, *args, **kwargs)
        

# #############################################################################
class TxCanBusSignal(_bus_signals_canida.TxCanBusSignal):
    """ A basic CAN signal sent from the DUT to the test system (ECU Tx => HIL Rx). 
        
        Basic implementation, directly accesses raw .value as-is from CAN-Plugin, 
        without a converted physical value or error injections.
    """
    # #########################################################################
    def __init__(self, context, signal_identifier, 
                 message=None, cycle_time=None, debounce_time=None,
                 unit="", alias="", descr="", lookup=None,
                 change_delay=None, timeout=None, recovery_time=None,
                 ):
        """ Basic Tx bus signal initialization (ECU Tx => HIL Rx).
            
            Note: `signal_identifier` var name
                Use `.value` entry (or optionally `.value_phy`/`.value_raw`,
                if available), e.g. 
                `"CAN.CanName.HIL_RX.MessageName.signals.SignalName.value"`  
                or just the base signal identifier to default to use `.value`:   
                `"CAN.CanName.HIL_RX.MessageName.signals.SignalName"`  
                
            Parameters:
                context            -  parent iDA context 
                signal_identifier  -  identifier for signal value var (see note) 
                message            -  reference to associated TxCanBusMessage instance
                
                cycle_time    - (opt) cycle time in [ms], overrides settings in message
                debounce_time - (opt) minimum debounce delay between events in [ms],
                                      overrides settings in Message
                unit          - (opt) unit of physical signal value (as string,
                                      mainly used for report entries)
                alias         - (opt) bus signal alias/name, defaults to the 
                                      last (non-default) entry in identifier
                                      (i.e. signal model path)
                
                descr         - (opt) signal description (e.g. used in report entries)
                lookup        - (opt) a lookup-table for mapping discrete signal 
                                      states to textual descriptions
                
                change_delay  - (opt) delay to wait after a value change [ms], 
                                      defaults to 2x max(cycle_time, debounce_time)
                timeout       - (opt) detection time for timeout errors [ms], 
                                      defaults to 2x max(cycle_time, debounce_time)
                recovery_time - (opt) time for recovery/"wiedergut" checks [ms]
                                      defaults to 2x max(cycle_time, debounce_time)
            
            Info: Minimal/Basic Signals:
                ECU-Tx/HIL-Rx Signals will only contain variables for:
                * `<SignalName>.value`     - raw value as received from CAN-Plugin
                * `<SignalName>.timestamp` - Rx time stamp
                * `<SignalName>.length`    - message length
        
        """
     
        # Note: base class members added explicitly here (they will be updated 
        #       in base class' constructor) so automatic code completion may 
        #       find them even if the base class' code cannot be analyzed.
        
        
        # Members inherited from CanBusSignal #################################
        # (see Note above)
        
        ## Signal PV address/identifier as base identifier for deriving sub-elements.
        # For CAN/Gamma signals, related variables follow the form 
        # `<base_identifier>.<suffix>`
        self.base_identifier = None
        ## reference to associated (Tx-)CanBusMessage instance
        self.message = None
        
        # Members inherited from BusSignal ####################################
        # (see Note above) 
        
        ## parent context (a gaapi reference to resolve signal/variable paths)
        self.context = None
        
        ## Signal value variable, default representation. get/info methods of 
        # this TxCanBusSignal will access this variable.  
        # Note that the default self.signal_var usually maps to member "value" or "value_phy", 
        # (depending on supplied signal_identifier).
        self.signal_var = None
        
        ## unit of physical signal value (as string, mainly used for report entries)
        self.unit = None
        ## bus signal alias name
        self.alias = None
        ## bus signal description text
        self.descr = None
        
        
        # timings #############################################################
        ## cycle time of Message/PDU in [ms]
        self.cycle_time = None
        ## minimum debounce delay for event-triggered Messages/PDUs in [ms]
        self.debounce_time = None
        ## delay to wait after a value change [ms] 
        self.change_delay = None
        ## detection time for timeout errors [ms]
        self.timeout = None
        ## time for recovery/"wiedergut" checks [ms]
        self.recovery_time = None
        
        
        # CanBusSignal will default to ".value" member and accept .value/.value_phy/.value_raw


        _bus_signals_canida.TxCanBusSignal.__init__(
            self, context, 
            
            signal_identifier, message=message, 
            cycle_time=cycle_time, debounce_time=debounce_time,

            unit=unit, alias=alias, descr=descr, lookup=lookup,
            change_delay=change_delay, timeout=timeout, recovery_time=recovery_time,
        )
    
    # #########################################################################
    def info(self):
        """ Get a current info string about the HIL signal variable, 
            see `signal_var`
            Returns the current info string from `signal_var`.
        """
        return _bus_signals_canida.TxCanBusSignal.info(self)
    
    # #########################################################################
    def get(self):
        """ Get the current value of the HIL signal variable, see `signal_var` 
            Returns the current value from `signal_var`.
        """
        return _bus_signals_canida.TxCanBusSignal.get(self)
    
    # #########################################################################
    def set(self, value):
        """ Set a value to the HIL signal variable, see `signal_var`
            
            Attention:
                For TxCanBusSignals, this will only overwrite the current 
                contents of the HIl receive buffer of the signal (which is 
                typically not too useful as it will be overwritten on next 
                update with data from CAN plugin)
            
            Parameters:
                value - value to set
            
            Returns the previous value from `signal_var`.
        """
        return _bus_signals_canida.TxCanBusSignal.set(self, value)
    
    # #########################################################################
    def getState(self):
        """ Get a textual state for the HIL signal variable's current data, 
            see `signal_var`. This uses the lookup values supplied in constructor.
            Fallback (if no matching state was found) will be the unmapped 
            numeric value.
            
            Returns the current state representation from `signal_var`.
        """
        return _bus_signals_canida.TxCanBusSignal.getState(self)
    
    # #########################################################################
    def setState(self, state):
        """ Set a textual state to the HIL signal variable, see `signal_var`.
            This uses the lookup values supplied in constructor.
            
            Attention:
                For TxFrBusSignals this will only overwrite the current 
                contents of the HIl receive buffer of the signal 
                (which typically is not too useful).
            
            Parameters:
                state - named state to set
            
            Returns the previous state representation from `signal_var`.
        """
        return _bus_signals_canida.TxCanBusSignal.setState(self, state)
    
    # #########################################################################
    def getStateDescr(self, value=None, fallback=None):
        """ Get a state description text for the given value from the HIL 
            signal variable's defined lookup table (if any).
            
            Parameters:
                value     - value for which to get a state description. 
                            If None, the last read value will be used instead.
                fallback  - fallback value to return if no match was found.
                            Default: None
            
            Returns the state text if a match was found, otherwise the specified
            fallback value.
        """
        return _bus_signals_canida.TxCanBusSignal.getStateDescr(
            self, value=value, fallback=fallback
        )
    
    # #########################################################################
    # Inherited from ResettableContainer
    # #########################################################################
    def reset(self, *args, **kwargs):
        """ Reset all resettable variables of this bus signal. """
        _bus_signals_canida.TxCanBusSignal.reset(self, *args, **kwargs)
        

# #############################################################################
class RxCanBusSignal(_bus_signals_canida.RxCanBusSignal):
    """ A basic CAN signal sent from the test system to the DUT (ECU Rx <= HIL Tx). 
        
        Basic implementation, directly accesses raw value as-is from CAN, 
        without a converted physical value or error injections.
    """
    # #########################################################################
    def __init__(self, context, signal_identifier, 
                 message=None, cycle_time=None, debounce_time=None,
                 unit="", alias="", descr="", lookup=None,
                 change_delay=None, timeout=None, recovery_time=None,
                 ):
        """ Basic Rx bus signal initialization (ECU Rx <= HIL Tx).
            
            Note: `signal_identifier` var name
                Use `.value` entry (or optionally `.value_phy`/`.value_raw`,
                if available), e.g.  
                `"CAN.CanName.HIL_TX.MessageName.signals.SignalName.value"`  
                or the base signal identifier to default to use `.value`:  
                `"CAN.CanName.HIL_TX.MessageName.signals.SignalName"`  
                                      
            Parameters:
                context            -  parent iDA context 
                signal_identifier  -  identifier for signal value var (see note for samples)
                message            -  reference to associated CanBusMessage instance

                cycle_time    - (opt) cycle time in [ms], overrides settings in Message
                debounce_time - (opt) minimum debounce delay between events in [ms],
                                      overrides settings in Message
                unit          - (opt) unit of physical signal value (as string,
                                      mainly used for report entries)
                alias         - (opt) bus signal alias/name, defaults to the 
                                      last (non-default) entry in identifier
                                      (i.e. signal model path)
                
                descr         - (opt) signal description (e.g. used in report entries)
                lookup        - (opt) a lookup-table for mapping discrete signal 
                                      states to textual descriptions
                
                change_delay  - (opt) delay to wait after a value change [ms], 
                                      defaults to 2x max(cycle_time, debounce_time)
                timeout       - (opt) detection time for timeout errors [ms], 
                                      defaults to 2x max(cycle_time, debounce_time)
                recovery_time - (opt) time for recovery/"wiedergut" checks [ms]
                                      defaults to 2x max(cycle_time, debounce_time)
            
            Info: Minimal/Basic Signals:
                ECU-Rx/HIL-Tx Signals generated by iSyDBC in minimal/basic mode 
                will only contain PVs for:
                * `<SignalName>.value`     - raw value as sent to CAN-Plugin
                * `<SignalName>.period`    - tx cycle time / period in ms.
                * `<SignalName>.timestamp` - Tx time stamp
                * `<SignalName>.length`    - message length
            
        """
        # Note: base class members added explicitly here (they will be updated 
        #       in base class' constructor) so automatic code completion may 
        #       find them even if the base class' code cannot be analyzed.
        
        
        # Members inherited from CanBusSignal #################################
        # (see Note above) 
        
        ## Signal PV address/identifier as base identifier for deriving sub-elements.
        # For CAN/Gamma signals, related variables follow the form 
        # `<base_identifier>.<suffix>`
        self.base_identifier = None
        
        ## reference to associated (Rx-)CanBusMessage instance
        self.message = None
        
        # Members inherited from BusSignal ####################################
        # (see Note above) 
        
        ## parent context (a gaapi reference to resolve signal/variable PVs)
        self.context = None
        
        ## signal value variable. get/info methods of this RxCanBusSignal
        # will access this variable.
        self.signal_var = None
        
        ## unit of physical signal value (as string, mainly used for report entries)
        self.unit = None
        ## bus signal alias/name
        self.alias = None
        ## bus signal description text
        self.descr = None
        
        # timings #############################################################
        ## cycle time of Message/PDU in [ms]
        self.cycle_time = None
        ## minimum debounce delay for event-triggered Messages/PDUs in [ms]
        self.debounce_time = None
        ## delay to wait after a value change [ms] 
        self.change_delay = None
        ## detection time for timeout errors [ms]
        self.timeout = None
        ## time for recovery/"wiedergut" checks [ms]
        self.recovery_time = None
        
        # #####################################################################
        # CanBusSignal will default to ".value" member and accept .value/.value_phy/.value_raw
        _bus_signals_canida.RxCanBusSignal.__init__(
            self, context=context, 
            signal_identifier=signal_identifier, message=message, 
            
            cycle_time=cycle_time, debounce_time=debounce_time,
            unit=unit, alias=alias, descr=descr, lookup=lookup,
            change_delay=change_delay, timeout=timeout, recovery_time=recovery_time,
        )
    
    # #########################################################################
    def info(self):
        """ Get a current info string about the HIL signal variable, 
            see `signal_var`.
            Attention:
                For RxCanBusSignals, this will show info on the contents 
                of the HIL-send-buffer, not the value from Model/Simulink 
                source nor the last seen signal value on CAN bus.
            
            Returns the current info string from `signal_var`.
        """
        return _bus_signals_canida.RxCanBusSignal.info(self)
    
    # #########################################################################
    def get(self):
        """ Get the current value of the HIL signal variable, see `signal_var`. 
            
            Attention:
                For RxCanBusSignals, this will get the current (raw) value 
                of the HIL-send-buffer, not the last seen signal value on CAN 
                bus.
            
            Returns the current value from `signal_var`.
        """
        return _bus_signals_canida.RxCanBusSignal.get(self)
    
    # #########################################################################
    def set(self, value):
        """ Set a value to the HIL signal variable (`.signal_var`).
            
            Parameters:
                value - value to set (physical)
            
            Returns the previous value from `signal_var`.
        """
        return _bus_signals_canida.RxCanBusSignal.set(self, value=value)
    
    # #########################################################################
    def getState(self):
        """ Get a textual state for the HIL signal variable's current data, 
            see `value_var`. This uses the lookup values supplied in constructor.
            Fallback (if no matching state was found) will be the unmapped 
            numeric value.
            
            Attention:
                For RxCanBusSignals, this will get the current (raw) value 
                of the HIL-send-buffer, not the last seen signal value on 
                CAN bus.
            
            Returns the current state representation from `signal_var`.
        """
        return _bus_signals_canida.RxCanBusSignal.getState(self)
    
    # #########################################################################
    def setState(self, state):
        """ Set a textual state to the HIL signal variable (`.value_var`). 
            This uses the lookup values supplied in constructor.
            
            Parameters:
                state - named state to set
            
            Returns the previous value from `signal_var`.
        """
        return _bus_signals_canida.RxCanBusSignal.setState(self, state=state)
    
    # #########################################################################
    def getStateDescr(self, value=None, fallback=None):
        """ Get a state description text for the given value from the HIL 
            signal variable's defined lookup table (if any).
            
            Parameters:
                value     - value for which to get a state description. 
                            If None, the last read value will be used instead.
                fallback  - fallback value to return if no match was found.
                            Default: None
            
            Returns the state text if a match was found, otherwise the specified
            fallback value.
        """
        return _bus_signals_canida.RxCanBusSignal.getStateDescr(
            self, value=value, fallback=fallback
        )
    
    # #########################################################################
    # Inherited from ResettableContainer
    # #########################################################################
    def reset(self, *args, **kwargs):
        """ Reset all resettable variables of this bus signal. Note that this
            will also switch the variable source switch back to its original 
            setting.
        """
        _bus_signals_canida.RxCanBusSignal.reset(self, *args, **kwargs)
        
    # #########################################################################
    def enableHilTx(self):
        """ Enable transmission of signal HIL => DUT (if the assigned 
            CAN-Message/PDU supports it).
            
            Note:
                This will enable transmission of _all_ signals of the parent 
                Message/PDU.
        """
        return _bus_signals_canida.RxCanBusSignal.enableHilTx(self)
    
    # #########################################################################
    def disableHilTx(self):
        """ Disable transmission of signal HIL => DUT (if the assigned 
            CAN-Message/PDU supports it). 
            
            Note:
                This will disable transmission of _all_ signals of the parent 
                Message/PDU.
        """
        return _bus_signals_canida.RxCanBusSignal.disableHilTx(self)
    
    # #########################################################################
    def kickout(self):
        """ Trigger transmission ("kickout") of signal HIL => DUT (by 
            triggering the parent CAN-Message/PDU). 
            
            Note:
                All other signals of the parent Message/PDU will also be sent.
        """
        return _bus_signals_canida.RxCanBusSignal.kickout(self)
    

# #############################################################################
# Signal Container ~~~~~~~~~~~~~~~~~~~~---
# #############################################################################
class CanBusSignalContainer(_bus_signals_canida.CanBusSignalContainer):
    """ A BusSignalContainer for CAN Bus Signals """
    # #########################################################################
    def __init__(self, context):
        """ Override to add signals.
            
            Parameters:
                context - context used for contained BusSignals
        """
        _bus_signals_canida.CanBusSignalContainer.__init__(self, context)
    
    # #########################################################################
    def resetAll(self, verbosity=1, recursion_depth=4):
        """ Call reset() on all contained BusSignals that support it. 
            Parameters:
                verbosity       - verbosity of log output:  
                                   0: silent except for errors  
                                   1: only minimal status info (begin/end)  
                                   2: also show processed variable names  
                recursion_depth - how "deep" to recurse into lists/dictionary
                                  structures when looking for variables to 
                                  reset.
        """
        _bus_signals_canida.CanBusSignalContainer.resetAll(
            self, 
            verbosity=verbosity, 
            recursion_depth=recursion_depth
        )
    
    # #########################################################################
    def iterSignals(self, msg):
        """ Iterate over all signals that reference the specified CAN message/PDU.
            
            Parameters:
                msg - a CAN message/PDU instance
            
            Usage:
                for sig in bus.iterSignals(bus.tx_msg_FNORD):
                    print sig
            
            Returns an iterator object.
        """
        return _bus_signals_canida.CanBusSignalContainer.iterSignals(
            self, msg=msg
        )
        

# #############################################################################
# @cond DOXYGEN_IGNORE
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    import time
    import ttk_tools.isyst.ida_testware_offline_stub as ida_testware
    
    
    with ida_testware.IdaTestware(addr="127.0.0.1") as ida_tw:
            
        # #########################################################################
        class BusSignals(CanBusSignalContainer):
            def __init__(self, ctx):
                super().__init__(ctx)
                self.tx_msg = TxCanBusMessage(ctx, 
                    # only first 4 elements will be used as base var name
                    "CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.payload", 
                    cycle_time=100, debounce_time=10
                )
                self.rx_msg = RxCanBusMessage(ctx, 
                    "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1", 
                    cycle_time=100, debounce_time=10, alias="BAZ_Message"
                )
                self.rx_msg2 = RxCanBusMessage(ctx, 
                    base_identifier="CAN.can3_iFIU_iSRC.HIL_RX.FnordMsg.payload", 
                    cycle_time=50, debounce_time=10
                )
                
                #
                self.BarBazSig  = TxCanBusSignal(ctx, "CAN.can3_iFIU_iSRC.HIL_RX.N0FIU_Status_Card19.signals.State_Path_3_break.value", self.tx_msg)
                
                #
                self.FooBarSig  = RxCanBusSignal(ctx, "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_EI_1.value", self.rx_msg)
                self.BazQuuxSig = RxCanBusSignal(ctx, "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_EI_2.value", self.rx_msg)
                self.AnotherSig = RxCanBusSignal(ctx, "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_break.value", 
                    alias="Another Bus Signal", descr="Another Signal to test", unit="rpm", 
                    message=self.rx_msg, 
                    change_delay=250, timeout=500, recovery_time=500,
                )
                
                self.BasicSig   = RxCanBusSignal(ctx, "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_EI_1.value", self.rx_msg)
                self.BazQuuxSig = RxCanBusSignal(ctx, "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_EI_2.value", self.rx_msg)
                self.AnotherSig = RxCanBusSignal(ctx, "CAN.can3_iFIU_iSRC.HIL_TX.N0FIU_SetError_Card1.signals.Path_1_break.value", 
                    alias="Another Bus Signal", descr="Another Signal to test", unit="rpm", 
                    message=self.rx_msg, 
                    change_delay=250, timeout=500, recovery_time=500,
                )
                
        
    bus_signals = BusSignals(ida_tw)
    
    print("# initial:")
    print(bus_signals.FooBarSig.info())
    print(bus_signals.BazQuuxSig.info())
    print(bus_signals.AnotherSig.info())
    bus_signals.FooBarSig.set(1234)
    bus_signals.AnotherSig.set(1000)
    time.sleep(bus_signals.AnotherSig.cycle_time / 1000.0)
    
    
    
    print("# changed:")
    print(bus_signals.FooBarSig.info())
    print(bus_signals.BazQuuxSig.info())
    print(bus_signals.AnotherSig.info())
    
    print()
    bus_signals.resetAll()
    print("# reset:")
    print(bus_signals.FooBarSig.info())
    print(bus_signals.BazQuuxSig.info())
    print(bus_signals.AnotherSig.info())
    
    
    print() 
    print("# iterSignals:")
    print(f'Signals in rx_msg ("{bus_signals.rx_msg.alias}"):')
    for sig in bus_signals.iterSignals(bus_signals.rx_msg):
        print(" -> %-100s (%s)"%(sig, type(sig).__name__))
    
    print(f'Signals in tx_msg ("{bus_signals.tx_msg.alias}"):')
    for sig in bus_signals.iterSignals(bus_signals.tx_msg):
        print(" -> %-100s (%s)"%(sig, type(sig).__name__))
    
    print("#" * 80)
    
    def varinfo(obj, name):
        var = getattr(obj, name, None)
        print(f"  {name!s:<16} ► {type(var)!s} {var}")
        
    

    print("-------------------------------------------------------------------")
    print(bus_signals.FooBarSig.message.alias)
    varinfo(bus_signals.FooBarSig.message, "cycle_time_var")
    varinfo(bus_signals.FooBarSig.message, "kickout_var")
    print(bus_signals.FooBarSig.alias)
    
    print("-------------------------------------------------------------------")
    print("#", bus_signals.rx_msg.alias)
    varinfo(bus_signals.rx_msg, "cycle_time_var")
    varinfo(bus_signals.rx_msg, "kickout_var")
    print("#", bus_signals.rx_msg2.alias)
    varinfo(bus_signals.rx_msg2, "cycle_time_var")
    varinfo(bus_signals.rx_msg2, "kickout_var")
    
    
    print("\nDone.")
# @endcond DOXYGEN_IGNORE
# #############################################################################

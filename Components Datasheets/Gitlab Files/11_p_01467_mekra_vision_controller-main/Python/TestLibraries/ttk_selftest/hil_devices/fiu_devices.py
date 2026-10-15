#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : fiu_devices.py
# Package : ttk_selftest.hil_devices
# Task    : Wrapper classes for fiu device descriptions
# Python  : 3.8+
# Type    : Base implementation
#
# Copyright 2018 - 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 10.09.2018 | C.Haas     | initial (derived from 
#                                  | selftest_hil_devices_base)
# 1.1.0  | 06.10.2022 | C.Haas     | Added parameter for waiting time,
#                                  | fixed review findings
# 2.0.0  | 09.01.2024 | M. Jellen  | Python3 update
# 2.0.1  | 31.01.2024 | J.Tremmel  | updated docstrings, super() for parent calls
#******************************************************************************
"""
@package ttk_selftest.hil_devices.fiu_devices
Interface wrapper for fiu device descriptions.
"""
from ttk_selftest.hil_devices import _fiu_devices # @UnresolvedImport (compiled extension) 


# #############################################################################
# FIU channel - Base class for FIU channels
# #############################################################################
class FiuChannel(_fiu_devices.FiuChannel):
    """ Base FIU channel container """
    # #########################################################################
    def __init__(self, context, base_path,
                 num_fiu_card, num_fiu_channel, wait_time_ms=5, alias=""):
        """ FIU Channel initialization.
            
            Parameters:
                context                 - parent context
                base_path               - base path of the iFIUCard in the model
                                          (all required variables will be derived 
                                          from this path)
                num_fiu_card            - ID of the iFIUCard
                num_fiu_channel         - channel number of the specified iFIUCard
                wait_time_ms            - (opt) waiting time in milliseconds after
                                          state of the FIU channel has been set
                                          defaults to 5ms
                alias                   - (opt) alias of the FIU channel
                                          defaults to number and channel of the FIU 
        """
        super().__init__(
            context=context, 
            base_path=base_path, 
            num_fiu_card=num_fiu_card, 
            num_fiu_channel=num_fiu_channel, 
            wait_time_ms=wait_time_ms, 
            alias=alias
        )
    
    # #########################################################################
    def setOpenLoad(self):
        """ Set Open load state on the FIU channel """
        return super().setOpenLoad()
    
    # #########################################################################
    def resetOpenLoad(self):
        """ Reset Open load state on the FIU channel """
        return super().resetOpenLoad()
    
    # #########################################################################
    def setEI1(self):
        """ Set connection to EI1 on the FIU channel """
        return super().setEI1()
    
    # #########################################################################
    def resetEI1(self):
        """ Reset connection to EI1 on the FIU channel """
        return super().resetEI1()
    
    # #########################################################################
    def setEI2(self):
        """ Set connection to EI2 on the FIU channel """
        return super().setEI2()
    
    # #########################################################################
    def resetEI2(self):
        """ Reset connection to EI2 on the FIU channel """
        return super().resetEI2()
    
    # #########################################################################
    def resetChannel(self):
        """ Reset FIU channel to default. No Error will be active. """
        return super().resetChannel()
    
    # #########################################################################
    def resetSignals(self):
        """ Reset the signals of the FIU channel to default without triggering
            the CAN message. 
        """
        return super().resetSignals()
        

# #############################################################################
# FIU CAN FR channel - Base class for FIU CAN FR channels
# #############################################################################
class FiuCanFrChannel(_fiu_devices.FiuCanFrChannel):
    """ Base FIU CAN FR channel container """
    # #########################################################################
    def __init__(self, context, base_path,
                 num_fiu_can_fr_card, num_fiu_can_fr_channel, 
                 wait_time_ms=5, alias=""):
        """ FIU CAN FR Channel initialization.
            
            Parameters:
                context                 - parent context
                base_path               - base path of the iFIU_CAN_FR in the model
                                          (all required variables will be derived 
                                          from this path)
                num_fiu_can_fr_card     - ID of the iFIU_CAN_FR
                num_fiu_can_fr_channel  - channel number of the specified iFIU_CAN_FR
                wait_time_ms            - (opt) waiting time in milliseconds after
                                          state of the FIU channel has been set
                                          defaults to 5ms
                alias                   - (opt) alias of the FIU_CAN_FR channel
                                          defaults to number and channel of the iFIU_CAN_FR 
        """
        super().__init__(
            context=context, 
            base_path=base_path, 
            num_fiu_can_fr_card=num_fiu_can_fr_card, 
            num_fiu_can_fr_channel=num_fiu_can_fr_channel, 
            wait_time_ms=wait_time_ms, 
            alias=alias
        )
    
    # #########################################################################
    def setHighOpenLoad(self):
        """ Set Open load on the high bus signal """
        return super().setHighOpenLoad()
    
    # #########################################################################
    def setLowOpenLoad(self):
        """ Set Open load on the low bus signal """
        return super().setLowOpenLoad()
    
    # #########################################################################
    def setHighEI1(self):
        """ Connect EI1 to the high bus signal """
        return super().setHighEI1()
    
    # #########################################################################
    def setLowEI1(self):
        """ Connect EI1 to the low bus signal """
        return super().setLowEI1()
    
    # #########################################################################
    def setHighEI2(self):
        """ Connect EI2 to the high bus signal """
        return super().setHighEI2()
    
    # #########################################################################
    def setLowEI2(self):
        """ Connect EI1 to the low bus signal """
        return super().setLowEI2()
    
    # #########################################################################
    def resetChannel(self):
        """ Reset FIU_CAN_FR channel to default. No Error will be active. """
        return super().resetChannel()
    
    # #########################################################################
    def resetSignals(self):
        """ Reset the signals of the FIU_CAN_FR channel to default without 
            triggering the CAN message.
        """
        return super().resetSignals()

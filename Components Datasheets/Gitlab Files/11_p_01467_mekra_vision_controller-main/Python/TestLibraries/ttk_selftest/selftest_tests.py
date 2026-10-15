#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : ttk_selftest.selftest_tests.py
# Task    : Wrapper for test functions for self tests
# Copyright 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 03.12.2018 | C.Haas     | initial
# 2.0.0  | 09.01.2024 | M. Jellen  | Python3 update
#******************************************************************************
"""
@package ttk_selftest.selftest_tests
Wrapper for self test test functions
This serves as "interface" to the precompiled module in delivery to enable
code-completion in PyDev.
"""
from ttk_selftest import _selftest_tests # @UnresolvedImport (compiled extension)


# #############################################################################
# test functions
# #############################################################################
def testGND(testenv, gnd, threshold = 10000, ignore_results=False):
    """ Function to test ground connections
        
        The test is passed if the gnd has no connection to any other defined 
        ground.
        
        Parameters:
            testenv        - test environment
            gnd            - gnd device which shall be tested
            threshold      - (opt) minimum required resistance between two ground
                             devices in Ohm, defaults to 10k
                             Note: The measured resistance depends on the 
                             system configuration. Therefore the threshold has to
                             be chosen individually for each system!
            ignore_results - If set to True, the test will be performed ignoring
                             any already available results.
                             If set to False, the available results will be taken
                             into account. For example, the test of gnd1 to gnd2
                             will not be performed anymore if the test gnd2 to
                             gnd1 has already been performed before.
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testGND(testenv, gnd, threshold, ignore_results)
    

# #############################################################################
def testAnalogOutput(testenv, channel, ref_channel, num_testvalues=5, gnd_offset=0.5):
    """ Function to test an analog output channel
        
        Parameters:
            testenv        - test environment
            channel        - analog output that shall be tested
            ref_channel    - iSystemReferenceCard device to be used as reference
            num_testvalues - (opt) number of different values to be tested
                             equally split within common range of both analog
                             channels
                             defaults to 5 values
            gnd_offset     - (opt) voltage to be applied to channel ground
                             if it is not equal to the ground of the PSU that
                             is connected to the iSRC
                             valid range: 0-2V, defaults to 0.5V
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testAnalogOutput(testenv, channel, ref_channel, num_testvalues, gnd_offset)
    

# #############################################################################
def testAnalogVoltageInput(testenv, device, num_testvalues = 5):
    """ Function to test an analog voltage input channel
        
        Parameters:
            testenv        - test environment
            device         - analog input channel to be tested or load device
                             whose voltage measurement shall be tested
            num_testvalues - (opt) number of different values to be tested
                             equally split within common range of the channel
                             and the range of the iSRC (only relevant for load
                             devices)
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testAnalogVoltageInput(testenv, device, num_testvalues)
    

# #############################################################################
def testAnalogCurrentInput(testenv, device, num_testvalues = 5):
    """ Function to test an analog current input channel
        
        Parameters:
            testenv        - test environment
            device         - load device whose current measurement shall be tested
            num_testvalues - (opt) number of different values to be tested
                             equally split within common range of the channel
                             and the range of the iSRC
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testAnalogCurrentInput(testenv, device, num_testvalues)
    

# #############################################################################
def testPowerSupplyVoltage(testenv, power_supply, num_testvalues = 5):
    """ Function to test power supply voltage control and measurement
        
        Parameters:
            testenv        - test environment
            power_supply   - power supply that shall be tested
            num_testvalues - (opt) number of different values to be tested
                             equally split within common range of the power
                             supply and the iSRC
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testPowerSupplyVoltage(testenv, power_supply, num_testvalues)
    

# #############################################################################
def testPowerSupplyCurrent(testenv, power_supply, max_test_current = None, num_testvalues= 5):
    """ Function to test power supply current control and measurement
        
        Parameters:
            testenv          - test environment
            power_supply     - power supply that shall be tested
            max_test_current - (opt) current limit during current test
                               defaults to 18A
            num_testvalues   - (opt) number of different values to be tested
                                equally split within common range of the power
                                supply and the iSRC
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testPowerSupplyCurrent(testenv, power_supply, max_test_current, num_testvalues)
    

# #############################################################################
def testPowerSupply(testenv, power_supply, max_test_current = None, num_testvalues= 5):
    """ Function to test Power Supply voltage and current
        
        Parameters:
            testenv          - test environment
            power_supply     - power supply that shall be tested
            max_test_current - (opt) current limit during current test
                               defaults to 18A
            num_testvalues   - (opt) number of different values to be tested
                               equally split within common range of the power
                               supply and the iSRC
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testPowerSupply(testenv, power_supply, max_test_current, num_testvalues)
    

# #############################################################################
def testPwmInput(testenv, device, num_testvalues= 5):
    """ Function to test a PWM input channel
        
        Parameters:
            testenv          - test environment
            device           - PWM input channel to be tested or load device
                               whose PWM input channel(s) shall be tested
            num_testvalues   - (opt) number of different values to be tested
                               equally split within common range of both
                               frequency and duty cycle
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testPwmInput(testenv, device, num_testvalues)
    

# #############################################################################
def testLoad(testenv, load, num_testvalues= 5):
    """ Function to test a load
        
        Parameters:
            testenv          - test environment
            load             - load that shall be tested
            num_testvalues   - (opt) number of different values to be tested
                               equally split within common range of loads
                               specification and iSRC
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testLoad(testenv, load, num_testvalues)
    

# #############################################################################
def testPwmOutput(testenv, channel, num_testvalues= 5):
    """ Function to test an PWM output channel
        
        Parameters:
            testenv        - test environment
            channel        - PWM output that shall be tested
            num_testvalues - (opt) number of different values to be tested
                             equally split within common range of both 
                             frequency and duty cycle
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testPwmOutput(testenv, channel, num_testvalues)
    

# #############################################################################
def testCan(testenv, channel):
    """ Function to test a CAN channel
        
        Parameters:
            testenv        - test environment
            channel        - CAN channel that shall be tested
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testCan(testenv, channel)
    

# #############################################################################
def testDigitalInput(testenv, device):
    """ Function to test a digital input channel
        
        Parameters:
            testenv          - test environment
            device           - digital input channel to be tested or load device
                               whose digital input channel(s) shall be tested
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testDigitalInput(testenv, device)
    

# #############################################################################
def testDigitalOutput(testenv, channel):
    """ Function to test a digital output channel
        
        Parameters:
            testenv        - test environment
            channel        - digital output that shall be tested
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testDigitalOutput(testenv, channel)


# #############################################################################
def testiDigiRes(testenv, idigires):
    """ Function to test an iDigiRes
        
        Parameters:
            testenv        - test environment
            idigires       - iDigiRes that shall be tested
        
        Returns the testresult parameter extended by test result entries.
    """
    return _selftest_tests.testiDigiRes(testenv, idigires)


# #############################################################################
def resetFiu(hil_devices):
    """ Function to reset the FIU.
        This affects the iFIUCards and iFIU_CAN_FRs, whose channels will be
        set to the no error state.
        
        Parameters:
            hil_devices - devices of the HIL system
        
        Returns a single test result entry.
    """
    return _selftest_tests.resetFiu(hil_devices)

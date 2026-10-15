#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : adjustment_calculation.py
# Package : ttk_selftest
# Task    : Wrapper for Calibration methods for adjustment calculation of
#           self test.
#
# Copyright 2019 - 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.	 | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0  	 | 14.08.2019 | SeMeyer    | initial
# 1.1  	 | 28.08.2019 | SeMeyer    | update all header after sw review
# 1.2  	 | 23.03.2020 | SeMeyer    | Bug fix of AdjustmentCalculation.__init__()
#                                  | => change default Parameter-Specification
# 2.0.0  | 09.01.2024 | M. Jellen  | Python3 update
# 2.0.1  | 31.01.2024 | J.Tremmel  | updated docstrings, super() for parent calls
#******************************************************************************
""" 
@package ttk_selftest.adjustment_calculation

Interface wrapper for adjustment calculation class.
"""

from ttk_selftest import _adjustment_calculation  # @UnresolvedImport (compiled extension)


# #############################################################################
class AdjustmentCalculation(_adjustment_calculation.AdjustmentCalculation):
    """ Class for adjustment one hil channel which is currently in state self
        test and adjustment.
    """
    
    
    # #########################################################################
    def __init__(self, hilvar_gain, hilvar_offset, limit_gain=None,
                 limit_offset=None, precision=6):
        """ Initialize the instance and prepare the self adjustment environment.
            Parameters:
                hilvar_gain   -       variable definition with a get() and set()
                                      method to read current specified gain for
                                      channel is specified to run the adjustment
                                      calculation.
                hilvar_offset -       variable definition with a get() and set()
                                      method to read current specified offset for
                                      channel is specified to run the adjustment
                                      calculation.
                limit_gain    - (opt) dict with struct {"max":<value>, "min":<value>}
                                      Limitation of calculated new gain. In use
                                      to check the calculation and in case of
                                      incorrect set the calculation to false.
                                      - "max": maximum limitation (> min)
                                      - "min": minimum limitation (< max)
                                      - Type: Type of "Float", "Long" and "Int"
                                              acceptable
                limit_offset  - (opt) dict with struct {"max":<value>, "min":<value>}
                                      Limitation of calculated new offset. In use
                                      to check the calculation and in case of
                                      incorrect set the calculation to false.
                                      - "max": maximum limitation (> min)
                                      - "min": minimum limitation (< max)
                                      - Type: Type of "Float", "Long" and "Int"
                                              acceptable
                precision     - (opt) Specify the number of decimal places the
                                      new gain and offset value should round
                                      after the calculation.
                                      Type: "Integer"
            
            Raises Exception in case of sanity check fails
        """
        super().__init__(
            hilvar_gain=hilvar_gain, 
            hilvar_offset=hilvar_offset,
            limit_gain=limit_gain, 
            limit_offset=limit_offset, 
            precision=precision
        )
    
    # #########################################################################
    def calibData(self, expected, measured, verbosity=True):
        """ Calibration Method - The method describe the complete hil adjustment
            calculation:
                - Check parameter are correct
                - compensate possible old gain and offset values different to the
                  default in model
                - calculate the linear regression
                - calculate the new calibrated data (gain and offset)
                - check the new calibrated data against the limitation
            Parameters:
                expected -       list of expected data
                measured -       list of measured data
                verbosity- (opt) state to define the depth of logging
                                 False: No print out
                                 True:  Print the call of methods...
            Attention:
                expected and measured data should have the same value order.
                
        """
        super().calibData(expected, measured, verbosity)
        
    
    # #########################################################################
    def getCurrentGain(self):
        """ Get back the current gain which is specified in running simulation
            model at current test system. The value will be read out by use the
            specified variable.
            
            Returns current gain value read from used hil variable.
        """
        return super().getCurrentGain()
        
    
    # #########################################################################
    def getCurrentOffset(self):
        """ Get back the current offset which is specified in running simulation
            model at current test system. The value will be read out by use the
            specified variable.
            
            Returns current offset value read from used hil variable.
        """
        return super().getCurrentOffset()
        
    
    # #########################################################################
    def getNewGain(self):
        """ Get back the calculated gain (linear regression).
        
            Returns new/calculated gain value to use after calibration or 
            None in case calibration is not running correctly.
        """
        return super().getNewGain()
        
    
    # #########################################################################
    def getNewOffset(self):
        """ Get back the new offset (linear regression).
        
            Returns new/calculated offset to use after calibration or 
            None in case calibration is not running correctly.
        """
        return super().getNewOffset()
        
    
    # #########################################################################
    def getCalibVerdict(self):
        """ Get back the qualification string from the check the new parameter
            against the specified ranges.
            
            Returns a verdict string, "PASSED", "FAILED" or "NOT TESTED"  
                * PASSED:    Check of new parameters against defined ranges passed  
                * FAILED:    Check of new parameters against defined ranges failed  
                * NOTTESTED: Check is not running  
        """
        return super().getCalibVerdict()
        
    
    # #########################################################################
    def getCalibTimeStamp(self):
        """ Get back the time stamp of running calibration.
        
            Returns timestamp of calibration run or None if calibration is not 
            running correctly.
            Note:
                Value can be converted like:
                    time.strftime(
                        "%Y-%m-%dT%H:%M:%S",
                        time.localtime(getCalibTimeStamp())
                    )
        """
        return super().getCalibTimeStamp()
        
    
    # #########################################################################
    def getLimitGainMax(self):
        """ Get back the maximum specified limitation value of gain.
            Returns maximum limitation value of the gain.
        """
        return super().getLimitGainMax()
        
    
    # #########################################################################
    def getLimitGainMin(self):
        """ Get back the minimum specified limitation value of gain.
            Returns minimum limitation value of the gain.
        """
        return super().getLimitGainMin()
        
    
    # #########################################################################
    def getLimitOffsetMax(self):
        """ Get back the maximum specified limitation value of offset.
            Returns maximum limitation value of the offset.
        """
        return super().getLimitOffsetMax()
        
    
    # #########################################################################
    def getLimitOffsetMin(self):
        """ Get back the minimum specified limitation value of offset.
            Returns minimum limitation value of the offset.
        """
        return super().getLimitOffsetMin()
        
    
    # #########################################################################
    def getPrecision(self):
        """ Get back the specified number of decimal places, which is used to
            round the new gain and offset value before get back.
            Returns number of decimal places that should be used to round values.
        """
        return super().getPrecision()
        
    
    # #########################################################################
    def getStandardVariance(self):
        """ Return the standard variance of linear regression back. 
            Will be generated during calibration value calculation.
            
            Returns the calculated standard variance to use after calibration 
            or None in case calibration is not running correctly.
        """
        return super().getStandardVariance()
        
    
    # #########################################################################
    def getGainVariance(self):
        """ Return the gain variance of linear regression back. 
            Will be generated during calibration values calculated.
            
            Returns the calculated gain variance to use after calibration 
            or None in case calibration is not running correctly.
        """
        return super().getGainVariance()
        
    
    # #########################################################################
    def getOffsetVariance(self):
        """ Return the offset variance of linear regression back. 
            Will be generated during calibration value calculation.
            
            Returns the calculated offset variance to use after calibration 
            or None in case calibration is not running correctly.
        """
        return super().getOffsetVariance()

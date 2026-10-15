#******************************************************************************
# -*- coding: utf-8 -*-
# File   : test_result_list.py
# Package:
# Task   : Adapted ResultList with a few convenience methods (for a 
#          "unit-test-ish" use case with plain values without a variable  
#          abstraction layer) and proxies to basic_tests functions
# Python : 3
#
# Copyright 2022 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 01.07.2022 | JoTremmel  | adapted from result_list_plus v1.0.2
#******************************************************************************
import traceback
from enum import IntEnum
from result_list import ResultList as _ResultList # @UnresolvedImport, part of test_support
from result_list import SubResult  as _SubResult  # @UnresolvedImport, dto.
from ttk_checks  import basic_tests
from ttk_checks  import adv_tests


# #############################################################################
class ResultList(_ResultList):
    """ ResultList, plus a few convenience methods """
    
    # #########################################################################
    def add(self, *items):
        """ Add a result, last item has to contain test verdict. 
            Example: 
                # result.add vs. default list.append
                result.append(["argument is a list", "with result entry items", "VERDICT"])
                result.add("items", "as separate arguments", "VERDICT")
        """
        while len(items) < 2:
            items = list(items) + [""]
        self.append(items)
    
    # #########################################################################
    def addHeader(self, text):
        self.add("\n" + text.strip(), "")
        
    # #########################################################################
    def addSubHeader(self, text):
        self.add("\xA0" + text.strip(), "")
        
    # #########################################################################
    def addInfo(self, *msg):
        self.add(*msg, "INFO")
        
    # #########################################################################
    def addError(self, msg, ex=None, show_tb=True):
        """ Add an ERROR result.
            Parameters:
                msg     - error message
                ex      - optional Exception instance to add to message
                show_tb - True: if ex has been supplied, print traceback to console
        """
        ex_info = f":\n> {type(ex).__name__}: {ex}" if ex else ""
        self.add(f"{msg}{ex_info}", "ERROR")
        if ex and show_tb:
            traceback.print_exc()
        
    # #########################################################################
    # Simple Test Methods ~~~~~~~~~~~~~~~~---
    # #########################################################################
    def addBoolean(self, *items):
        """ Add a boolean result. Last item will be interpreted as bool 
            (True=>PASSED, False=>FAILED). 
            If less than two items a present, verdict will be ERROR.
        """
        if len(items) < 2:
            verdict = "ERROR"
            items = list(items) + [""] * (2 - len(items))
        elif bool(items[-1]):
            verdict = "PASSED"
        else:
            verdict = "FAILED"
        
        # replace boolean "verdict" with keyword verdict
        items = list(items)
        items[-1] = verdict
        self.append(items)
    
    # #########################################################################
    def addEqual(self, descr=None, expected=None, actual=None, 
                 abs_tol=None, places=None, value_label="Value"):
        """ Add a result, passes if values are equal.
            Compare unittest assertEqual/assertAlmostEqual methods.
        
            Parameters:
                descr    - description of test step
                expected - expected value
                actual   - actual/measured/current value
                abs_tol  - absolute tolerance to use for numeric checks
                places   - number of decimal places to compare in numeric checks

            Note: Tested Values
                Values should be basic python types.
                In contrast to functions in ttk_checks.basic_tests, TTk variables
                (using variable abstraction with get/set methods) are _not_ 
                supported.

            Note: Tolerances
                * Specify either `abs_tol` or number of decimal `places` when 
                  checking numeric values, not both
                * If float values are tested and not tolerances have been
                  specified, a default of 7 decimal places will be checked
                  
        """
        if abs_tol is not None and places is not None:
            raise TypeError("addEqual: specify either abs_tol or places, not both")
        
        if abs_tol is not None:
            abs_tol = abs(abs_tol)
            
        if places is None:
            places = 7 # will only be used for float checks and if abs_tol is not specified
            
        is_equal = False
        check_note = ""
        error_msg = ""
        
        try:
            if (expected == actual 
                    and not isinstance(expected, float)
                    and abs_tol is None):
                # short cut, also handles non-numeric cases (strings, ...)
                #
                # Skip short cut for float values (even though it works/is value)
                # in order to always show the currently defined tolerance / 
                # checked decimal places.
                is_equal = True
                
            elif isinstance(expected, int) and isinstance(actual, int):
                # numeric check, integer values; tolerance optional
                delta = abs(expected - actual)
                if abs_tol is None or abs_tol < 1:
                    # no relevant tolerance specified
                    is_equal = (delta == 0)
                else:
                    is_equal = (delta <= abs_tol)
                    check_note = f" ± {abs_tol}"
                    
            elif isinstance(expected, float) or isinstance(actual, float):
                # numeric check with tolerance
                delta = abs(expected - actual)
                
                if abs_tol is not None:
                    is_equal = (delta < abs_tol)
                    check_note = f" ± {abs_tol}"
                else:
                    is_equal = (round(delta, places) == 0)
                    check_note = f" (within {places} decimal places)"
                    
            elif abs_tol:
                # non-numeric values, but abs_tol was given
                raise TypeError("non-numeric values supplied, but a abs_tol for numeric checks was given")
            
            else:
                # non-numeric values, non-equal
                pass 
                
        except Exception as ex:
            error_msg = f"{type(ex).__name__}: {ex}" if ex else ""
        
        info = []
        if descr:
            info.append(str(descr))
            
        expected_value = repr(expected)
        actual_value   = repr(actual)
        try:
            if isinstance(expected, IntEnum):
                expected_value = str(expected)
                actual_value   = str(type(expected)(actual))
            
            else:
                    
                if isinstance(expected, float) and abs_tol is None:
                    # check using a number of decimal places:
                    # show (only) the checked number of places
                    expected_value = f"{round(expected, places):0.{places}f}"
                
                if isinstance(actual, float) and abs_tol is None:
                    actual_value   = f"{round(actual, places):0.{places}f}"
                
        except Exception as ex:
            print(f"> addEqual: Issues during value formatting:\n{type(ex).__name__}: {ex}")
        
        value_label = str(value_label).strip()
        info.append(f"Expected {value_label}: {expected_value}{check_note}")
        info.append(f"Actual {value_label}:   {actual_value}")
        
        
        if error_msg:
            info.append(f"> {error_msg}")
            verdict = "ERROR"
        elif is_equal:
            verdict = "PASSED"
        else:
            verdict = "FAILED"
            
        self.add("\n".join(info), verdict)
    
    
    # #########################################################################
    # Forwarded basic_tests ~~~~~~~~~~~~~~~~---
    # Check results will be added to this ResultList.
    # #########################################################################
    
    # #########################################################################
    def addCheckBitMask(self, value, mask, operator="AND", bit_length=None, 
                        pass_on_true=True, descr=""):
        """ Check result of the operation given in `operator`. 
            Result will be added to this ResultList.
            Depending on parameter `pass_on_true`, the test will be PASSED if 
            the result is True (i.e. 'greater 0') or False (i.e. 'equal 0').
        
            Parameters:
                value        -  value to be checked
                mask         -  mask to be used for operation in operator
                operator     -  operator for check operation, one of 
                                ("AND", "OR", "XOR", "NAND", "NOR", "NXOR")  
                                see _basic_checks.CHECKBITMASK_*-constants.
                bit_length   -  bit length for value and mask
                pass_on_true -  if True, test will be PASSED if result is 'greater 0',
                                otherwise it will be PASSED if the result is 'equal 0'
                descr        -  user specific description shown at the start of the 
                                result text
        """
        if bit_length is None:
            bit_length = basic_tests.CHECKBITMASK_DEFAULT_BIT_LENGTH
            
        self.append(basic_tests.checkBitMask(
            value=value, mask=mask, operator=operator, 
            bit_length=bit_length, pass_on_true=pass_on_true, 
            descr=descr
        ))
    
    # #############################################################################
    def addCheckBitPattern(self, value, pattern, invert=False, descr=""):
        """ Check that a numeric value matches a certain pattern.
            Result will be added to this ResultList.
            
            Parameters:
                value     - value to check. The value must match the full pattern 
                            in order to pass. Values may be numeric (int/long),
                            string representations of binary/hexadecimal values 
                            ("0xABCD", "0b1010" etc.) or a list of bytes.
                
                pattern   - a string describing the desired bit pattern.  
                            * a pattern must always describe the full value 
                              (i.e. all bits from start to end).  
                            * a pattern starting with "0x" will be interpreted as hexadecimal 
                            * "0b" at the beginning denotes a binary pattern 
                            * "X" marks "don't care" sections (may appear anywhere in pattern)
                
                invert    -  True: inverted check: pattern must not match  
                             False: default check: pattern has to match
                
                descr     -  user specific description shown at the start of the 
                             result text
            
            Info: Pattern String Examples: 
                * `0xABC123`   - a hexadecimal 24-bit pattern
                * `123ABC`     - without a prefix, pattern defaults to hexadecimal
                * `0b0101101`  - a binary 6-bit pattern
                * `0xAABXX2`   - X designates "don't care" (4-bit-nibbles in hex 
                                 patterns)
                * `0b1XX001`   - "don't care" on a bit level in binary patterns
                * `0xAA[8]BB`  - longer "don't care"-sections can be written as
                                 a repetition number in square brackets. This example
                                 pattern is 48 bits long with 32 don't care bits in 
                                 the middle.
                * `0b10[8]00`  - as above but in a binary pattern: 12 bits with 8
                                 don't care bits in the middle.
                * `0xAA BB CC` - whitespace will be ignored for pattern check, but
                                 plain spaces will be retained in formatted 
                                 intermediate values
                * `0xab Ab aB` - patterns are not case sensitive
        """
        self.append(basic_tests.checkBitPattern(
            value=value, pattern=pattern, invert=invert, descr=descr
        ))
        
    
    # #########################################################################
    def addCheckBit(self, value, offset, status=1, descr=""):
        """ Check if the bit given by the value and offset is set or cleared 
            depending on the status.
            Result will be added to this ResultList.
            
            Parameters:
                value     -  Numeric value where the bit has to be checked
                offset    -  Offset of the bit inside of value (based on 0)
                status    -  The expected value of the bit (default 1)
                descr     -  user specific description printed on the start of the 
                             single test result
        """
        self.append(basic_tests.checkBit(
            value=value, offset=offset, status=status, descr=descr
        ))
        
    
    # #########################################################################
    def addCheckTolerance(self, current_value, rated_value,
                       rel_pos=0, abs_pos=0, rel_neg=None, abs_neg=None, 
                       invert=False, descr=""):
        """ Check if the current value is within a specified range of the rated 
            value. The range is defined by an absolute and a relative tolerance. 
            Both tolerance types will be added to get the effective tolerance. 
            Result will be added to this ResultList.
            
            Note: 
                If a _symmetric_ tolerance range is desired, only `rel_pos` and/or 
                `abs_pos` need to be set.
            
            Info: Relative Tolerances
                Relative tolerance values are specified as factors in relation to 
                the supplied `rated_value`.  
                A range of `0.0 .. 1.0` maps to `0 .. 100 %` 
            
            Info: Using both relative and absolute tolerances:
                Internally, both tolerances are added to determine the effective
                boundary values:  
                `lower_boundary = abs_neg + rel_neg * abs(rated_value) + rated_value`  
                `upper_boundary = abs_pos + rel_pos * abs(rated_value) + rated_value`  
                
                `current_value` will pass the check if its value lies between the
                calculated boundary values:  
                `lower_boundary <= current_value <= upper_boundary`
            
            Parameters:
                current_value    -   value to be checked
                rated_value      -   expected value
                rel_pos          -   (optional) relative positive tolerance 
                                      as factor, typically in range 0.0..1.0
                abs_pos          -   (optional) absolute positive tolerance
                rel_neg          -   (optional) relative negative tolerance 
                                      as factor, typically in range 0.0..-1.0
                abs_neg          -   (optional) absolute negative tolerance
                invert           -   True: inverted, check current value != rated value (+/- tolerance)  
                                     False: default: check current value == rated value (+/- tolerance)
                descr            -   user specific description printed on 
                                     the start of the single test result
        """
        self.append(basic_tests.checkTolerance(
            current_value=current_value, rated_value=rated_value,
            rel_pos=rel_pos, abs_pos=abs_pos, 
            rel_neg=rel_neg, abs_neg=abs_neg,
            invert=invert, descr=descr
        ))
        
    
    # #########################################################################
    def addCheckAbsTol(self, current_value, rated_value, abs_tol=0, invert=False, descr=""): 
        """ Check if the current value is within a specified range of the rated 
            value. The valid range is defined by an absolute tolerance as a 
            symmetric range around the `rated_value`. 
            Result will be added to this ResultList.
            
            Parameters:
                current_value    -   value to be checked
                rated_value      -   expected value
                abs_tol          -   absolute tolerance value, valid range will 
                                     be `rated_value` +/- `abs_tol`
                invert           -   True: inverted, check current value != rated value (+/- tolerance)  
                                     False: default, check current value == rated value (+/- tolerance)
                descr            -   user specific description shown before the 
                                     single test result
        """
        self.append(basic_tests.checkAbsTol(
            current_value=current_value, rated_value=rated_value, 
            abs_tol=abs_tol, invert=invert, descr=descr
        ))
        
    
    # #############################################################################
    def addCheckRelTol(self, current_value, rated_value, rel_tol=0.0, invert=False, descr=""): 
        """ Check if the current value is within a specified range of the rated 
            value. The valid range is defined by relative tolerance factor 
            (as a symmetric range around the `rated_value`). 
            Result will be added to this ResultList.
            
            Info: Relative Tolerances
                Relative tolerance values are specified as factors in relation to 
                the supplied `rated_value`.  
                A range of `0.0 .. 1.0` maps to `0 .. 100 %` 
            
            Note:
                `checkRelTol` will treat `rel_tol` values >= 1.0 as unintended and 
                mark the returned result as ERROR.  
                Use the main test function `checkTolerance` if checks with 
                tolerance values >= 100% should ever be needed.
            
            Parameters:
                current_value    -   value to be checked
                rated_value      -   expected value
                rel_tol          -   relative tolerance as factor, in range 0.0..1.0
                invert           -   True: inverted, check current value != rated value (+/- tolerance)  
                                     False: default: check current value == rated value (+/- tolerance)
                descr            -   user specific description shown before the 
                                     single test result
        """
        self.append(basic_tests.checkRelTol(
            current_value=current_value, rated_value=rated_value, 
            rel_tol=rel_tol, invert=invert, descr=descr
        ))
        
    
    # #########################################################################
    def addCheckStatus(self, current_status, nominal_status, equal=True, descr=""):
        """ Check if the current status value is identical to the nominal status
            value. Both statuses will be interpreted as int/long values for the
            comparison. 
            Result will be added to this ResultList.
            
            Note:
                If one or both values cannot be represented as integer numbers, 
                the test will fail with verdicts.ERROR.
            
            Parameters:
                current_status   -   status to be checked
                nominal_status   -   expected status to be checked against 
                equal            -   True:  check current status `==` nominal status,  
                                     False: check current status `!=` nominal status
                descr            -   user specific description printed on 
                                     the start of the single test result
        """
        self.append(basic_tests.checkStatus(
            current_status=current_status, nominal_status=nominal_status, 
            equal=equal, descr=descr
        ))
        
    
    # #########################################################################
    def addCheckRange(self, value, min_value, max_value, invert=False, descr=""):
        """ Check if value is in defined range (`min_value <= value <= max_value`).
            Result will be added to this ResultList.
            
            Parameters:
                value          -  value to be checked
                min_value      -  lower Limit
                max_value      -  upper Limit 
                invert         -  True: inverted, check that value is outside of range
                                  False: default, check that value is inside of range
                descr          -  user specific description printed on the start 
                                  of the single test result
        """
        self.append(basic_tests.checkRange(
            value=value, min_value=min_value, max_value=max_value, 
            invert=invert, descr=descr
        ))
        
    
    # #########################################################################
    def addCompare(self, left_value, operator, right_value, abs_tol=0, descr=""):
        """ Verify the conditional relationship between two operands based on 
            the given operator.
            Result will be added to this ResultList.
            
            Parameters:
                left_value  -  left operand of the relational expression
                operator    -  relational operator given as a string, see below
                right_value -  right operand of the relational expression
                abs_tol     -  absolute tolerance for equality/non-equality
                               checks of numeric types
                descr       -  user specific description printed on the start of
                               the single test result
            
            Info: Tolerance
                A a tolerance > 0 is mandatory for equality / non-equality checks 
                involving float values.  
                See checkTolerance() for more in-depth options like relative and 
                non-symmetric tolerances.
            
            Info: Relational operator strings:
                * "==" : equal to
                * "<"  : less than
                * ">"  : greater than
                * "<=" : less than or equal to
                * ">=" : greater than or equal to
                * "!=" : not equal to
        """
        self.append(basic_tests.compare(
            left_value=left_value, operator=operator, right_value=right_value,
            abs_tol=abs_tol, descr=descr
        ))
        
    
    # #############################################################################
    def addCompareCE(self, current_value, operator, expected_value, abs_tol=0, descr=""):
        """ Verify the conditional relationship between current and expected value
            based on the given operator.
            Result will be added to this ResultList.
            
            This is a compare variant with an alternative output formatting to 
            explicitly label input values as "current" and "expected".
            See also basic_tests.compare.
            
            Parameters:
                current_value  - left operand of the relational expression
                operator       - relational operator given as a string, see below
                expected_value - right operand of the relational expression
                abs_tol        - absolute tolerance for equality/non-equality
                                 checks of numeric types
                descr          - user specific description printed on the start of
                                 the single test result
            
            Info: Tolerance
                A tolerance > 0 is mandatory for equality / non-equality checks 
                involving float values.  
            
            Info: Relational operator strings:
                * "==" : equal to
                * "<"  : less than
                * ">"  : greater than
                * "<=" : less than or equal to
                * ">=" : greater than or equal to
                * "!=" : not equal to
        """
        self.append(basic_tests.compareCE(
            current_value=current_value, operator=operator, 
            expected_value=expected_value, abs_tol=abs_tol, descr=descr
        ))
        
    
    # #############################################################################
    def addContains(self, defined_values, current_value, mode="all", descr=""): 
        """ Check if current_value is an element (or sub set) of defined_values.
            Result will be added to this ResultList.
            
            Parameters:
                defined_values -  List of scalars to be searched in
                current_value  -  the function checks if this scalar or list is 
                                  contained in 'defined_values'
                mode           -  search mode (see below) 
                descr          -  user specific description printed on the start of
                                  the single test result
            
            Info: Available Modes:
                * "all":         each value of 'current_value' should be in `defined_values`
                * "any":         at least one element of 'current_value' should be in `defined_values`
                * "none"/"not":  no element of 'current_value' should be in `defined_values`
         """
        self.append(basic_tests.contains(
            defined_values=defined_values, current_value=current_value, mode=mode, 
            descr=descr, format=format
        ))
    
    # #########################################################################
    # Forwarded adv_tests ~~~~~~~~~~~~~~~~---
    # Check results will be added to this ResultList.
    # #########################################################################
    
    # #########################################################################
    def addTestVars(self, set_var_list=None, check_var_list=None, 
                    min_wait_time_ms=100, descr=''):
        """ Check the values of multiple variables/signals as a result of setting
            multiple other variables/signals. Between setting and checking, a 
            configurable time will be waited to deal with propagation delay. This
            wait time defaults to the minimum practicable wait time of all involved 
            bus signals.
            Result will be added to this ResultList.
            
            See ttk_checks.adv_tests.testVars for details.
            
            Parameters:
                set_var_list     -  Variables to set: a list of dictionaries with 
                                    variable and value 
                check_var_list   -  Variables to check: a list of dictionaries with 
                                    variable, expected value and tolerance
                min_wait_time_ms -  minimum wait time between setting variables and
                                    performing checks
                descr            -  user specific description shown at the start of 
                                    the result text
        """
        self.append(adv_tests.testVars(
            set_var_list=set_var_list, check_var_list=check_var_list, 
            min_wait_time_ms=min_wait_time_ms, descr=descr,
        ))
    

# #############################################################################
class SubResult(_SubResult, ResultList):
    def __init__(self, parent_result_list=None, divider="\n-------------------------------\n"):
        ResultList.__init__(self)
        _SubResult.__init__(
            self, parent_result_list=parent_result_list, divider=divider
        )
    
    
# #############################################################################
if __name__ == '__main__':
    results = ResultList()
    
    results.addHeader("Header")
    results.addBoolean("addBoolean, True", True)
    results.addBoolean("addBoolean, False", False)
    results.addBoolean("addBoolean, no verdict")
    
    results.addSubHeader("Sub-Header")
    results.addInfo("This is an info result")
    results.addError("addError without exception")
    try:
        raise RuntimeError("Some Exception Message")
    except Exception as ex:
        # if the exception is not "active", printing the traceback looks a
        # bit odd ("NoneType: None")
        results.addError("addError with exception", ex)
    
    results.addEqual()
    results.addEqual("Some int value", expected=1234, actual=4711)
    results.addEqual("Some float value", expected=1234.0, actual=1234.00001)
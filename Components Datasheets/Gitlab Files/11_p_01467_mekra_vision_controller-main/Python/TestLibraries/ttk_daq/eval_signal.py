#******************************************************************************
# -*- coding: utf-8 -*-
# File    : eval_signal.py
# Package : ttk_daq
# Task    : Evaluation of recorded signal data
#           (interface wrapper, see _eval_signal.py for implementation details)
# Python  : 3.6+
# Type    : Interface
#
# Copyright 2012 - 2021 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver. | Date       | Name    | Description
#------------------------------------------------------------------------------
# 1.0  | 02.07.2015 | Tremmel | initial, wrapper for _eval_signal.py 
# 1.1  | 03.07.2015 | Tremmel | fixed missing returns in seek methods
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2.1  | 08.07.2016 | Tremmel | added getEvalRangeData, 
#                             | seek()-methods now return the data value at the 
#                             | sought time (just as find()-methods return the 
#                             | timestamp at the found value)
# 2.2  | 23.12.2016 | Tremmel | added getEvalRangeData sample calls to __main__
# 2.3  | 01.12.2017 | Tremmel | added info on find() tolerances and 64bit values
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3.0.0  | 26.06.2020 | Tremmel | migrated to Python 3,  support for custom find operators,
#                               | default find tolerances now 0, updated handling
#                               | for equality checks with float-as-int-data.
# 3.1.0  | 30.11.2021 | Tremmel | added configurable seek() behavior (Task #481)
#******************************************************************************
"""
@package ttk_daq.eval_signal
Interface wrapper for recorded signal data evaluation utility class in 
ttk_daq._eval_signal.
"""
from ttk_daq import _eval_signal # @UnresolvedImport (compiled extension)
from ttk_daq._eval_signal import OperatorException # @UnresolvedImport @UnusedImport


# #############################################################################
class EvalSignal(_eval_signal.EvalSignal):
    """ Class for evaluation of recorded signal data. A signal can be searched 
        similar to an open file handle with functions to seek in time or data 
        domains.
        
        Note:
            When searching for a certain data value, data points will be
            compared individually (values will __not__ be interpolated between 
            data points).  
            The first suitable/matching entry will be used/returned instead. 
    """
    ## seek() behavior, find entry at or directly after the supplied time value
    seek_after   = "after"
    ## seek() behavior, find entry at or directly before the supplied time value
    seek_before  = "before"
    ## seek() behavior, find entry closest to the supplied time value.
    seek_closest = "closest"
    
    # #########################################################################
    def __init__(self, *args):
        """ Initialize an EvalSignal with existing data.
            
            Parameters:
                *args -  either a single signal dictionary with  
                         `{ "time": [<time1>, <time2>, ..., <timeN>], `  
                         `  "data": [<data1>, <data2>, ..., <dataN>], }`  
                         or two separate lists with time and data entries:  
                         `[<time1>, ..., <timeN>], [<data1>, ..., <dataN>]`
            
            Attention:
                Time values have to be monotonically increasing
            
            Example: Using a signal dict
                sig = EvalSignal(some_signal)
                sig = EvalSignal(mat_data["signal_1"])
            
            Example: Using separate time and data lists
                sig = EvalSignal(time_stamps, data_points)
                sig = EvalSignal(
                    [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], 
                    [  0,   1,   1,   2,   3,   5,   8,  13], 
                )
        """
        _eval_signal.EvalSignal.__init__(self, *args)
    
    # #########################################################################
    def clearAll(self):
        """ Clear all current settings (evaluation range, current position) 
            to start at the beginning of available data.
        """
        return _eval_signal.EvalSignal.clearAll(self)
    
    # #########################################################################
    # Seek current time position
    # #########################################################################
    def seek(self, time_stamp, target=seek_closest, strict=True):
        """ Seek the data point at (or near) the supplied time stamp within the 
            currently active evaluation range. Note that time values are 
            expected to be stored in monotonically increasing order.
            
            Parameters:
                time_stamp - time stamp value to seek.
                target     - target time stamp to seek, one of
                             * "after"    position at or directly after the supplied time
                                          (seek from beginning, match first value >= `time_stamp`)  
                             * "before":  position at or directly before the supplied time
                                          (seek from end, match first value <= `time_stamp`)  
                             * "closest": position at or closest to `time_stamp`
                                          (in either direction)  
                strict     - True: `time_stamp` has to fit inside the available
                                   time range (min time <= `time_stamp` <= max time).
                             False: saturate on boundary value, if possible (see note/example)
            
            Note: strict=False
                If `time_stamp` is outside the available time/evaluation range, 
                seek may return one of the boundary values (start or end of eval 
                range), depending on `target`.
                
            Example:
                sig = EvalSignal({
                    "data": [  0,   1,   2,   3,   4,   5,   6,   7,   8,   9],
                    "time": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                })
                
                # seek returns the data value at the matched time 
                sig.seek(0.42, target="closest") == 4
                sig.seek(0.42, target="before")  == 4
                sig.seek(0.42, target="after")   == 5
                
                sig.seek(0.56, target="closest") == 6
                sig.seek(0.56, target="before")  == 5
                sig.seek(0.56, target="after")   == 6
                
                # out-of-range w/ strict=False:
                sig.seek(1024, target="closest", strict=False) == 9
                sig.seek(1024, target="before",  strict=False) == 9
                sig.seek(1024, target="after",   strict=False) is None # no entry exists after time 1024
                
                sig.seek(-512, target="closest", strict=False) == 0
                sig.seek(-512, target="before",  strict=False) is None # no entry exists before time -512
                sig.seek(-512, target="after",   strict=False) == 0
            
            
            Returns the value at the specified time or None if `time_stamp` 
            is invalid / out of (evaluation) range.
        """
        return _eval_signal.EvalSignal.seek(
            self, 
            time_stamp=time_stamp, 
            target=target,
            strict=strict
        )
    
    # #########################################################################
    def seekStart(self):
        """ Seek data point at start position of currently active evaluation 
            range.
            
            Returns the value at start of range or None if current evaluation 
            range is is invalid.
        """
        return _eval_signal.EvalSignal.seekStart(self)
    
    # #########################################################################
    def seekEnd(self):
        """ Seek data point at end position of currently active evaluation 
            range.
            
            Returns the value at end of range or None if current evaluation 
            range is is invalid.
        """
        return _eval_signal.EvalSignal.seekEnd(self)
    
    # #########################################################################
    def seekMiddle(self):
        """ Seek a data point closest to the middle of currently active 
            evaluation range.
            
            Returns the value at middle of range or None if current evaluation 
            range is is invalid.
        """
        return _eval_signal.EvalSignal.seekMiddle(self)
    
    # #########################################################################
    # Eval Range 
    # #########################################################################
    def markEvalRangeStart(self):
        """ Mark/set the current entry as new start of the evaluation range.
            Returns True if the new range is valid, otherwise False.
        """
        return _eval_signal.EvalSignal.markEvalRangeStart(self)
    
    # #########################################################################
    def markEvalRangeEnd(self):
        """ Mark/set the current entry as new end of the evaluation range. 
            Returns True if the new range is valid, otherwise False.
        """
        return _eval_signal.EvalSignal.markEvalRangeEnd(self)
    
    # #########################################################################
    def clearEvalRange(self):
        """ Clear any currently limited evaluation range to include all 
            available data. 
            Current position will remain unchanged.
        """
        _eval_signal.EvalSignal.clearEvalRange(self)
    
    # #########################################################################
    def clearEvalRangeStart(self):
        """ Clear evaluation range to start at beginning of available data. 
            Current position will remain unchanged.
        """
        _eval_signal.EvalSignal.clearEvalRangeStart(self)
    
    # #########################################################################
    def clearEvalRangeEnd(self):
        """ Clear evaluation range to include all entries until the end of 
            available data.
            Current position will remain unchanged.
        """
        _eval_signal.EvalSignal.clearEvalRangeEnd(self)
    
    # #########################################################################
    def setEvalRange(self, start_time, stop_time):
        """ Limit evaluation to a defined time range. 
            Current position will be set to start of the new evaluation range.
            
            Parameters:
                start_time - first time of evaluation range
                stop_time  - last time of evaluation range
            
            Returns True if the new range has been successfully set,
            otherwise False
        """
        return _eval_signal.EvalSignal.setEvalRange(self, start_time, stop_time)
    
    # #########################################################################
    def getEvalRangeData(self):
        """ Get a copy of signal data contained in the current evaluation range.
            First entry will be the first data point at range start, last entry 
            will be the last data point at range end.
            
            Returns a dictionary with "time" and "data" lists: {  
                "time": [t0, t1, t2, ..., tn],  
                "data": [d0, d1, d2, ..., dn],  
            }  
            or None if the current evaluation range is invalid (that is, 
            start or end timestamp are undefined)
        """
        return _eval_signal.EvalSignal.getEvalRangeData(self)
    
    # #########################################################################
    # Current entry data access
    # #########################################################################
    def getValue(self):
        """ Get the current value for the current/last found entry.
            Returns a data value or None if current index position is invalid.
        """
        return _eval_signal.EvalSignal.getValue(self)
    
    # #########################################################################
    def getData(self):
        """ Alias for getValue().
            Internal lists are named "data" and "time", so a function getData 
            to get a value from data might also be expected.
            Returns a data value or None if current index position is invalid.
        """
        return _eval_signal.EvalSignal.getData(self)
    
    # #########################################################################
    def getTime(self):
        """ Get the current time stamp for the current/last found entry.
            Returns a time value or None if current position is invalid.
        """
        return _eval_signal.EvalSignal.getTime(self)
    
    # #########################################################################
    def isValid(self):
        """ Check if the current data/time/index position is valid.
            Returns True if cursor position is valid, otherwise False.
        """
        return _eval_signal.EvalSignal.isValid(self)
    
    
    # #########################################################################
    # Find operations (find in data values)
    # #########################################################################
    def find(self, operator="==", value=0, forward=True, abs_tol=0, rel_tol=0, 
             skip_current_value=False):
        """ Find the next (or previous) value in the current data that matches 
            the specified condition. 
            
            Note:
                If the current value already matches the condition, it will be 
                "found" right away unless `skip_current` is set to True.
            
            Note:
                If data consists of non-numeric entries, the contained objects
                will have to support relational operators and be comparable to 
                the supplied value
                
            
            Parameters:
                operator  - comparison operator, 
                            one of `==`, `!=`, `>=`, `>`, `<`, `<=`  
                            or a callable/function as custom operator, see Example
                value     - value to compare against
                forward   - direction of checks.  
                            True for forwards (current => end),  
                            False for backwards (current => start)
                abs_tol   - absolute tolerance value to use for numeric equality checks (`==`, `!=`)  
                rel_tol   - relative tolerance factor to use for numeric equality checks (`==`, `!=`)
                
                skip_current_value - True: the current value will be skipped (and
                                     thus not be "found"), which should be the 
                                     expected behavior when seeking a "next" or
                                     "previous" value.  
                                     See findNext(), findPrev()
                                     
            Note: float-as-int data
                If data contains only float values that were originally integers
                (some interfaces only return double/float values, regardless 
                of the original data type), then equality checks (`==`, `!=`)
                with both tolerances set to 0 will try to interpret data as
                integer values during comparison.  
                If encountered data values are too far off to be considered 
                integer, a ValueError will be raised.
                
                All other relational checks (`>=`, `>`, `<`, `<=`) will behave
                normally (tolerances will be disregarded), so e.g. 0.9999999 
                will be treated as < 1.0 and find(">=", 1) will not match it.
                
            
            Note:
                An invalid "current" position will also result in an invalid 
                "find" result.  
                This means that you can specify a sequence of multiple find() 
                operations and only check the last result in order to determine 
                that the complete sequence was valid.
            
            Attention:
                If float values are used for tolerances, the comparisons will be 
                forced to use float values. 
                Python internally uses double/float64 (IEEE-754 double-precision) 
                as data type for  "float", which will limit maximum precision.
                
                If signal data contains 64-bit integer values, the implicit
                cast to float will limit the possible integer range to 52 bits. 
                
                In order to avoid this, the `threshold`/`abs_tol` parameter 
                can be set to 0 (or any other integer value as desired). 
                This way, an integer comparison will be performed which 
                supports arbitrary bit lengths.
            
            Example:
                # e.g. signal should (within the available measurement time)
                # assume state 2, then raise to or above state 3 and remain 
                # below state 5 until the end of the measurement:
                status_sig.seekStart()
                status_sig.findNext("==", 2)
                status_sig.findNext(">=", 3)
                valid = status_sig.findNext("<", 5) is not None
                print("status valid:", valid)
            
            Example:
                # a status signal should assume status 2, followed by status 7.
                # There should be no other states in between.
                status_sig.seekStart()
                first_state_2_ts       = status_sig.findNext("==", 2)
                state_7_ts             = status_sig.findNext("==", 7)
                last_before_state_7_ts = status_sig.findPrev("!=", 7)
                status_sig.setEvalRange(first_state_2_ts, last_before_state_7_ts)
                print("no other status between 2 and 7:", status_sig.findNext("!=", 2) is None)
                
                # or with less time stamp fiddling:
                status_sig.clearAll()
                print("first status 2 at time", status_sig.findNext("==", 2))
                status_sig.markEvalRangeStart()
                
                print("first following status 7 at time", status_sig.findNext("==", 7))
                # since findPrev finds the previous match before the current "7",
                # we can simply use:
                print("no other status between 2 and 7:", status_sig.findPrev("!=", 2) is None)
            
            Example:
                # a rpm signal should raise above 2000rpm and never drop below
                # 1800rpm until the motor is stopped
                rpm_sig.setEvalRange(motor_running_ts, motor_stopped_ts)
                rpm_reached_ts = status_sig.findNext(">=", 2000)
                rpm_valid = status_sig.findNext("<=", 1800)
                print("rpm reached:", rpm_reached_ts is not None)
                print("rpm remained valid:", rpm_valid is not None)
                
                print("delay (motor enabled => rpm reached):", end=" ")
                if None not in (motor_running_ts, rpm_reached_ts):
                    print(f"{rpm_reached_ts - motor_running_ts :.3f}s")
                else:
                    print("not found")
                    
            
            Example: Custom Operator
                # A function can be used as operator to get customized behavior, 
                # for example:
                def op(current_value, target_value):
                    # Custom find() operator.
                    # Parameters:
                    #    current_value - current data value to compare
                    #    target_value  - value to compare against (from find()-parameter value) 
                    # Returns True if value was found, otherwise False 
                    return current_value & 0xFFFF > target_value & 0xFFFF
                
                sig.findNext(op)
                
            Returns a time stamp for the found value or None if no matching 
            value has been found (or if the the current data start position was 
            unspecified to begin with). 
        """
        return _eval_signal.EvalSignal.find(
             self, 
             operator=operator, 
             value=value, 
             forward=forward, 
             abs_tol=abs_tol, rel_tol=rel_tol, 
             skip_current_value=skip_current_value
        )
    
    
    # #########################################################################
    def findChanged(self, forward=True, threshold=None):
        """ Find the next (or previous) value that differs sufficiently from 
            the current value.
            
            Parameters:
                forward   - check direction.  
                            True for forwards (find next changed value),  
                            False for backwards (find previous changed value)
                threshold - threshold, absolute, to determine if a value has 
                            changed.  
                            None: automatic; uses  
                                 0.001 for float data values or  
                                 0 for integer data values  
            
            Returns the time stamp of the found value or None if no changed
            value has been found (or if the the current value was unspecified). 
        """
        return _eval_signal.EvalSignal.findChanged(
            self, 
            forward=forward, 
            threshold=threshold
        )
    
    # #########################################################################
    # convenience function wrappers
    def findNext(self, operator="==", value=0, abs_tol=0, rel_tol=0):
        """ Find next entry matching the condition. The current entry will be 
            ignored, so multiple calls to findNext() will return the time stamp
            of the next following matching entry.
            
            Returns the time stamp of the found value or None if no changed
            value has been found. See find() for details.
        """
        return _eval_signal.EvalSignal.findNext(
            self, 
            operator=operator, 
            value=value, 
            abs_tol=abs_tol, rel_tol=rel_tol
        )
    
    # #########################################################################
    def findPrev(self, operator="==", value=0, abs_tol=0, rel_tol=0):
        """ Find previous entry matching the condition. The current entry will
            be ignored, so multiple calls to findPrev() will return the time 
            stamp of the preceding matching entry.
            
            Returns the time stamp of the found value or None if no changed
            value has been found. See find() for details.
        """
        return _eval_signal.EvalSignal.findPrev(
            self, 
            operator=operator, 
            value=value, 
            abs_tol=abs_tol, rel_tol=rel_tol
        )
    
    # #########################################################################
    def findNextChanged(self, threshold=None):
        """ Find next entry that changed more than the supplied `threshold`
            from the current value.
            Parameters:
                threshold - threshold to determine if a value has changed.  
                            None: automatic; 
                            uses 0.001 for float and 0 for integer data values  
            
            Returns the time stamp of the found value or None if no changed
            value has been found. See findChanged() for details.
        """
        return _eval_signal.EvalSignal.findNextChanged(self, threshold=threshold)
    
    # #########################################################################
    def findPrevChanged(self, threshold=None):
        """ Find previous entry that changed more than the supplied `threshold` 
            from the current value.
            
            Parameters:
                threshold - threshold to determine if a value has changed.  
                            None: automatic; 
                            uses 0.001 for float and 0 for integer data values  
            
            Returns the time stamp of the found value or None if no changed
            value has been found. See findChanged() for details.
        """
        return _eval_signal.EvalSignal.findPrevChanged(self, threshold=threshold)
        

# #############################################################################
# @cond DOXYGEN_IGNORE  
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    values     = [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 7, 7, 7, 7, 0, 0]
    timestamps = [ts * 0.020 for ts in range(len(values))]
    daq_data = {'data': values, 'time': timestamps}
    
    print("# " * 60)
    for entry, data in sorted(daq_data.items()):
        print("%s: %s"%(entry, ", ".join(f"{v:4}" for v in data)))
    print("# " * 60)
    
    status_sig = EvalSignal(daq_data)
    status_sig = EvalSignal(timestamps, values)
    status_sig.seekStart()
    first_state_2_ts       = status_sig.findNext("==", 2)
    state_7_ts             = status_sig.findNext("==", 7)
    last_before_state_7_ts = status_sig.findPrev("!=", 7)
    print("first state 2 found @", first_state_2_ts) 
    print("first state 7 found @", state_7_ts)
    print("last state before 7 found @", last_before_state_7_ts)
    print()
    status_sig.setEvalRange(first_state_2_ts, last_before_state_7_ts)
    
    print("#" * 80)
    print("# getEvalRangeData (first state 2 until last state 2):")
    print(status_sig.getEvalRangeData())
    print("#" * 80)
    
    status_sig.seekStart()
    print("no other status between 2 and 7:", status_sig.findNext("!=", 2) is None)
    
    
    status_sig.clearAll()
    print("first status 2 at timestamp", status_sig.findNext("==", 2))
    status_sig.markEvalRangeStart()
    print("# marked EvalRangeStart at first status 2")
    print("first following status 7 at timestamp", status_sig.findNext("==", 7))
    # check all statuses before the first "7" until eval range start
    # are of status 2
    print("no other status between 2 and 7:", status_sig.findPrev("!=", 2) is None)
    
    print("# getEvalRangeData:")
    print(status_sig.getEvalRangeData())
    
    status_sig.clearAll()
    
    print("# EvalRangeData after clearAll():")
    print(status_sig.getEvalRangeData())
    
    print(status_sig.findNext("==", 2))
    print(status_sig.findNext("==", 2))
    print(status_sig.findNext("==", 2))
    print(status_sig.findNext("==", 2))
    print(status_sig.findNext("==", 2))
    print(status_sig.findNext("==", 2))
    
    
    print("Done.")
    
# @endcond DOXYGEN_IGNORE
# #############################################################################

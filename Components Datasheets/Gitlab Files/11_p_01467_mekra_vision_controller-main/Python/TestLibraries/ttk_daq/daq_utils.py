#******************************************************************************
# -*- coding: utf-8 -*-
# File    : daq_utils.py
# Package : ttk_daq
# Task    : utilities for data acquisition 
#           (interface wrapper, see _daq_utils.py for implementation details)
# Python  : 3.6+
# Type    : Interface
#
# Copyright 2015 - 2022 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************** Version ***********************************
#******************************************************************************
# Ver.   | Date       | Name    | Description
#------------------------------------------------------------------------------
# 1.0.0  | 02.07.2015 | Tremmel | initial, wrapper for _daq_utils.py 
# 1.1.0  | 08.07.2016 | Tremmel | added linearInterpolate, tableLookup, getInterpolatedValue
# 1.2.0  | 23.12.2016 | Tremmel | added sample for linearInterpolate
# 1.3.0  | 23.06.2020 | Tremmel | migrated to Python 3, fixed getNormalizedDaqData call
# 1.4.0  | 15.11.2021 | Tremmel | appendDaqData: configurable time between data sets
# 1.5.0  | 30.11.2021 | Tremmel | added shiftTimeAxes, printDataInfo
# 1.5.1  | 14.02.2022 | Tremmel | minor docstring updates
#******************************************************************************
"""
@package ttk_daq.daq_utils
Interface wrapper for recorded signal data utility functions in ttk_daq._daq_utils.

Most functions expect a `daq_data` structure as input, which is essentially
a dictionary containing signal-dicts with two lists:

* one list containing timestamps (in [s])
* one list containing data points / values for those timestamps. 

Both lists have to contain the same number of entries for the signal to be consistent.

### Example DAQ data structure:
    
    daq_data = { 
         <label1>: {
            'data': [<value1_0>, <value1_1>, ...], 
            'time': [<time0>,  <time1>,  ...]}, 
         },
         <label2>: {
            'data': [<value2_0>, <value2_1>, ...], 
            'time': [<time0>,  <time1>,  ...]}, 
        },
         <label3>: {
            'data': [<value3_0>, <value3_1>, ...], 
            'time': [<time2_0>,  <time2_1>,  ...]}, 
        },
    }
    

"""
from ttk_daq import _daq_utils # @UnresolvedImport (compiled extension)


# #############################################################################
def printDataInfo(values, indent_level=1, outer_n=2):
    """ Print a summary of the supplied values to stdout. Mainly intended to be
        used during development / debugging as a (somewhat) compact output of 
        DAQ data structures.
        
        Example:
            # Sample output using a DAQ data structure with two signals 
            # and the default outer_n=2
              label:
                data[20]: [100.052, 100.087, ... 100.315, 100.448]
                time[20]: [  0.000,   0.001, ...   0.018,   0.019]
              another label:
                data[20]: [ 27.162,   2.783, ...  23.078,  15.383]
                time[20]: [  0.000,   0.020, ...   0.360,   0.380]
        
        Parameter:
            values       - a scalar value or values in lists or dictionaries.
            indent_level - starting indent level (as multiple of two spaces)
            outer_n      - print only the outer n values from start and end of data.
                           None: all values will be printed
    """
    return _daq_utils.printDataInfo(
        values=values, 
        indent_level=indent_level, 
        outer_n=outer_n
    )


# #############################################################################
def getDaqDataStruct(capture_data):
    """ Get a "DAQ"-like data structure from a classic dSPACE rtplib 
        capture.Fetch() dictionary.
        
        Note:
            If a multi-core data structure contains conflicting variable names
            (e.g. same name used in multiple cores), the core name will be used 
            as prefix for all variables beyond the first.
        
        Example:
            capture_data = { # single core
                <label1>: [<value1_0>, <value1_1>, ...], 
                <label2>: [<value2_0>, <value2_1>, ...], 
                'xAxis' : [<time0>,  <time1>,  ...], 
            }
            # or 
            capture_data = { # multi core
                <core_name>: {
                    <label1>: [<value1_0>, <value1_1>, ...], 
                    <label2>: [<value2_0>, <value2_1>, ...], 
                    'xAxis' : [<time0>,  <time1>,  ...], 
                },
                <core2_name>: {
                    <label3>: [<value3_0>, <value3_1>, ...], 
                    'xAxis' : [<time2_0>,  <time2_1>,  ...], 
                }
            }
            
            # maps to 
            daq_data = { 
                 <label1>: {
                    'data': [<value1_0>, <value1_1>, ...], 
                    'time': [<time0>,  <time1>,  ...]}, 
                 },
                 <label2>: {
                    'data': [<value2_0>, <value2_1>, ...], 
                    'time': [<time0>,  <time1>,  ...]},
                },
                 <label3>: {
                    'data': [<value3_0>, <value3_1>, ...], 
                    'time': [<time2_0>,  <time2_1>,  ...]},
                },
            }
        
        Note: Time Axis:
            Signals of the same core (with identical time axes) will reference
            the *same* list of timestamps.  
            Changing timestamps of one time axis will therefore influence all 
            associated signals.
        
        Returns capture signals referenced in a daq-data structure
    """
    return _daq_utils.getDaqDataStruct(capture_data)
    

# #############################################################################
def roundDaqData(daq_data, digits=6):
    """ Round all data points in daq_data to the specified number of digits.
        
        Note:
            Data in daq_data` will be directly modified in-place.
        
        Parameters:
            daq_data  - data dictionary
            digits    - number of digits / decimal places to round to
        
        Example: Data dictionary format
            {  <label>: {
                'data': [value0, value1, ...], 
                'time': [time0,  time1, ...]}, 
            }
        
        Returns: -- (`daq_data` is modified in place)
    """
    return _daq_utils.roundDaqData(daq_data, digits=digits)
    

# #############################################################################
def getOuterTimeBoundaries(daq_data):
    """ Get minimum and maximum time stamps for all measurements in daq_data
        to contain all measurements, even if some might not have data for all
        time stamps (e.g. in case acquisition started later or stopped sooner).
        
        Example:
            [    S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1  ]
            [ S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2        ]
              ^- start                                            ^- end
        
        Returns a tuple `(min_start_time, max_end_time)`
    """
    return _daq_utils.getOuterTimeBoundaries(daq_data)
    

# #############################################################################
def getInnerTimeBoundaries(daq_data):
    """ Get minimum and maximum time stamps for all measurements in daq_data,
        so that all measurements have samples between those boundaries (i.e. 
        the overlapping section of all measurements)
        
        Example:
            [    S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1 S1  ]
            [ S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2 S2        ]
                 ^- start                                  ^- end
        
        Returns a tuple `(max_start_time, min_end_time)`.  
        If data does not overlap at all, both min/max values will be None.
    """
    return _daq_utils.getInnerTimeBoundaries(daq_data)
    

# #############################################################################
def shiftTimeAxes(daq_data, offset):
    """ Shift all time axes values in daq_data by the specified offset.
        
        Parameters:
            daq_data  - a DAQ data dict with signals.
            offset    - offset to add to all time values
        
        Note:
            * only daq_data items with "time" entries will be modified.
            * if time axes are referenced multiple times (e.g. shared between
              signals), each unique axis will only be shifted once.
            * daq_data will be modified in-place
    """
    return _daq_utils.shiftTimeAxes(daq_data, offset=offset)
    

# #############################################################################
def appendDaqData(cur_daq_data, new_daq_data, 
                  only_append_to_existing=False, time_between_s=None, 
                  verbosity=0):
    """ Append the measurement data in new_daq_data to the data in cur_daq_data.
        
        Note:
            * `cur_daq_data` will be modified directly.
            * `new_daq_data` will remain unmodified.
            * if the same time or data axes are referenced in multiple signals, 
              those references will be replaced by standalone copies.
        
        Parameters:
            cur_daq_data             - current data dictionary  
            new_daq_data             - data dictionary with data to append
            
            only_append_to_existing  - if True, only measurements that are 
                                       already in cur_daq_data will be appended 
                                       to, all others in new_daq_data will be 
                                       ignored.
                                       
            time_between_s           - time in [s] to insert between data sets
                                       (time between last point in existing data 
                                       and first new point in appended data).  
                                       None: determine suitable time from existing time steps
                                       
            verbosity                - verbosity of log output  
                                        0: only errors and "skipped signal" warnings  
                                        1: also log current signal label  
                                        2: also show summary of signal data  
        
        Example: Data dictionary format
            {  <label>: {
                'data': [value0, value1, ...], 
                'time': [time0,  time1, ...]}, 
            }
        
    """
    return _daq_utils.appendDaqData(
        cur_daq_data = cur_daq_data, 
        new_daq_data = new_daq_data, 
        only_append_to_existing = only_append_to_existing, 
        time_between_s = time_between_s,
        verbosity = verbosity
    )
    

# #############################################################################
def trimDaqData(daq_data, verbosity=0):
    """ Trim measurements in a daq data structure to the area where all 
        signals have data points (i.e. where all signals overlap).
        
        Note:
            `daq_data` will be modified in place.
            
            Time axis references will be replaced with trimmed versions (and 
            not modified in-place), so shared time axes (in case multiple each 
            signals hold a reference to the same axis data) will not cause issues.
        
        Parameters:
            daq_data  - data dictionary with measurements 
            verbosity - log verbosity;  
                         0: only error messages 
                        >0: more verbose
        
        Example: Data dictionary format
            {  <label>: {
                'data': [value0, value1, ...], 
                'time': [time0,  time1, ...]}, 
            }
        
    """
    return _daq_utils.trimDaqData(daq_data, verbosity = verbosity)
    

# #############################################################################
def getNormalizedDaqData(daq_data):
    """ Get a data dictionary with normalized/shifted time axes, so the 
        earliest data point(s) will start at time 0.0.
        
        Parameters:
            daq_data  - data dictionary with measurements 
        
        Returns a daq data dictionary where time axes start at time 0.
    """
    return _daq_utils.getNormalizedDaqData(daq_data)
    

# #############################################################################
def linearInterpolate(x, x0, y0, x1, y1):
    """ Linear interpolation at point `x` between two points `(x0, y0)` and 
        `(x1, y1)`.
        
        Text: Info:
            y1 --+-----------+--
                 |         / |  
                 |       /   |  
            y <--+-----/     |  
                 |   / |     |  
                 | /   |     |  
            y0 --+-----+-----+--
                x0     x    x1  
        
        If x is outside the specified range, the y-value will saturate 
        at the corresponding boundary. Precondition: x1 >= x0.
        
        Returns a float value `y`, interpolated between `y0` and `y1`.
    """
    return _daq_utils.linearInterpolate(x, x0, y0, x1, y1)
    

# #############################################################################
def tableLookup(x, x_values, y_values):
    """ Get an interpolated y-value for a given x-value in a x/y lookup table.
        
        Info: Limitations:
             x-values have to be monotonically increasing.  
             Both x- and y-value lists have to contain the same number of elements. 
        
        See linearInterpolate() for details.
        
        Text: Info:
            y_values
            ^
            |   |           /  
                |         /    
                |       /      
            y <-+-----/        
                |   / |        
                | /   |        
              --+-----+--------
                |     x    --> x_values
        
        Parameters:
            x        - value on x-axis for which to get a corresponding x-value 
            x_values - a list of values on the x-axis
            y_values - a list of values on the y-axis
        
        Returns an interpolated y-value for the supplied x-value. If x-value is 
        out of lookup range, y will saturate at its boundary values.
    """
    return _daq_utils.tableLookup(x, x_values, y_values)
    

# #############################################################################
def getInterpolatedValue(signal_data, time_stamp):
    """ Get a value at the specified time. Data will be interpolated if 
        timestamp falls between available data points.  
        See tableLookup() for details.
        
        Parameters:
            signal_data - a dictionary with "time" and "data" lists.
            time_stamp  - time stamp at which to get a value 
        
        Returns an interpolated value. 
    """
    return _daq_utils.getInterpolatedValue(signal_data, time_stamp)
    

# #############################################################################
# @cond DOXYGEN_IGNORE  
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    import random
    print("\n" + "#" * 120)
    print("# roundDaqData")
    length =  20
    daq_data = {
        "label": {
            "data": [random.random() for _ in range(length)],
            "time": [t * 0.001       for t in range(length)]
        }
    }
    print("before:", daq_data["label"]["data"])
    roundDaqData(daq_data, 3)
    print("after: ", daq_data["label"]["data"])
    
    print("\n" + "#" * 120)
    print("# getInterpolatedValue")
    daq_data = {
        "label": {
            "data": [v * 0.25  for v in range(length)],
            "time": [t * 0.01 for t in range(length)]
        }
    }
    print("data:", ", ".join(["%.2f"%(v) for v in daq_data["label"]["data"]]))
    print("time:", ", ".join(["%.2f"%(v) for v in daq_data["label"]["time"]]))
    
    print(getInterpolatedValue(daq_data["label"], -1000)) # should saturate
    print(getInterpolatedValue(daq_data["label"], 0.010))
    print(getInterpolatedValue(daq_data["label"], 0.015))
    print(getInterpolatedValue(daq_data["label"], 0.020))
    print(getInterpolatedValue(daq_data["label"], +1000)) # should saturate
    
    print("Done.")
# @endcond DOXYGEN_IGNORE
# #############################################################################

#******************************************************************************
# -*- coding: utf-8 -*-
# File    : data_sync.py
# Package : ttk_daq
# Task    : Examples/utilities for daq data synchronization. 
#           
#           As synchronization requirements vary with available HW and SW 
#           features, the provided functions are intended as a starting point 
#           for developing individual sync functions suitable for specific 
#           project needs.
# 
# Python  : 3.6+
#
# Copyright 2011 - 2023 iSyst Intelligente Systeme GmbH
#******************************************************************************
# Ver. | Date       | Name    | Description
#------------------------------------------------------------------------------
# 1.0  | 17.10.2011 | Tremmel | initial
# 1.1  | 11.11.2011 | Tremmel | added twoStepSynch
# 1.9  | 19.02.2013 | Tremmel | added getToggleEdgeNearestSync to twoStepSync()
#                             | which might give better sync results
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2.0  | 13.02.2015 | Tremmel | refactored from daq_utils
# 2.1  | 31.08.2017 | Tremmel | updated synchronize example with code from TTk
#                             | advanced training (now supports interpolation)
# 2.2  | 24.06.2020 | Tremmel | migrated to Python 3, added basic usage example to __main__
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3.0.0  | 26.11.2021 | Tremmel | updated synchronize to use two daq_data dicts
# 3.0.1  | 29.11.2021 | Tremmel | removed old synchronize_classic and twoStepSync
# 3.0.2  | 07.12.2023 | Tremmel | moved daq_utils import to module
#******************************************************************************
"""
@package ttk_daq.data_sync
Examples/utilities for daq data synchronization. 

Note:
    As synchronization requirements vary with available HW and SW features, 
    the provided functions are intended as a starting point for developing 
    individual sync functions suitable for specific project needs.
    
"""

from ttk_daq import daq_utils
    
# NOTE: nomenclature consistency: cal_data is called daq_data in refactored 
#       modules (but cal_data might be clearer here)


# #############################################################################
def synchronize(daq_data_a, sync_signal_a, sync_value_a,
                daq_data_b, sync_signal_b, sync_value_b,
                interpolate = True,
                offset = 0,
                ):
    """ Synchronize timestamps of two sets of DAQ measurements (a and b) by
        using a synchronization signal value change recorded in both.
        
        Note:
            * Time axes in `daq_data_a` will be updated in-place, if a sync time
              was successfully detected.  
            * `daq_data_b` will remain unmodified.
            * it is assumed that signals/measurements in a daq-data container
              are already synchronous to all other signals in that container.
        
        Parameters:
            daq_data_a      - daq_data dict structure of first set of measurements
            sync_signal_a   - name/label of sync signal in `daq_data_a`
            sync_value_a    - sync time will be found if value exceed this  
                              threshold for the first time
            
            daq_data_b      - daq_data data structure of second set of measurements
            sync_signal_b   - name/label of sync signal in `daq_data_b`
            sync_value_b    - sync time will be found if value exceed this  
                              threshold for the first time
            
            interpolate     - True: interpolate time of sync edge between the 
                                    first matching and the previous data point 
                                    (might be helpful for analog values and 
                                     slower measurements)  
                              False: use timestamp of first match 
                                     (usually preferable if sync signals are
                                      digital signals with discrete states)
            
            offset          - additional time axis offset [s] data a vs. data b.
        
        
        Note: Offset example
            If `daq_data_a`'s source is a HIL/RT capture and `daq_data_b`'s source 
            is a Calibration tool measurement, `offset` might be set to a 
            positive value to offset processing and/or filter time in ECU 
            (e.g. a 2.5ms delay due to low pass filter on ADC input plus 5ms 
             cycle time of ADC read task)
        
        Example:
            # given recorded HIL data in `hil_data` (e.g. from a real time logger) 
            # and recorded calibration data (e.g. via CANape) `cal_data`
            # as well als `hil` and `cal` variable containers:
            synchronize(
                # hil capture
                daq_data_a      = hil_data, 
                sync_signal_a   = hil.vbat, 
                sync_value_a    = 11.5, 
                
                # daq measurement
                daq_data_b      = cal_data, 
                sync_signal_b   = cal.adc_vbat, 
                sync_value_b    = 11.5, 
                
                interpolate     = True,
                # 5ms offset to compensate e.g. for input filters and (worst-case) task timing
                offset          = 0.005 
            )
            # merge synchronized data
            synched = {}
            synched.update(hil_data)
            synched.update(cal_data)
            
            # trim off excess data points to get a cleaner area if you want to create a plot 
            daq_utils.trimDaqData(synched)
            
        
        Returns True if synchronization was successful, otherwise False.  
        Time axis of `daq_data_a` will be modified in-place and synch'ed to the 
        axis of `daq_data_b`.
    """
    print("Synchronizing time axis...")
    
    def getSyncEdgeTime(signal, threshold):
        """ closure; detect timestamp where data first reaches threshold value """
        sync_time = None
        data_axis = signal.get("data", [])
        time_axis = signal.get("time", [])
        
        for index in range(len(data_axis)):
            if data_axis[index] >= threshold:
                sync_time = time_axis[index]
                if interpolate and index > 0:
                    # linear interpolate between the data point that is 
                    # above the threshold value and its predecessor
                    delta_thresh = threshold        - data_axis[index - 1]
                    delta_data   = data_axis[index] - data_axis[index - 1]
                    delta_time   = time_axis[index] - time_axis[index - 1]
                    sync_time = delta_time / float(delta_data) * delta_thresh \
                              + time_axis[index - 1] 
                break
        return sync_time
    
    # seek sync edges
    sync_time_a = getSyncEdgeTime(daq_data_a[sync_signal_a], sync_value_a)
    sync_time_b = getSyncEdgeTime(daq_data_b[sync_signal_b], sync_value_b)
    
    print("# sync-time a:", "n/a" if sync_time_a is None else f"{sync_time_a:.4f} s")
    print("# sync-time b:", "n/a" if sync_time_b is None else f"{sync_time_b:.4f} s")
    
    if (sync_time_a is not None and sync_time_b is not None):
        print("--> detected sync edges.")
        delta = sync_time_b - sync_time_a
        print(f"   time axis delta, a to b: {delta * 1000:.1f} ms")
        if offset:
            delta -= offset 
            print(f"   including manual offset:  {delta * 1000:.1f} ms")
        
        # shift time axes of all signals in daq_data_a 
        daq_utils.shiftTimeAxes(daq_data_a, offset=delta)
        print("--> time axis synchronized.\n")
        return True
    
    else:
        print("> failed to detect sync edges.")
        print("Signals will remain unsynchronized.\n")
    return False
    
    
# #############################################################################
# @cond DOXYGEN_IGNORE  
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    # See also daq_sync_example.py in HIL-Demo-Project
    from copy import deepcopy
    from matplotlib import pyplot
    from ttk_daq.daq_utils import printDataInfo
    
    
    def plot(hil_daq_data, cal_daq_data, synched_daq_data):
        """ Plot source data and synchronizes/merged data. """
        
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.html
        # "matplotlib.pyplot is a state-based interface to matplotlib. 
        #  It provides an implicit, MATLAB-like, way of plotting. It also opens 
        #  figures on your screen, and acts as the figure GUI manager.
        
        fig = pyplot.figure(figsize=(16, 8)) 
        # argument layout='tight' might be n/a in non-recent versions 
        # (e.g. not in 3.3.1, but it is available in 3.5.0)
        fig.set_tight_layout(True) # also works in 3.3.1; preferred over tight_layout=True
        fig.suptitle("data sync", x=.01, horizontalalignment="left")
        
        subplot_src1    = fig.add_subplot(311, xlabel="time", ylabel="values", title="hil data") # nrows, ncols, index
        subplot_src2    = fig.add_subplot(312, xlabel="time", ylabel="values", title="cal data") # nrows, ncols, index
        subplot_syncd   = fig.add_subplot(313, xlabel="time", ylabel="values", title="sync'd data") # nrows, ncols, index
        
        # get default colors
        prop_cycle = pyplot.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
        color_index = 0
        assigned_colors = {}
        
        def getColorForLabel(label):
            """ map colors to labels, so the same color will be assigned to 
                all signals (with a specific label) in all plots
           """
            nonlocal color_index
            if label not in assigned_colors:
                assigned_colors[label] = colors[color_index]
                color_index += 1
                if color_index > len(colors):
                    color_index = 0
            return assigned_colors[label]
        
        def addSubplotData(subplot, daq_data):
            for label, data in daq_data.items():
                if "data" not in data or "time" not in data:
                    print(f"[skipped] {label}")
                    continue
                # plot data, signals with the same label will use the same color
                subplot.plot(data["time"], data["data"], label=label, color=getColorForLabel(label))
        
        addSubplotData(subplot_src1,  hil_daq_data)
        addSubplotData(subplot_src2,  cal_daq_data)
        addSubplotData(subplot_syncd, synched_daq_data)
        
        for sp in (subplot_src1, subplot_src2, subplot_syncd):
            sp.grid(True) 
            sp.legend()
        
        # pylab.show() opens a modal control, so it does not work that well 
        # during automatic tests (but it may be nice during debugging)
        pyplot.show()
        
        # release figure memory (might not work as well in older pylab releases)
        try:
            # using a tk backend to show interactive plots may raise exceptions on 
            # clear() in some matplotlib versions (e.g. TclError: invalid command name)
            # => does not matter that much here
            fig.clear()
        except Exception:
            pass
        pyplot.close()
        
    
    def getCalDaqData():
        # daq-data, similar to recorded data using CANape
        return {
            "bar": {
                'data': [0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0], 
                'time': [0.8 + 0.001 * t for t in range(16)]
            }, 
            "cal_sync": { # sync edge at index 5
                'data': [0.0, 0.1, 0.0, 0.0, 0.0, 5.1, 4.9, 5.0, 4.9, 5.0, 5.0, 5.1, 5.0, 5.0, 4.9, 5.0], 
                'time': [0.8 + 0.001 * t for t in range(16)]
            }, 
            "baz": { # synchronous to bar and sync, but uses a different time axis step size
                'data': [0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 4.0, 0.0, 5.0], 
                'time': [0.8 + 0.002 * t for t in range(9)]
            },
        }
    
    def getHilDaqData():
        # same data as found in the older getCaptureData, 
        # but in daq_data format with individual time axes
        return { 
            "foo":      {
                "data": [0.00, 0.00, 0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90], 
                "time": [0.5 + 0.001 * t for t in range(12)]
            },
            # sync edge at index 3
            "hil_sync": {
                "data": [0.00, 0.02, 0.01, 1.10, 1.12, 1.09, 1.10, 1.11, 1.11, 1.10, 1.10, 1.10], 
                "time": [0.5 + 0.001 * t for t in range(12)]
            }
        
        }
        
    
    cal_daq_data    = getCalDaqData()
    hil_daq_data    = getHilDaqData()
    
    # for later plotting, as hil_daq_data (daq_data_a) will be modified in-place
    orig_hil_daq_data = deepcopy(hil_daq_data) 
    
    unsynched = {}
    unsynched.update(deepcopy(cal_daq_data))
    unsynched.update(deepcopy(hil_daq_data))
    
    synchronize(
        # hil capture
        daq_data_a      = hil_daq_data, 
        sync_signal_a   = "hil_sync", 
        sync_value_a    = 0.9, 
        
        # daq measurement
        daq_data_b      = cal_daq_data, 
        sync_signal_b   = "cal_sync", 
        sync_value_b    = 4.8, 
       
        interpolate     = True,
    )
    # merge synchronized data
    synched = {}
    synched.update(hil_daq_data)
    synched.update(cal_daq_data)
    
    # let time axes start at 0
    synched = daq_utils.getNormalizedDaqData(synched)
    
    print("# Before: #########################################################")
    printDataInfo(unsynched, outer_n=6)
    print("# After Sync: #####################################################")
    printDataInfo(synched, outer_n=6)
    
    # sync edges: 4th entry of hil_sync, 6th entry of cal_sync 
    # => both should now be at the same time value
    assert round(synched["hil_sync"]["time"][3], 3) == round(synched["cal_sync"]["time"][5], 3)
    
    # and before they were quite different:
    assert round(unsynched["hil_sync"]["time"][3], 3) != round(unsynched["cal_sync"]["time"][5], 3)
    
    plot(orig_hil_daq_data, cal_daq_data, synched)
    
    
    
    print("Done.")
    
# @endcond DOXYGEN_IGNORE
# #############################################################################


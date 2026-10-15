#******************************************************************************
# -*- coding: utf-8 -*-
# File : psu_arb.py
# Task : power supply unit, arbitrary sequence / waveform generation 
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 23.06.2025 | Tremmel  | initial  
#******************************************************************************
import os
import time
from _automation_wrapper_ import TestEnv
from ttk_daq.daq_utils import printDataInfo
import plot_utils


with TestEnv(testcase_id="psu_arb") as testenv:

    testresult = testenv.getResults()
    psu = testenv.getPSU()
    
    print(psu)
    
    testresult.addInfo("Defining an arbitrary sequence on channel 1")
    psu.defineSequence(
        points = (
            (0, 1, 0.5, 0,), 
            (1, 1, 0.5, 0,), 
            (2, 1, 0.5, 0,), 
            (3, 1, 0.5, 0,),
            (4, 1, 0.5, 0,),
            (5, 1, 0.5, 0,),
            
            # (5, 1, 0.5, 1,),
            # (4, 1, 0.5, 1,),
            # (3, 1, 0.5, 1,),
            # (2, 1, 0.5, 1,),
            # (1, 1, 0.5, 1,),
            # (0, 1, 0.5, 1,), 
            
            (5, 1, 0.25, 1,),
            (5, 1, 0.25, 1,),
            (4, 1, 0.25, 1,),
            (4, 1, 0.25, 1,),
            (3, 1, 0.25, 1,),
            (3, 1, 0.25, 1,),
            (2, 1, 0.25, 1,),
            (2, 1, 0.25, 1,),
            (1, 1, 0.25, 1,),
            (1, 1, 0.25, 1,),
            (0, 1, 0.50, 1,), 
        ), 
        channel=1, 
        repetitions=1, 
        hold_at_end=True)
    
    print(f"{psu.sequenceStatus(1) = }")
    print("ARBitrary:STATe (channels 1..4):", psu.sequenceStatus(channel=(1, 2, 3, 4)))
    
    testresult.addInfo("Running arbitrary sequence")
    psu.masterOutputEnable(True)
    psu.runSequence(channel=1)
    psu.channelOutputEnable(1, True)

    duration_s = 8.0
    print(f"recording for {duration_s}s...")
    start_time = time.time()
    timestamps = []
    values     = []
    while True:
        delta_s = time.time() - start_time 
        timestamps.append(delta_s)
        values.append(psu.voltage_ch1.get())
        # time.sleep(.1)
        # print(values[-1])
        if delta_s > duration_s:
            break

    print("...done")
    
    daq_data = {psu.voltage_ch1: {"data": values, "time": timestamps}}
    #print(daq_data)
    printDataInfo(daq_data, outer_n=4)
    
    print("ARBitrary:STATe (channels 1..4):", psu.sequenceStatus(channel=(1, 2, 3, 4)))

    psu.stopSequence()
    
    print("ARBitrary:STATe (channels 1..4):", psu.sequenceStatus(channel=(1, 2, 3, 4)))

    psu.masterOutputEnable(False)
    


    plot_file_path = os.path.join(testenv.getDataFolderPath(), "arbitary.png") 
    if "SingleTestManual" in plot_file_path:
        # q&d "run-standalone" detection
        plot_utils.plotSignals(daq_data) # show interactive plot
        
    plot_utils.plotSignals(daq_data, out_file_path=plot_file_path)
    
    testresult.append([
        f"[[IMG]] {plot_file_path}", # add image to result entry
        "INFO"
    ])
        
    
print("Done.")

#******************************************************************************
# -*- coding: utf-8 -*-
# File : psu_test.py
# Task : basic access tests for power supply unit
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 13.05.2025 | Tremmel  | initial  
# 1.0.1  | 19.05.2025 | Tremmel  | 
#******************************************************************************
import time
from _automation_wrapper_ import TestEnv
# from ttk_checks import basic_tests


with TestEnv(testcase_id="psu_basics") as testenv:

    testresult = testenv.getResults()
    psu = testenv.getPSU()
    
    print(psu)

    print(f"{psu.displayBrightness() = }")
    psu.displayBrightness(.4)
    print(f"{psu.displayBrightness() = }")

    psu.displayText("Test running...")

    #
    testresult.addInfo(f"Current PSU system datetime: {psu.systemDatetime()}")
    print("-" * 80)
        
    #psu.master_output_enable = True
    psu.channelOutputEnable(1, True)
    psu.channelOutputEnable(2, True)
    psu.channelOutputEnable(3, False)
    psu.channelOutputEnable(4, False)
    psu.masterOutputEnable(True)

    print(f"{psu.channelOutputEnable(1) = }")
    print(f"{psu.channelOutputEnable(2) = }")
    print(f"{psu.channelOutputEnable(3) = }")
    print(f"{psu.channelOutputEnable(4) = }")
    print(f"{psu.masterOutputEnable()   = }")
    print("-" * 80)
    
    
    psu.voltage_preset_ch1.set(2.22)
    testresult.addInfo(f"Power supply set to {psu.voltage_preset_ch1.get()} V")
    print(psu.voltage_preset_ch1.info())
    print(psu.voltage_ch1.info())

    testresult.addCheckAbsTol(
        psu.voltage_ch1, 2.22, abs_tol=0.02,
        descr="Check PSU output voltage",
    )

    psu.voltage_preset_ch1.set(12.345)
    testresult.addInfo(f"Power supply set to {psu.voltage_preset_ch1.get()} V")
    print(psu.voltage_preset_ch1.info())
    print(psu.voltage_ch1.info())
    #
    testresult.addCheckAbsTol(
        psu.voltage_ch1, 12.345, abs_tol=0.02,
        descr="Check PSU output voltage",
    )
    
    psu.channelOutputEnable(1, False)
    testresult.addInfo("Disabled Channel 1 output")
    
    # give output voltage a little time drop to zero 
    # (this may take a little without load on output)
    # time.sleep(.100)
    timeout_s = time.time() + 1.0
    while True:
        value = psu.voltage_ch1.get() 
        print(f"{value:.2f}V", end=" ")
        if value < 0.02:
            print("...ok")
            break
        if time.time() > timeout_s:
            print("...timeout")
            break
        time.sleep(0.010)
        
            
            
    testresult.addCheckAbsTol(
        psu.voltage_ch1, 0.0, abs_tol=0.02,
        descr="Voltage of disabled channel should be zero.",
    )
     
     

    testresult.addCheckRange(
        psu.temperature_ch1, 
        min_value=18, max_value=50,
        descr="Check current temperature of output channel 1",
    )
    

        
    #psu.reset()
    psu.displayText(None)

    psu.masterOutputEnable(False)
    

print("Done.")

#******************************************************************************
# -*- coding: utf-8 -*-
# File : dmm_test.py
# Task : basic access tests for digital multimeter
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 26.05.2025 | Tremmel  | initial  
#******************************************************************************
from _automation_wrapper_ import TestEnv
# from ttk_checks import basic_tests


with TestEnv(testcase_id="dmm_basics") as testenv:

    testresult = testenv.getResults()
    psu = testenv.getPSU()
    dmm = testenv.getDMM()
    
    
    psu.voltage_preset_ch1.set(2.22)
    psu.channelOutputEnable(1, True)
    psu.masterOutputEnable(True)
    
    testresult.addInfo(f"Power supply set to {psu.voltage_preset_ch1.get()} V")
    
    print(psu.voltage_preset_ch1.info())
    print(psu.voltage_ch1.info())

    testresult.addCheckAbsTol(
        psu.voltage_ch1, 2.22, abs_tol=0.02,
        descr="Check PSU output voltage",
    )

    testresult.addCheckAbsTol(
        dmm.voltage, 2.22, abs_tol=0.02,
        descr="Check DMM voltage (autorange)",
    )

    testresult.addCheckAbsTol(
        dmm.voltage_20V, 2.22, abs_tol=0.02,
        descr="Check DMM voltage (20V range)",
    )

    testresult.addCheckAbsTol(
        dmm.voltage_200mV, 2220, abs_tol=0.02,
        descr="Check DMM voltage (200mV range) => out-of-range",
        invert=True # this should fail 
    )


    psu.voltage_preset_ch1.set(12.0)
    testresult.addInfo(f"Power supply set to {psu.voltage_preset_ch1.get()} V")
    
    print(psu.voltage_preset_ch1.info())
    print(psu.voltage_ch1.info())

    testresult.addCheckAbsTol(
        psu.voltage_ch1, 12, abs_tol=0.02,
        descr="Check PSU output voltage",
    )

    testresult.addCheckAbsTol(
        dmm.voltage, 12, abs_tol=0.02,
        descr="Check DMM voltage (autorange)",
    )

    testresult.addCheckAbsTol(
        dmm.voltage_20V, 12, abs_tol=0.02,
        descr="Check DMM voltage (20V range)",
    )

    testresult.addCheckAbsTol(
        dmm.voltage_2V, 12, abs_tol=0.02,
        descr="Check DMM voltage (2V range) => out-of-range",
        invert=True # this should fail 
    )
    
    psu.voltage_preset_ch1.set(1.234)
    print(dmm.voltage.info())
    #psu.masterOutputEnable(False)
    

print("Done.")

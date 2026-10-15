#******************************************************************************
# -*- coding: utf-8 -*-
# File : ees_basics.py
# Task : basic access tests for TE-2004 Enhanced Ethernet Switch
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 23.06.2025 | Tremmel  | initial, (very) basic example
#******************************************************************************
import time
from _automation_wrapper_ import TestEnv
from pickle import NONE

with TestEnv(testcase_id="ees_basics") as testenv:

    testresult = testenv.getResults()

    ees = testenv.getEES()

    testresult.addCheckStatus(
        current_status = ees.checkAlive(),
        nominal_status = True,
        descr="Enhanced Ethernet Switch should report 'alive'"
    )
    
    
    print("-- getConfig -----------------------------------------------------")
    testresult.addInfo("getting current EES configuration")
    cfg_current = ees.getConfig()
    print(cfg_current.keys())
    
    
    print("-- validateConfig ------------------------------------------------")
    cfg_validated = ees.validateConfig(cfg_current)
    
    testresult.addBoolean(f"validateConfig: Configuration is valid", 
                          cfg_validated is not None)
    # validateConfig returns a (potentially updated) configuration, 
    # or None if supplied config was invalid

    print("-- writeConfig ---------------------------------------------------")
    testresult.addInfo("write back current configuration (in non-persistent mode)\n"
                       "Note: A 'warm' reset is required for non-persistent "
                       "configuration changes to become active")
   
    success = ees.writeConfig(cfg_current, persistent=False, allow_partial=True)
    
    testresult.addBoolean(f"Configuration successfully written", success)
    
    
    
    
    print(f"{ees.checkAlive() = }")
    print("-- warmReset ------------------------------------------------------")
    testresult.addInfo("performing a warm reset")
    ees.warmReset()
    start_time = time.time()
    timeout_s = 20.0
    while True:
        delta_s = time.time() - start_time 
        if ees.checkAlive(verbosity=1):
            testresult.add(f"EES Status: EES back to 'alive' state after {delta_s:.1f}s", "PASSED")
            break
        if delta_s > timeout_s:
            testresult.add(f"EES Status: not responding, timeout after {delta_s:.1f}s", "FAILED")
            break
        time.sleep(.100)
    
    testresult.addCheckStatus(
        current_status = ees.checkAlive(),
        nominal_status = True,
        descr="Enhanced Ethernet Switch should report 'alive' after the configration change"
    )

print("Done.")

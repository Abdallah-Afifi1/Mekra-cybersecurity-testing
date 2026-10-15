#******************************************************************************
# -*- coding: utf-8 -*-
# File : cc_test.py
# Task : basic access tests for climate chamber access
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 16.06.2025 | Tremmel  | initial  
#******************************************************************************
import time
from _automation_wrapper_ import TestEnv
# from ttk_checks import basic_tests


with TestEnv(testcase_id="cc_basics") as testenv:

    testresult = testenv.getResults()

    cc = testenv.getCC()

    cc.manualMode(True)
    print(f"{cc.manualMode() = }")
    testresult.addInfo(f"Climate chamber set to manual mode / start")

    testresult.addCheckRange(
        cc.temperature, 
        min_value = cc.MIN_TEMPERATURE,
        max_value = cc.MAX_TEMPERATURE,
        descr="Current temperature should be within climate chamber limits",
    )
    
    testresult.addCheckRange(
        cc.temperature_setpoint, 
        min_value = cc.MIN_TEMPERATURE,
        max_value = cc.MAX_TEMPERATURE,
        descr="Active temperature setpoint should be within climate chamber limits",
    )

    """
    for target_temp in (40, -10, 20):
        testresult.addHeader(f"Setpoint: {target_temp} °C")
        testresult.addInfo(f"Setting setpoint to {target_temp} °C "
                           f"and waiting to temperature to settle")
        start_time = time.time()
        try:
            cc.gotoTemperature(target_temp, settling_time_s=2)
            
            delta_s = time.time() - start_time
            testresult.addInfo(f"Chamber reached target temperature after {delta_s:.1f}s")
    
        except TimeoutError as ex:
            testresult.addError(ex)
    
        testresult.addCheckAbsTol(
            cc.temperature, target_temp, abs_tol=.5,
            descr=f"Current chamber temperature"
        )
    """   
    #cc.gotoTemperature(85, settling_time_s=2)
    #print("sleep for 8h")
    #time.sleep(28800)
    cc.gotoTemperature(-40, settling_time_s=2)
    print("sleep for 8h")
    time.sleep(28800)
    
    cc.manualMode(False)
    testresult.addInfo(f"Climate chamber manual mode cleared / stop")
    print(f"{cc.manualMode() = }")
    

print("Done.")

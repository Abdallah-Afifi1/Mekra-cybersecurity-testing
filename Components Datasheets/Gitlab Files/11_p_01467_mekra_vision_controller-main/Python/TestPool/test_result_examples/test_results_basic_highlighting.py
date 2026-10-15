#******************************************************************************
# -*- coding: utf-8 -*-
# File    : test_results_basic_highlighting.py
# Title   : Test Results – Basic Description Highlighting 
# Task    : Highlighting of description entries (basic markers)
#
# Copyright 2016 - 2023 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 07.05.2016 | Tremmel  | initial
# 1.1.0  | 22.05.2023 | Tremmel  | migrated from base project examples
#******************************************************************************
from _automation_wrapper_ import TestEnv
testenv = TestEnv()

try:
    # #########################################################################
    testenv.setup()
    # #########################################################################

    testresult = testenv.getResults()
    testresult.append(["Basic Highlighting Markers "
                       "(using default highlighting rules)",           "INFO"])
    
    testresult.append(["\xa0Highlighting 1: A Bold Description "
                       "(starting with a non-breakable space)",        "INFO"])
    
    testresult.append(["a normal test result description",           "PASSED"])
    
    testresult.append(["\nHighlighting 2: A Header-like Description "
                       "(starting with a newline)",                        ""])
    
    testresult.append(["another normal test result description",     "PASSED"])
    
    testresult.append(["´Highlighting 3: Another Bold Description "
                       "(starting with an acute accent)",              "INFO"])
    
    testresult.append(["and again a normal test result description", "PASSED"])
    
finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################

print("Done.")

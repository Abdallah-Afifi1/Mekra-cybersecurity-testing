#******************************************************************************
# -*- coding: utf-8 -*-
# File    : test_results_basics.py
# Title   : Test Results – Basics
# Task    : Basic test result entries
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
    testresult.append(["\nSome Basic Test Results", ""])
    
    # description and verdict
    # Note:
    #     both "INFO" and "FIXME" are info-level verdicts that will not
    #     influence the overall result. 
    testresult.append(["Dirty Hungarian Phrasebook", "INFO"])
    testresult.append(["My hovercraft is full of eels.", "FIXME"])
    
    # multiple descriptions and verdict
    testresult.append([
        "I will not buy this record;", 
        "it is scratched;",
        "so scratched." 
        "FAILED"
    ])

    # alternate append with += operator (extending by a single entry)
    testresult += [["Dead Parrot", "INFO"]]
    testresult += [["It's expired and gone to meet its maker. ", "FAILED"]]
    
    # appending multiple results 
    testresult += [
        ["It's not pining, it's passed on.",             "FAILED"],
        ["This parrot is no more! It has ceased to be.", "FAILED"],
    ]
    
finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################

print("Done.")

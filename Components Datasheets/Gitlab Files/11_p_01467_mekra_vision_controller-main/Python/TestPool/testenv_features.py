#******************************************************************************
# -*- coding: utf-8 -*-
# File    : testenv_features.py
# Title   : TestEnv Features
# Task    : Basic Features of TestEnv instances
#
# Copyright 2020 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 06.03.2020 | Tremmel  | initial, adapted from Advanced Training I
#******************************************************************************
from _automation_wrapper_ import TestEnv
testenv = TestEnv()


try:
    # #########################################################################
    testenv.setup()
    # #########################################################################
    
    # get a reference to the test results list
    testresult = testenv.getResults()
   
    testresult.append([" Overview of TestEnvironmentBase-Methods", ""])
    
    # set a custom meta value 
    # This will be stored in XML data, but only appear in generated reports 
    # if they are configured to show this entry.
    #
    # A meta entry added this way will behave just like entries from the 
    # script header.
    testenv.setMetaEntry("Custom Meta Key", "custom meta value")
    
    
    # get path to the configured result file for this test
    testresult.append([
        "Current test results file path:",
        "testenv.getResultsFilePath() == %r"%(testenv.getResultsFilePath()),
        "INFO"
    ])
    
    # Get a path to the folder where additional data files can be stored.
    testresult.append([
        "Current data folder path:",
        "testenv.getDataFolderPath() == %r"%(testenv.getDataFolderPath()),
        "INFO"
    ])
    testresult.append([
        "Current data folder path (without test-run-unique sub-folder):",
        "testenv.getDataFolderPath(create_safe_subfolder=False) == %r"%(
            testenv.getDataFolderPath(create_safe_subfolder=False)
        ),
        "INFO"
    ])
    
    
    # store current test results to the XML result file
    # Gets called during .breakdown(), so there is usually no need to call
    # it during normal test script execution.
    testenv.storeResults()
    
    # get seconds since start of test script (or, more accurately, since 
    # TestEnv has been instantiated)
    testresult.append([
        "Elapsed time since start of test script:",
        "testenv.getElapsedTime() == %s s"%(testenv.getElapsedTime()),
        "INFO"
    ])
    # This is mainly used for determining overall test run time 
    # print elapsed time since test start:
    testenv.printElapsedTime() 
    
    
    testresult.append([" Overview of TestEnvironmentBase-Members", ""])

    testresult.append([
        "Current test script's name",
        "testenv.script_name = %r"%(testenv.script_name), 
        "INFO"
    ])
    testresult.append([
        "Base path of current HIL-project:",
        "testenv.project_base_path = %r"%(testenv.project_base_path),
        "INFO"
    ])
    testresult.append([
        "Current TestPool folder path:",
        "testenv.testpool_path = %r"%(testenv.testpool_path),
        "INFO"
    ])
    testresult.append([
        "Path to current test script, relative to test pool folder:",
        "testenv.script_rel_path = %r"%(testenv.script_rel_path),
        "INFO"
    ])
    testresult.append([
        "Path to current test script, absolute:",
        "testenv.script_abs_path = %r"%(testenv.script_abs_path),
        "INFO"
    ])
    testresult.append([
        "Test start timestamp (set during setup()):",
        "testenv.start_time = %r"%(testenv.start_time),
        "INFO"
    ])
    testresult.append([
        "Test stop timestamp (will be updated during breakdown()):",
        "testenv.stop_time = %r"%(testenv.stop_time),
        "INFO"
    ])


    # enable or disable listing of test results during breakdown()
    testenv.show_testresults = True
    
    # project configuration access (hil_project.ini / persistence.ini)
    testenv.config.get(section="FNORD", key="foo", default="n/a")
    testenv.config.set(section="FNORD", key="foo")
    testenv.config.store()

    
    
finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################

print("Done.")

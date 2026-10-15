#******************************************************************************
# -*- coding: utf-8 -*-
# File    : test_results_extended_formats.py
# Title   : Test Results – Extended Formats
# Task    : Test result entries with extended formats
#
# Copyright 2016 - 2023 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 07.05.2016 | Tremmel  | initial
# 1.1.0  | 06.03.2020 | Tremmel  | updated examples
# 1.2.0  | 22.05.2023 | Tremmel  | migrated from base project examples
#******************************************************************************
import os
import shutil 
import random

from _automation_wrapper_ import TestEnv
testenv = TestEnv()


# #############################################################################
def plotData(data, path):  # @UnusedVariable: data
    """ Mock for some actual plot function.
        Parameters:
            data  -  data to plot, see ttk_daq DAQ data format 
                     (does not matter in this mock, though)
            path  -  output path for generated image
    """
    reports_path = testenv.config.getAbsPath("FOLDERS", "test_reports")
    try:
        if data:
            file_name = "plot.png"
        else:
            file_name = "Testbild_mini.pd.png"
            
        src = os.path.join(reports_path, "sample_data", file_name)
        shutil.copyfile(src, path)
    except EnvironmentError as ex:
        print(f"> plotData: {ex}")
        

try:
    # #########################################################################
    testenv.setup()
    # #########################################################################
    testenv.testresult = [] # just use a plain list for these examples
    # Note: This overrides the default ResultList instance, which provides
    #       some convenience features like adding a delta time stamp to each 
    #       result.
    
    testresult = testenv.getResults()


    # Just for the following examples with hardcoded paths:
    # prepare sample images/objects if we have a result container with a 
    # data/ folder
    data_path    = testenv.getDataFolderPath(create_safe_subfolder=False)
    reports_path = testenv.config.getAbsPath("FOLDERS", "test_reports")
    # Demo Project's sample images are stored in TestReports/sample_data
    samples_path = os.path.join(reports_path, "sample_data")
    
    if os.path.basename(data_path) == "data":
        for name in ("hovercraft.cc0.jpg", "scratched.cc0.jpg", "eel.cc0.png", 
                     "lorem_ipsum.txt", "eel_distribution.mat"):
            shutil.copy(os.path.join(samples_path, name), data_path)

    # Note:
    #     Usually, plots created in test scripts would be stored to the data 
    #     folder and the file's absolute output path would be added to a test 
    #     result entry.

    
    # #########################################################################
    # Images/Objects
    # #########################################################################
    testresult.append(["\nTest Results With Images", ""])
    
    # image referenced by a relative path
    # Note:
    #    Image/Object file paths in test reports will be treated as relative to 
    #    the result container folder / the full XML report, not the individual 
    #    single test result files.
    #    Full XML reports will be created in the result container folder.
    testresult.append([
        "My hovercraft is full of eels.", 
        "[[IMG]] data/hovercraft.cc0.jpg", 
        "FIXME"
    ])

    # image referenced by an absolute path
    # Note: Result Container Structure:
    #    Absolute paths that reference files in the result container folder
    #    will be resolved to paths relative to the result container.
    #    This way, the container folder can be moved without breaking references.
    testresult.append([
        "I will not buy this tobacconist's; it is scratched.", 
        "[[IMG]] %s"%(os.path.join(data_path, "scratched.cc0.jpg")), 
        "FAILED"
    ])

    

    # multiple images and one generic "object"
    testresult.append([
        "My hovercraft is full of eels "
        "and has multiple images plus\n"
        " • one generic object that may get linked to in html reports and \n"
        " • one text/plain object that will be embedded in html reports.",
        "[[IMG]] data/hovercraft.cc0.jpg", 
        "[[IMG]] data/eel.cc0.png", 
        "[[OBJ]] data/eel_distribution.mat", # this may be linked to in html reports (if the file exists)
        "[[OBJ]] data/lorem_ipsum.txt",
        "FAILED"
    ])
    
    # missing files
    testresult.append([
        "How not to be seen."
        "(files missing at report generation time will be added as a notice)",
        "[[OBJ]] data/missing file.gone",
        # Missing images will be added in HTML reports, but just show their
        # file name as alt text – unless the image gets added at the correct 
        # relative path after the report has been generated.
        "[[IMG]] data/nada.png",
        "PASSED",
    ])
    
    
    # "generated" images/plots ################################################
    def rnd(x):
        return random.random() * 12 / max(1, abs(x - num_values / 2))

    random.seed(0) # static seed to get the same dummy data every time
    num_values = 120
    data = {
        "signal": {
            "time": [t * 0.001 for t in range(num_values)], 
            "data": [rnd(x)    for x in range(num_values)]
        }
    }
    
    # Variant A: 
    # store plot to results folder and base name on single test results name:
    plot_file_path = os.path.splitext(testenv.getResultsFilePath())[0] + ".png"
    plotData(data, plot_file_path)
    
    testresult.append([
        "A result entry with a plotted figure "
        "(stored alongside the single test result)", 
        f"[[IMG]] {plot_file_path}", # add image to result entry
        "INFO"
    ])
    
    # Variant B: 
    # store plot/image to data folder (with a generated unique sub-folder)

    # getDataFolderPath defaults to create_safe_subfolder=True
    plot_file_path = os.path.join(testenv.getDataFolderPath(), "test.png") 
    plotData(None, plot_file_path)
    
    testresult.append([
        "A result entry with an image "
        "(stored in container data folder, if available)", 
        f"[[IMG]] {plot_file_path}", # add image to result entry
        "INFO"
    ])
    
    
    
    # #########################################################################
    # Test Case IDs
    # #########################################################################
    testresult.append(["\nTest Results With Test Case IDs", ""])
    
    # Note:
    #    This shows how to "manually" add test case IDs to results.
    #    See test_results_with_result_list.py for a more convenient way.
    
    # single test case ID
    testresult.append([
        "Test step with a single test case ID", 
        "[[TCID]] 1970",
        "FAILED"
    ])
    
    # multiple test case IDs can be added
    testresult.append([
        "Test step with two test case IDs", 
        "[[TCID]] 1970",
        "[[TCID]] MPFC_S2E12",
        "FAILED"
    ])
    
    # #########################################################################
    # Odds & Ends
    # #########################################################################
    testresult.append(["\nTest Results - Odds & Ends", ""])
    
    # directly added comment
    testresult.append([
        "Test result with a directly added comment:\n",
        "I will not buy this tobacconist's", 
        "[[COMMENT]] it is scratched!",
        "INFO"
    ])
    
    # manually set delta time (not really that useful, but see ResultList)
    # If a ResultList instance is used, the delta time entry will be overwritten
    # with the current delta time stamp
    testresult.append([
        "Test result with manually added delta time stamp:\n",
        "And now for something completely different", 
        "[[DELTATIME]] 12.34567",
        "INFO"
    ])
    
    
    
finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################

print("Done.")

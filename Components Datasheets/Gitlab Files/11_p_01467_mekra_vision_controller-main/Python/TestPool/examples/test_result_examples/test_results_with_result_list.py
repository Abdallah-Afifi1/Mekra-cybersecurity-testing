#******************************************************************************
# -*- coding: utf-8 -*-
# File    : test_results_with_result_list.py
# Title   : Test Results – ResultList Features
# Task    : Additional features provided by ResultList instances.
#
# Copyright 2016 - 2023 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 09.05.2016 | Tremmel  | initial
# 1.1.0  | 06.03.2020 | Tremmel  | expanded examples 
# 1.2.0  | 22.05.2023 | Tremmel  | migrated from base project examples
#******************************************************************************
import time
from _automation_wrapper_ import TestEnv
from result_list import ResultList, SubResult   # @UnresolvedImport (in .pyz)
from result_list import ChapterNumbers          # @UnresolvedImport (in .pyz)

testenv = TestEnv()

# just to get a non-zero delta time...
time.sleep(0.123)

try:
    # #########################################################################
    testenv.setup()
    # #########################################################################
    
    # by default, TestEnv uses an ResultList instance
    testresult = testenv.getResults() 
    
    
    
    # #########################################################################
    # Basic results
    # #########################################################################
    testresult.append(["\nTest Results With ResultList", ""])
    # nothing new here:
    testresult.append(["Test result with an empty verdict",             ""])
    testresult.append(["Test result with an actual verdict",      "PASSED"])
    testresult.append(["Test result with an info-level verdict",    "INFO"])
    
    
    
    # #########################################################################
    # Delta time stamps 
    # #########################################################################
    testresult.append(["\nDelta Time Stamps", ""])
    testresult.append([
        "ResultList can automatically set the delta time entry on test results, "
        "which may aid during test result analysis.",
        "Delta time will contain the seconds since test start at the time the "
        "result was added", 
        "INFO"
    ])
    
    testresult.append([
        "I will not buy this record; it is scratched.", "FAILED"
    ])
    time.sleep(0.200)
    testresult.append([
        "I will not buy this tobacconist's; it is scratched.", "FAILED"
    ])
    
    time.sleep(0.200)
    testresult.enableDeltaTime(False)
    testresult.append([
        "Test result, adding of delta time stamps disabled", "PASSED"
    ])
    testresult.enableDeltaTime(True)
    testresult.append([
        "Test result, adding of delta time stamps enabled once again", "PASSED"
    ])
    
    
    
    # #########################################################################
    # Automatic logging to console
    # #########################################################################
    testresult.append(["\nTest Result Echo", ""])
    testresult.append([
        "In order to provide progress feedback, ResultList will (by default) "
        "echo new test results on the log console (i.e. on stdout).",
        "INFO"
    ])
    testresult.enableEcho(False)
    testresult.append(["Test result, echo to log console disabled", "PASSED"])
    testresult.enableEcho(True)
    testresult.append(["Test result, echo to log console enabled", "PASSED"])
    
    
    
    # #########################################################################
    # Testcase-IDs
    # #########################################################################
    testresult.append(["\nAssigning TC-IDs", ""])
    testresult.append(["\xa0Single TC-IDs", ""])
    testresult.append([
        "A test case ID can be assigned to all following test results",
        "INFO"
    ])
    # Notes:
    # * Only one automatically assigned test case ID can be active at a time
    # * Setting a new test case ID will replace the active ID for all following 
    #   results
    # * Clearing the test case ID will stop assigning of IDs.    
    testresult.setTestcaseId("MPFC_S2E11")
    testresult.append(["How Not to be Seen",                       "PASSED"])
    testresult.append(["Crossing the Atlantic on a Tricycle",      "PASSED"])
    
    testresult.setTestcaseId("MPFC_S2E01")
    testresult.append(["The Ministry of Silly Walks",              "PASSED"])
    
    testresult.clearTestcaseId()
    testresult.append(["My hovercraft is full of eels.",           "FAILED"])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    testresult.append(["\xa0Multiple TC-IDs", ""])
    testresult.append([
        "An automatically added test case ID will supplement any existing "
        "manually defined IDs",
        "INFO"
    ])
    testresult.setTestcaseId("MPFC_S1E8")
    testresult.append(["This parrot is no more!",                  "FAILED"])
    testresult.append(["He has ceased to be!", "[[TCID]] parrot",  "FAILED"])
    testresult.append(["'E's off the twig!",   "[[TCID]] parrot",  "FAILED"])
    
    testresult.append(["'E's kicked the bucket",                   "[[TCID]] parrot", "FAILED"])
    testresult.append(["'E's expired and gone to meet 'is maker!", "[[TCID]] parrot", "FAILED"])
    testresult.append(["'Is metabolic processes are now 'istory!", "[[TCID]] parrot", "FAILED"])
    
    
    # #########################################################################
    # Chapter Numbering
    # #########################################################################
    testresult.setTestcaseId("CN-01")
    testresult.enableDeltaTime(True)
    testresult.append(["\nChapter Numbering", ""])
    testresult.append([" Default Chapter Numbering", ""])
    testresult.append([
        "A ResultList instance can be used to automatically increment or " 
        "decrement chapter numbers in \"header-type\" test result entries "
        "(i.e. entries with an empty verdict).",
        "INFO"
    ])
    
    # Chapter Commands:
    #  [#<nr>]  Set current chapter number
    #  [.]      Continue with next chapter on the current level
    #  [+]      Go one sub chapter down, add a new sub chapter
    #  [-]      Go one chapter level up, add next parent chapter
    #  [+0]     Go one sub chapter down, add new sub chapter but start a 0.
    #           This will not add an header entry in the test results. 
    #           Use [.] to start the first sub chapter.
    #  [-0]     Go one chapter level up, back to the current parent chapter
    #           This will not add an header entry in the test results (see [+0]).
    
    # start with a defined chapter number
    testresult.append(["[#2.7] Actors (defined chapter number)",    ""])
    
    # sub-chapters
    testresult.append(["[+] Valve A (new sub chapter)",             ""])
    testresult.append(["Some test for Valve A",               "PASSED"])
    
    testresult.append(["[.] Valve B (next chapter on same level)",  ""])
    testresult.append(["Some test for Valve B",               "PASSED"])
    
    testresult.append(["[.] Valve X (next chapter on same level)",  ""])
    testresult.append(["Some test for Valve X",               "PASSED"])
    
    # start a new chapter in parent level
    testresult.append(["[-] Sensors (new chapter on parent level)", ""])
    testresult.append(["Some sensor test",                    "FAILED"])
    testresult.append(["Another sensor test",                 "PASSED"])
    
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    testresult.setTestcaseId("CN-02")
    testresult.append([" Custom Chapter Numbering", ""])
    testresult.append([
        "Within ResultList, chapter numbers are handled by an instance of "
        "ChapterNumbers.\n"
        "This default instance can be replaced in case a different "
        "appearance is desired.",
        "INFO"
    ])
    
    # default settings are 
    # start_chapter="0", separator=".", number_format="%d", wrapper="[%s]"
    orig_cn = testresult.current_chapter 
    testresult.current_chapter = ChapterNumbers(
        start_chapter="3", separator="-", number_format="%02d", 
        wrapper="(Episode %s)"
    )
    testresult.append(["[.] A New Hope", ""])
    testresult.append(["A long time ago in a galaxy far, far away....", "PASSED"])
    testresult.append(["[+] Space above Tatooine", ""])
    testresult.append(["(stuff happens)", "INFO"])
    testresult.current_chapter = orig_cn

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # In case automatic chapter numbering might not be desired at all,
    # it can be completely deactivated for all following results using:
    testresult.enableChapterNumbering(False)
    
    
    
    # #########################################################################
    # Combined Sub-Results
    # #########################################################################
    testresult.setTestcaseId("RESV-01")
    testresult.append(["\nCombined Sub-Results", ""])
    testresult.append([
        "A secondary ResultList instance can be used to combine multiple "
        "sub-results into a single result entry.\n"
        "The combined result will contain all sub result data (descriptions, "
        "test case IDs, images, ...) and receive a resulting verdict.",
        "INFO"
    ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # the somewhat classic approach...
    testresult.append([" Adding a sub result entry via getCombinedResult()", ""])
    subresult = ResultList()
    subresult.enableEcho(False) # no need to echo results twice
    
    subresult.setTestcaseId("SUB-01")
    subresult.append(["A passed sub-result",        "PASSED"])
    subresult.append(["A failed sub-result",        "FAILED"])
    subresult.append(["An info-level sub-result",      "FOO"])
    testresult.append(subresult.getCombinedResult())
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    testresult.append([" Adding a sub result via SubResult", ""])
    with SubResult(testresult) as subresult:
        subresult.setTestcaseId("SUB-02")
        subresult.append(["A passed sub-result",        "PASSED"])
        subresult.append(["A failed sub-result",        "FAILED"])
        subresult.append(["An info-level sub-result",      "FOO"])
        
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # Using the SubResult context manager has the additional advantage that
    # it will automatically catch exceptions inside its context and add them
    # as ERROR results:
    testresult.append([" Error handling with SubResult context manager", ""])
    with SubResult(testresult) as subresult:
        subresult.setTestcaseId("SUB-03")
        subresult.append(["A passed sub-result", "PASSED"])
        raise(RuntimeError("Oh no!"))
        subresult.append(["A result that will never be reached", "PASSED"])
        
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    testresult.append([" Customizing Combined Results", ""])
    testresult.append([
        "Appearance of combined sub-results can be influenced by specifying "
        "custom dividers or makers for failed results",
        "INFO"
    ])
    
    # with getCombinedResult:
    subresult = ResultList()
    subresult.enableEcho(False)
    
    subresult.setTestcaseId("SUB-03")
    subresult.append(["A passed sub-result",        "PASSED"])
    subresult.append(["A failed sub-result",        "FAILED"])
    subresult.append(["An info-level sub-result",      "FOO"])
    testresult.append(
        subresult.getCombinedResult(divider="\n", failed_prefix="--> ")
    )
    
    # with SubResult
    # Note: SubResult has members named like getCombinedResult's parameters,
    #       only parameter `divider` is available in constructor
    with SubResult(testresult) as subresult:
        subresult.divider       = "\n~~~~~~~~~~~~~~~\n"
        subresult.failed_prefix = "!? "
        
        subresult.setTestcaseId("SUB-04")
        subresult.append(["A passed sub-result",        "PASSED"])
        subresult.append(["A failed sub-result",        "FAILED"])
        subresult.append(["An info-level sub-result",      "FOO"])
    
    
    testresult.append([" Combined Results: Further Options", ""])
    testresult.append([
        "Outer white-space from beginning and end of each contributing "
        "description will be trimmed by default to make output more compact.",
        "INFO"
    ])
    with SubResult(testresult, divider="\n--8<---------------\n") as subres:
        SubResult.trim_descrs = True # default setting
        subres.append(["  white spaces  ", "PASSED"])
        subres.append(["\n\nnewlines\n\n", "PASSED"])
        subres.append(["\t\t\ttabs\t\t\t", "PASSED"])
        subres.append(["\t\n\rmisc\r\n\t", "INFO"])
        # "inner" white space will be retained, that also includes newlines
        # from merged descriptions:
        subres.append(["  multiple  ", "  padded  ", "  descriptions  ", ""])
       
    testresult.append([
        "Descriptions can optionally be \"compacted\" by removing all "
        "lines from the beginning that are already present in the directly "
        "preceding sub-result's description text.",
        "INFO"
    ])
    with SubResult(testresult) as subres:
        subres.divider = "\n------------------------------------------------\n"
        # compact_descrs defaults to True in SubResults 
        # and False in ResultList.getCombinedResult
        subres.compact_descrs = True 
        subres.append(["A typical use case: combining interface test steps", ""])
        subres.append([
            "Signal: TxFooBarSig\n"
            "Description: this is a tx-signal description\n"
            "- Bar set to 11.2 bar\n"
            "TxFooBarSig: 14 V (expected: 11.2 V +/- 0.5 V)",
            "FAILED"
        ])
        # follow-up failed entry: repeated lines at beginning will be omitted
        subres.append([
            "Signal: TxFooBarSig\n"
            "Description: this is a tx-signal description\n"
            "- Bar set to 12.0 bar\n"
            "TxFooBarSig: 14 V (expected: 12.0 V +/- 0.5 V)",
            "FAILED"
        ])
        # follow-up passed entry (will be added without fail marker, 
        # but otherwise identical lines at beginning will still be skipped)
        subres.append([
            "Signal: TxFooBarSig\n"
            "Description: this is a tx-signal description\n"
            "- Bar set to 13.8 bar\n"
            "TxFooBarSig: 14 V (expected: 13.8 V +/- 0.5 V)",
            "PASSED"
        ])
        # a different entry, will be retained as-is
        subres.append(["and another test step", "INFO"])
        
    
finally:
    # #########################################################################
    testenv.breakdown()
    # #########################################################################

print("Done.")


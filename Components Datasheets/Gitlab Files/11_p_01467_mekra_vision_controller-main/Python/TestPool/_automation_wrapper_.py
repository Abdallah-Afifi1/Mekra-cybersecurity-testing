#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : _automation_wrapper_.py
# Task    : Basic functionality and definitions for test automation
# Python  : 3
#
# Copyright 2024, 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 05.05.2025 | Tremmel   | adapted for Mekra SOW2
# 1.1.0  | 26.05.2025 | Tremmel   | added Siglent DMM
# 1.2.0  | 16.06.2025 | Tremmel   | added Vötsch Climate Chamber
# 1.3.0  | 11.08.2026 | ReinerS   | added TOELLNER TOE 8941 power supply
#******************************************************************************
# basic libraries
import os
import sys
import inspect

# initialize path to test support libraries.
# ITESTSTUDIO_PATH will be set to the iTS installation path during installation
_test_support_path = os.path.join(  # iTestStudio
    os.getenv("ITESTSTUDIO_PATH", ""), "libraries", 
    "test_support%d%d.pyz"%sys.version_info[0:2] # auto-select matching support-libs
)
# derive project base path from this script's folder (which has to be the TestPool)
_test_pool_path = os.path.abspath(inspect.currentframe().f_code.co_filename)
_test_pool_path = os.path.dirname(_test_pool_path)       # module located in TestPool folder
_base_project_path = os.path.dirname(_test_pool_path)    # parent is Python project folder
_base_project_path = os.path.dirname(_base_project_path) # parent is main/base project folder


# #######################################
# Import Test Environment ~~~~~~~~~~~---
# #######################################
_test_support_path = os.path.normpath(_test_support_path)
if _test_support_path not in sys.path:
    # insert test support in search order right after the "current" folder
    sys.path.insert(1, _test_support_path)

from test_environment import TestEnvironmentBase      # @UnresolvedImport, part of test_support
from test_environment import appendSysPath, getConfig # @UnresolvedImport, dto.

# get configured folder paths
config = getConfig(_base_project_path)
if _test_pool_path != config.getAbsPath("FOLDERS", "test_pool"):
    # _automation_wrapper_.py should be in TestPool
    print("> please check test pool path configured in hil_project.ini")
_test_libs_path = config.getAbsPath("FOLDERS", "test_libs") 


# #######################################
# Project Libraries ~~~~~~~~~~~~~~~~~---
# #######################################
appendSysPath(_test_libs_path)
from bridged import bridged


# #######################################
# Project-specific Modules ~~~~~~~~~~~---
# #######################################
# import hil_variables
from test_result_list import ResultList, SubResult # extended result_list

from tools.rhode_schwarz import psu_ngp800
from tools.toellner      import psu_toe8941
from tools.siglent       import dmm_sdm3065x
from tools.voetsch       import cc_vt7004
from tools.technica      import ees_te200x
from tools.dhcp.dhcp_server import DHCPServer

# #############################################################################
# Test Environment ~~~~~~~~~~~~~~~~---
# #############################################################################
class TestEnv(TestEnvironmentBase):
    """ Test environment automation access helper/wrapper. """
    
    # #########################################################################
    def __init__(self, testcase_id=None):
        """ Parameters:
                testcase_id - active test case ID to set on test start (if any)
        """
        # init base class 
        super().__init__(_base_project_path)
        
        self.psu  = None # R&S Power Supply
        self.toe  = None # TOELLNER Power Supply
        self.dmm  = None # Siglent Digital Multimeter 
        self.cc   = None # Vötsch Climate Chamber
        self.ees  = None # Technica Enhanced Ethernet Switch
        self.DHCPServer = None # DHCP Server

       
        self.testresult = ResultList() # custom extended ResultList class, overrides default instance
        self.testresult.setTestcaseId(testcase_id)
    
    # #########################################################################
    def setup(self):
        """ Test Setup: initialize test environment. """
        super().setup()
        
        
        # custom report meta-data entries could be added here 
        # (in addition to meta entries extracted from test script header):
        # self.setMetaEntry("Custom Meta Name", "Custom Meta Value")
        
    
    # #########################################################################
    def breakdown(self):
        """ Test breakdown: cleanup & housekeeping. """
        # restore previous values
        # if self.hil:
        #     self.hil.resetAll()
        
        if self.psu:
            self.psu.close()
            self.psu = None

        if self.toe:
            self.toe.close()
            self.toe = None

        if self.dmm:
            self.dmm.close()
            self.dmm = None

        if self.cc:
            self.cc.close()
            self.cc = None
            
        if self.DHCPServer:
            self.DHCPServer.close()
            self.DHCPServer = None    
            
        # self.ees has a stateless interface, no need to close() it

        # the base's breakdown() will handle, among other things, storing of 
        # the current test results 
        super().breakdown() 
        
    
    
    # #########################################################################
    # On-demand tool init ~~~~~~~~~~~~~---
    # #########################################################################
    def getPSU(self):
        """ Power supply / variables """
        if self.psu is None:
            self.psu = psu_ngp800.NGP800Series(visa_address="TCPIP0::192.168.10.10")
        
        return self.psu
        
    # #########################################################################
    def getPSU_TOE(self):
        """ TOELLNER power supply (single output) / variables """
        if self.toe is None:
            # USB-Option TOE 8940/025 enumerates as a USB-to-serial virtual
            # COM port, NOT as USB-TMC. Verify the COM port number assigned
            # by Windows in the device manager.
            self.toe = psu_toe8941.TOE8941(visa_address="ASRL4::INSTR")

        return self.toe

    # #########################################################################
    def getDMM(self):
        """ Digital multimeter / variables """
        if self.dmm is None:
            self.dmm = dmm_sdm3065x.SDM3065X(visa_address="TCPIP0::192.168.10.20",
                                             timeout_ms=4000)
        
        return self.dmm
    
    # #########################################################################
    def getCC(self):
        """ Climatic Chamber / variables """
        if self.cc is None:
            #self.cc = cc_vt7004.VT7004(ip_addr="127.0.0.1", timeout_ms=2000) # mock-server
            self.cc = cc_vt7004.VT7004(ip_addr="192.168.10.40", timeout_ms=2000)
        
        return self.cc
    
    # #########################################################################
    def getEES(self):
        """ Enhanced Ethernet Switch """
        if self.ees is None:
            self.ees = ees_te200x.TE200x(ip_addr="10.104.3.30")
        return self.ees
    
    
    # #########################################################################
    # Calibration and HIL Var Containers ~~~~---
    # #########################################################################
    
    # #########################################################################
    # def getHil(self):
    #     """ Get an instance of an object containing all defined hil/model
    #         variables.
    #     """
    #     # since the ubiquitous self.hil has been initialized during setup,
    #     # we can just return it here
    #     return self.hil
        
    
    # #########################################################################
    def subresult(self, divider="\n-------------------------------\n"):
        """ Convenience access to a subresult of the main testresults.
            Example:
                with testenv.subresult() as subresult:
                    subresult.addInfo("Hello World")
        """
        # use SubResult of extended result list
        return SubResult(self.testresult, divider=divider)
    
    
    # #########################################################################
    # Context Manager - for convenience 
    # #########################################################################
    def __enter__(self):
        """ Start TestEnv as context manager. 
            
            Note:
                This should only be used once per test script, as there is only
                a single test result file name per test script. Multiple calls 
                to setup/breakdown would therefore just overwrite the previous 
                results.
            
            Example:
                with TestEnv() as testenv:
                    testresult = testenv.getResults()
                    testresult.append(["Hello World!", "PASSED"])
        """
        self.setup()
        return self
    
    # #########################################################################
    def __exit__(self, exc_type, exc_value, tb):  # @UnusedVariable
        """ End context manager. """
        self.breakdown()
        
        # We could return True to suppress any raised exception (but then 
        # current exception info should be added as a ERROR result).
        # Raising active exceptions here will make debugging in IDEs more
        # convenient, though (as most provide "jump to line" features in 
        # exception tracebacks).
        # Note that the test runner will deal with raised exceptions that
        # ended test execution and add them as ERROR results.
        return False
    
    
    # #########################################################################
    # Explicit bridges to inherited functions ---
    # (so auto-complete from static analysis works better)
    @bridged
    def getResults(self):
        """ Get a reference to the test results list. """
        
    @bridged
    def getDataFolderPath(self, create_safe_subfolder=True):
        """ Get a path to the folder where additional data files can be stored. """
        
    @bridged
    def getResultsFilePath(self):
        """ Get a path to the file in which results will/should be stored. """
        
    @bridged
    def setMetaEntry(self, name, value):
        """ Set an (additional) meta entry to be saved with the test results. """
        

# #############################################################################
# Main
# #############################################################################
if __name__ == "__main__":
    print("Test Support Path:   ", _test_support_path)
    print("Project Path:        ", _base_project_path)
    print("Test Pool Path:      ", _test_pool_path)
    print("Test Libraries Path: ", _test_libs_path)
    print()
    print(config)

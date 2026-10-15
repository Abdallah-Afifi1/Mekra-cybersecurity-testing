#******************************************************************************
# -*- coding: utf-8 -*-
# File : dhcp_test.py
# Task : basic test for dhcp server
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 02.07.2025 | Völler J | initial  
#******************************************************************************
#
#
#Imports:
#
from _automation_wrapper_ import TestEnv
# from ttk_checks import basic_tests
from tools.dhcp.dhcp_server import DHCPServer
import socket

#Testcase:
with TestEnv(testcase_id="dhcp_test") as testenv:
    
    testresult = testenv.getResults()
    psu = testenv.getPSU()
    dmm = testenv.getDMM()
    
    
    psu.voltage_preset_ch1.set(24.00)
    psu.channelOutputEnable(1, True)
    psu.masterOutputEnable(True)
    
    testresult.addInfo(f"Power supply set to {psu.voltage_preset_ch1.get()} V")
    
    print(psu.voltage_preset_ch1.info())
    print(psu.voltage_ch1.info())

    testresult.addCheckAbsTol(
        psu.voltage_ch1, 24.00, abs_tol=0.10,
        descr="Check PSU output voltage",
    )
    
    
    my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                               68, [0xC0, 0xA8, 0x78, 0x04],
                               [51, 4, 0x00, 0x00, 0x00, 0x3C], 1024,
                               renew_ip=False, wait_for_discovery=True)
    my_dhcpserver.server()
    
    my_dhcpserver.s.close()
    
    
    
    
    
print("Done.")
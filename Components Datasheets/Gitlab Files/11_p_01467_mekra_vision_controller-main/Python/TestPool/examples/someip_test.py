#******************************************************************************
# -*- coding: utf-8 -*-
# File : someip_test.py
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
from tools.SOMEIP import someip_commands
from tools.dhcp.dhcp_server import DHCPServer
from time import sleep
from tools.GStreamer.gstreamer import GStreamer

import socket
import os



file_path = os.path.dirname(os.path.abspath(__file__))
test_rep_dir = file_path + '\\SOMEIP\\'
test_rep_dir = test_rep_dir.replace("\\", "/")
if not os.path.exists(test_rep_dir):
    os.makedirs(test_rep_dir)

gst = GStreamer(test_rep_dir)



#Testcase:
with TestEnv(testcase_id="someip_test") as testenv:
    
    testresult = testenv.getResults()
    psu = testenv.getPSU()
    #dmm = testenv.getDMM()
    
    
    psu.voltage_preset_ch4.set(28.00)
    psu.channelOutputEnable(4, True)
    psu.masterOutputEnable(True)
    

    testresult.addInfo(f"Power supply set to {psu.voltage_preset_ch4.get()} V")
    
    print(psu.voltage_preset_ch4.info())
    print(psu.voltage_ch4.info())

    testresult.addCheckAbsTol(
        psu.voltage_ch4, 28.00, abs_tol=0.10,
        descr="Check PSU output voltage",
    )
    
    
    my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                               68, [0xC0, 0xA8, 0x78, 0x0A],
                               [51, 4, 0x00, 0x00, 0x3C, 0x3C], 1024,
                               renew_ip=True, wait_for_discovery=True)
    my_dhcpserver.server()
    	
     
    sleep(2)
    rx =someip_commands.subscribeROIVideo(b'\x40\x01\x27\x0F')
    sleep(0.5)
    rx =someip_commands.subscribeROIVideo(b'\x10\x01\x27\x0F')
    gst.stream_background(port=5015, encoding='H264')
    gst.stream_background(port=5025, encoding='H264')
    sleep(10)
    rx =someip_commands.unSubscribeROIVideo(b'\x40\x01\x27\x0F')
    sleep(0.5)
    rx =someip_commands.unSubscribeROIVideo(b'\x10\x01\x27\x0F')
    sleep(5)

 
    
    my_dhcpserver.s.close()
    
    psu.channelOutputEnable(3, False)
    
    
    
    
    
print("Done.")
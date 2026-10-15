#******************************************************************************
# -*- coding: utf-8 -*-
# File : TempLogTest.py
# Task : basic access tests for climate chamber access
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 10.09.2025 | ReinerS  | initial  
#******************************************************************************
import time
from time import sleep
from datetime import datetime
from _automation_wrapper_ import TestEnv
# from ttk_checks import basic_tests
#from SOMEIP import someip_commands
from tools.SOMEIP import someip_commands
from tools.dhcp.dhcp_server import DHCPServer
from tools.GStreamer.gstreamer import GStreamer
import socket
import os
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import numbers
from datetime import datetime, timedelta

file_path = os.path.dirname(os.path.abspath(__file__))
test_rep_dir = file_path + '\\SOMEIP\\'
test_rep_dir = test_rep_dir.replace("\\", "/")
if not os.path.exists(test_rep_dir):
    os.makedirs(test_rep_dir)

gst = GStreamer(test_rep_dir)

with TestEnv(testcase_id="TempLogTest") as testenv:
    
    
    #ini##################################
    testresult = testenv.getResults()
    psu = testenv.getPSU()
    dmm = testenv.getDMM()
    
    #log###################################
    # Create a new Excel workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Messwerte"

    # Define the headers
    headers = ["Zeit", "Spannung in V", "Strom in A", "Leistung in W", "ccTemp in °C", "pT1000 in °C"]
    ws.append(headers)
    
    
    #Power#################################
    
    psu.voltage_preset_ch4.set(28)
    psu.channelOutputEnable(4, True)
    psu.masterOutputEnable(True)
    
    testresult.addInfo(f"Power supply set to {psu.voltage_preset_ch4.get()} V")
    
    print(psu.voltage_preset_ch4.info())
    print(psu.voltage_ch4.info())
    
    testresult.addCheckAbsTol(
        psu.voltage_ch4, 28, abs_tol=0.02,
        descr="Check PSU output voltage",
    )

    #gstreamer#################################

    my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                               68, [0xC0, 0xA8, 0x78, 0x0A],
                               [51, 4, 0x00, 0x00, 0x3C, 0x3C], 1024,
                               renew_ip=True, wait_for_discovery=True)
    my_dhcpserver.server()

    sleep(2)
    rx =someip_commands.subscribeROIVideo(b'\x40\x01\x27\x0F')
    gst.stream_background(port=5015, encoding='H264')
    sleep(0.5)
    
    #psu#####################################

    testresult.addCheckAbsTol(
        psu.voltage_ch4, 16, abs_tol=0.02,
        descr="Check PSU output voltage",
    )

    for i in range (16, 0, 0,5):
        psu.voltage_preset_ch4.set(i)
        #Check Video stream 
        

    #cleanup#################################
    rx =someip_commands.unSubscribeROIVideo(b'\x40\x01\x27\x0F')
    sleep(0.5)
 
    my_dhcpserver.s.close()
   
    psu.channelOutputEnable(4, False)
    psu.masterOutputEnable(False)

    testresult.addInfo(f"Climate chamber manual mode cleared / stop")
    print(dmm.temperature.info())

print("Done.")

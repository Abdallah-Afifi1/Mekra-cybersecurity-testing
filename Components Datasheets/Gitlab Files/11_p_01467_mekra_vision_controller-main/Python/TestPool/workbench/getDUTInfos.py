#******************************************************************************
# -*- coding: utf-8 -*-
# File : getDUTInfors.py
# Task : basic access tests for climate chamber access
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 09.10.2025 | ReinerS  | initial  
#******************************************************************************
import time
import pandas as pd
import someipy
from time import sleep
from datetime import datetime
from _automation_wrapper_ import TestEnv
# from ttk_checks import basic_tests
from tools.SOMEIP import someip_commands

from tools.dhcp.dhcp_server import DHCPServer
from tools.GStreamer.gstreamer import GStreamer
from tools.helpFunctions import evaluate
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


with TestEnv(testcase_id="getDUTInfos") as testenv:
    
    
    #ini##################################
    testresult = testenv.getResults()
    psu = testenv.getPSU()
    dmm = testenv.getDMM()
    
    #log###################################
    # Create a new Excel workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "DUTvalues"

    # Define the headers
    headers = ["Time stamp", "Voltage in V", "Current in A", "Power in W", "getCamIdent", "getDataSheet"]
    ws.append(headers)
    
    
    #Power#################################
    
    psu.voltage_preset_ch4.set(28)
    psu.channelOutputEnable(4, True)
    psu.masterOutputEnable(True)
    
    testresult.addSubHeader(f"Power supply set to {psu.voltage_preset_ch4.get()} V")
    
    print(psu.voltage_preset_ch4.info())
    print(psu.voltage_ch4.info())
    
    testresult.addCheckAbsTol(
        psu.voltage_ch4, 28, abs_tol=0.02,
        descr="Check PSU output voltage",
    )

    #gstreamer#################################

    my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                               68, [0xC0, 0xA8, 0x78, 0x0A],
                               [51, 4, 0x00, 0x3C, 0x3C, 0x3C], 1024,
                               renew_ip=True, wait_for_discovery=True)
    my_dhcpserver.server()

    sleep(2)
    rx, ex = someip_commands.subscribeROIVideo(b'\x80\x00\x00\x00')
    rx = rx.get_formatted_packet(rx)
    ex = ex.get_formatted_packet(ex)
    testresult.addCompareCE(rx, "==", ex, 0, "compare somieip massage")
    data = ""
    for i in range(7):
        data += str(rx[i]) + "\t\t " +  str(ex[i]) + "\n"
    testresult.addInfo(data)

    
    #testresult.addCompareCE(str(rx), "==", str(ex), 0, "hallo das ist eine Test")
    #print(someip_commands.subscribeROIVideo(b'\x40\x01\x27\x0F'))

    sleep(1)
    #someip_commands.subscribeROIVideo(b'\x80\x00\x00\x00')
    gst.stream_background(port=5015, encoding='H264')
    #gst.stream_background(port=5025, encoding='H264')
    
    data = []
    
    time.sleep(10)
    #get data form the DUT######################
    """
    
    nowTime = str(str(datetime.now()).split(" ", 1)[1]).split(".")[0]
    voltage = float(str(psu.voltage_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
    current = float(str(psu.current_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
    power = float(str(psu.power_ch4.info().split(" ", 1)[1]).split(" ", 1)[0])
    getCamIdent = someip_commands.getCamIdentification()
    getDataSheet = someip_commands.getDataSheet()
    ws.append([nowTime, voltage, current, power, getCamIdent, getDataSheet])
    data.append([nowTime, voltage, current, power, getCamIdent, getDataSheet])
    print(nowTime, voltage, current, power, getCamIdent, getCamIdent)

    rx = someip_commands.getCamIdentification()

    """
    
    # Example measurement data (can be replaced with actual data)

    # Append the data rows
    #for row in data:
    #    ws.append(row)

    # Create a table for the data range
    table = Table(displayName="MesswerteTabelle", ref=f"A1:F{len(data)+1}")
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                        showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    table.tableStyleInfo = style
    ws.add_table(table)


    # Adjust column widths  
    for col in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col)
        adjusted_width = max_length + 2
        ws.column_dimensions[col[0].column_letter].width = adjusted_width

    # Save the workbook
    wb.save(r"D:\VSC-GitLab\11_p_01467_mekra_vision_controller\TestReports\DUTvalues.xlsx")

    #cleanup#################################
    rx =someip_commands.unSubscribeROIVideo(b'\x40\x01\x27\x0F')
    sleep(0.5)
    #rx =someip_commands.unSubscribeROIVideo(b'\x10\x01\x27\x0F')
    #sleep(0.5)
 
    my_dhcpserver.s.close()
   
    psu.channelOutputEnable(4, False)
    psu.masterOutputEnable(False) 

    print(dmm.temperature.info())

print("Done.")

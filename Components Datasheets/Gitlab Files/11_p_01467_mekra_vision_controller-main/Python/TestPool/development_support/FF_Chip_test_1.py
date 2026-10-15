#******************************************************************************
# -*- coding: utf-8 -*-
# File : FF_Chip_test_1.py
# Task : basic access tests for climate chamber access
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 15.12.2025 | ReinerS  | initial  
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

#Test parameters
startTemp = 70#70
finalTemp = 85#85
stepDuration = 1200#sec1200

with TestEnv(testcase_id="FF_Chip_test_1") as testenv:
    
    
    #ini##################################
    testresult = testenv.getResults()
    cc = testenv.getCC()
    psu = testenv.getPSU()
    dmm = testenv.getDMM()
    
    #log###################################
    # Create a new Excel workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Messwerte"

    # Define the headers
    headers = ["Zeit", "Spannung in V", "Strom in A", "Leistung in W", "ccTemp in °C", "pT1000 in °C", "socTemp in °C"]
    ws.append(headers)
    

    #Temperature chamber#################################
    cc.manualMode(True)
    print(f"{cc.manualMode() = }")
    testresult.addInfo(f"Climate chamber set to manual mode / start")

    testresult.addCheckRange(
        cc.temperature, 
        min_value = cc.MIN_TEMPERATURE,
        max_value = cc.MAX_TEMPERATURE,
        descr="Current temperature should be within climate chamber limits",
    )
    
    testresult.addCheckRange(
        cc.temperature_setpoint, 
        min_value = cc.MIN_TEMPERATURE,
        max_value = cc.MAX_TEMPERATURE,
        descr="Active temperature setpoint should be within climate chamber limits",
    )
    
    #funktion test
    psu.voltage_preset_ch4.set(28)
    psu.channelOutputEnable(4, True)
    psu.masterOutputEnable(True)
    my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                               68, [0xC0, 0xA8, 0x78, 0x0A],
                               [51, 4, 0xFF, 0xFF, 0xFF, 0xFF], 1024,
                               renew_ip=True, wait_for_discovery=True)
    my_dhcpserver.server()
    sleep(1)
    rx =someip_commands.subscribeROIVideo(b'\xC0\x00\x00\x03')
    sleep(1)
    rx =someip_commands.subscribeROIVideo(b'\x00\x00\x00\x0A')
    gst.stream_background(port=5015, encoding='H264')
    gst.stream_background(port=5048, encoding='H264')
    print("funktion test")
    sleep(30)
    rx =someip_commands.unSubscribeROIVideo(b'\xC0\x00\x00\x03')
    sleep(0.5)
    rx =someip_commands.unSubscribeROIVideo(b'\x00\x00\x00\x0A')
    sleep(0.5)
    my_dhcpserver.s.close()
    psu.voltage_preset_ch4.set(28)
    psu.channelOutputEnable(4, False)
    pt1000 = float(str(dmm.temperature.info().split(" ", 1)[1]).split(" ", 1)[0])
    print(pt1000)
    #preheat
    cc.gotoTemperature(startTemp, 0.5, 10)
    print("Wait 45 min until the DUT has acclimatized")
    sleep(2700)#Wait 1 hour until the DUT has acclimatized
    
    
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
    sleep(3)
    #gstreamer#################################

    my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                               68, [0xC0, 0xA8, 0x78, 0x0A],
                               [51, 4, 0xFF, 0xFF, 0xFF, 0xFF], 1024,
                               renew_ip=True, wait_for_discovery=True)
    my_dhcpserver.server()
    
    sleep(1)
    rx =someip_commands.subscribeROIVideo(b'\xC0\x00\x00\x03')
    sleep(1)
    rx =someip_commands.subscribeROIVideo(b'\x00\x00\x00\x0A')
    gst.stream_background(port=5015, encoding='H264')
    gst.stream_background(port=5048, encoding='H264')
    
    print("Wait 20 minutes")
    sleep(stepDuration)#Wait 20 minutes until the DUT has acclimatized.
    sleep(5)
    try:
        count = 0
        for target_temp in range (startTemp, finalTemp +1 , 2):
            if target_temp >= finalTemp:
                break  

            print("Wait until the DUT has acclimatized")
            data_between = cc.gotoTemperatureContinuousData2(target_temp, count, psu, dmm, target_accuracy=0.5, settling_time_s = stepDuration)

            for data_point in data_between:
                ws.append(data_point)
                print(data_point)

            
            data = [[]]
            #count = count + 1
            
            if data_between[-1][3] < 3:
                break
        
        data_between = cc.gotoTemperatureContinuousData2(finalTemp, count, psu, dmm, target_accuracy=0.5, settling_time_s = stepDuration)
        for data_point in data_between:
                ws.append(data_point)
                print(data_point)       

    except TimeoutError as ex:
        testresult.addError(ex)
        #cleanup#################################
        rx =someip_commands.unSubscribeROIVideo(b'\xC0\x00\x00\x03')
        sleep(0.5)
        rx =someip_commands.unSubscribeROIVideo(b'\x00\x00\x00\x0A')
        sleep(0.5)

        my_dhcpserver.s.close()
        # Save the workbook
        now = datetime.now()
        PATH = r"D:\VSC-GitLab\11_p_01467_mekra_vision_controller\TestReports"
        timestamp = now.strftime('%H-%M-%S_%d.%m.%Y')
        FILENAME = os.path.join(PATH, "1_dataLog_" + timestamp + ".xlsx")
        wb.save(FILENAME)
        psu.channelOutputEnable(4, False)
        psu.masterOutputEnable(False)
        #cc.gotoTemperature(target_temp=20, settling_time_s=2) #cool down to 20°C   
        cc.manualMode(False)
        testresult.addInfo(f"Climate chamber manual mode cleared / stop")

    testresult.addCheckAbsTol(
        cc.temperature, target_temp, abs_tol=1,
        descr=f"Current chamber temperature"
    )


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
    
    # Set number formats for relevant columns
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=6):
        for cell in row:
            cell.number_format = numbers.FORMAT_NUMBER_00
    
    # Adjust column widths
    for col in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col)
        adjusted_width = max_length + 2
        ws.column_dimensions[col[0].column_letter].width = adjusted_width

    # Save the workbook
    now = datetime.now()
    PATH = r"D:\VSC-GitLab\11_p_01467_mekra_vision_controller\TestReports"
    timestamp = now.strftime('%H-%M-%S_%d.%m.%Y')
    FILENAME = os.path.join(PATH, "1_dataLog_" + timestamp + ".xlsx")
    wb.save(FILENAME)


    #cleanup#################################
    rx =someip_commands.unSubscribeROIVideo(b'\xC0\x00\x00\x03')
    sleep(0.5)
    rx =someip_commands.unSubscribeROIVideo(b'\x00\x00\x00\x0A')
    sleep(0.5)
 
    my_dhcpserver.s.close()
    psu.channelOutputEnable(4, False)
    psu.masterOutputEnable(False)
    cc.gotoTemperature(target_temperature=20, settling_time_s=2) #cool down to 20°C 
    print("cool down 1/2h")
    time.sleep(1800)  
    cc.manualMode(False)
    testresult.addInfo(f"Climate chamber manual mode cleared / stop")
    print(f"{cc.manualMode() = }")
    print(dmm.temperature.info())

print("Done.")

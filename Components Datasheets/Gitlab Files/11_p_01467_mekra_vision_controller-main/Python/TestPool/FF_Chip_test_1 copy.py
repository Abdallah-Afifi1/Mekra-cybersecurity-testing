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
import serial
import threading
import re
import pandas as pd
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
    headers = ["Zeit", "Spannung in V", "Strom in A", "Leistung in W", "ccTemp in °C", "pT1000 in °C"]
    ws.append(headers)
    

    
    #Temperature chamber#################################
    #cc.manualMode(True)
    #print(f"{cc.manualMode() = }")
    #testresult.addInfo(f"Climate chamber set to manual mode / start")

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
    sleep(10)

    
    def extract_temperature(uart_line: str) -> float | None:
        """
        Extrahiert die Temperatur in Celsius aus einer UART-Logzeile.
        Gibt die Temperatur als float zurück oder None, falls nichts gefunden.
        """
        match = re.search(r'Celsius\s+([-+]?\d+(?:\.\d+)?)', uart_line)
        if match:
            return float(match.group(1))
        return None

    def uart_logger(port, baudrate, stop_event):
        ser = serial.Serial(port, baudrate, timeout=1)
        
        while not stop_event.is_set():
            if ser.in_waiting:
                line = ser.readline().decode(errors="ignore")
                global UARTtemp
                UARTtemp = extract_temperature(line)    
        ser.close()

    
    stop_event = threading.Event()

    uart_thread = threading.Thread(
        target=uart_logger,
        args=("COM5", 115200, stop_event),
        daemon=True
    )

    uart_thread.start()

 
    count = 0
    for target_temp in range (startTemp, finalTemp +1 , 2):    

        testresult.addHeader(f"Setpoint: {target_temp} °C")
        testresult.addInfo(f"Setting setpoint to {target_temp} °C "
                        f"and waiting to temperature to settle")
        start_time = time.time()
        
        
        try:
            print("Wait until the DUT has acclimatized")
            data_between = cc.gotoTemperatureContinuousData2(target_temp, count, psu, dmm,target_accuracy=0.5, settling_time_s = stepDuration)
            #data_between = cc.gotoTemperatureContinuousData2(target_temp, count, psu, target_accuracy=0.5, settling_time_s = stepDuration)
            
            delta_s = time.time() - start_time
            testresult.addInfo(f"Chamber reached target temperature after {delta_s:.1f}s")
            
            #only data after reaching the first temperature is recorded
            #data before first temperature point is not relevant
            #if count > 0: 
            for data_point in data_between:
                ws.append(data_point)
                print(data_point)
            #in case of camera failing (indicated by drop in leistung below 5W)
            #loop is exited 
            
            data = [[]]
            #count = count + 1
            
            if data_between[-1][3] < 3:
                break
    
        
        except TimeoutError as ex:
            testresult.addError(ex)
            #cleanup#################################
            rx =someip_commands.unSubscribeROIVideo(b'\x40\x01\x27\x0F')
            sleep(0.5)
            rx =someip_commands.unSubscribeROIVideo(b'\x10\x01\x27\x0F')
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
    rx =someip_commands.unSubscribeROIVideo(b'\x40\x01\x27\x0F')
    sleep(0.5)
    rx =someip_commands.unSubscribeROIVideo(b'\x10\x01\x27\x0F')
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

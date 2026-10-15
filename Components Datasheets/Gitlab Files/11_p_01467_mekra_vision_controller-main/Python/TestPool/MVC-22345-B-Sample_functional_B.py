#******************************************************************************
# -*- coding: utf-8 -*-
# File : MVC-22345-B-Sample_functional_B.py
# Task : B-sample functional test, power supply TOELLNER TOE 8941
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 12.02.2026 | ReinerS  | initial  
# 1.1.0  | 11.08.2026 | ReinerS  | variant of MVC-12345-B using TOELLNER TOE 8941
#******************************************************************************
import os
from time import sleep
import pandas as pd
import numpy as np
import serial

from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_commands
from tools.dhcp.dhcp_server import DHCPServer
from tools.GStreamer.gstreamer import GStreamer
from tools.ServiceDiscovery.servicediscovery import ServiceDiscovery
from tools.RtpSniffer import rtpSniffer

from datetime import datetime
from reference_value.production_data import Volvo_Standard_1Gbit_SN00012315
from reference_value.SW_config import PAR_10C0

file_path = os.path.dirname(os.path.abspath(__file__))
test_rep_dir = file_path + '\\Data_import\\'
test_rep_dir = test_rep_dir.replace("\\", "/")
if not os.path.exists(test_rep_dir):
    os.makedirs(test_rep_dir)



excel_path = os.path.join(test_rep_dir, 'Musterüberprüfung.xlsx')

df = pd.read_excel(excel_path)
array = df.to_numpy()

dic = {"Lfd_Nr": None,
        "MEKRA-Nr":None,
        "Bezeichung": None,
       "device_type":None,
       "volvoNr":None,
       "volvoNr_cam":None,
       "volvoIndex_rev":None,
       "cam_index": None,
       "snpn":None,
       "PAR":None,
       "SNr":None,
       "mac-address_dmc":None,
       "mac-address":None,
       "date":None,
       "DMC": None}


def cleanup():
    try:
        someip_commands.unSubscribeROIVideo(b'\xC0\x00\x00\x03')
        sleep(0.5)
        someip_commands.unSubscribeROIVideo(b'\xC0\x00\x00\x0A')
        #someip_commands.someip_cleanup()
        psu.outputEnable(False)
    except:
        pass

try:
           

    with TestEnv(testcase_id="MVC-22345-B-Sample_functional_B") as testenv:
        try:
            
            
            #ini##################################
            testresult = testenv.getResults()
            psu = testenv.getPSU_TOE()
            #read DMC-code
            dmcScan = True
            while dmcScan == True:
                dmc = input("pleae scan the camera DMC: ")
                #Search for the correct line based on the camera DMC
                if dmc in array:
                    for line in array:
                        if dmc in line:
                            for i, key in enumerate(dic.keys()):
                                dic[key] = line[i]
                            dmcScan = False
                else:
                    print("Camera is not in list")
            testresult.append(["\n" + str(dmc),           "INFO"])
                
            #Power_On#################################
            psu.outputEnable(False)
            sleep(1)
            psu.voltage_preset.set(28)
            psu.outputEnable(True)
            testresult.addSubHeader(f"Power supply set to {psu.voltage_preset.get()} V")
            print(psu.voltage_preset.info())
            print(psu.voltage.info())
            testresult.addCheckAbsTol(
                psu.voltage, 28, abs_tol=0.02,
                descr="Check PSU output voltage",
            )

            #start_dhcp######################################
            my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                                    68, [0xC0, 0xA8, 0x78, 0x0A],
                                    [51, 4, 0xFF, 0xFF, 0xFF, 0xFF], 1024,
                                    renew_ip=True, wait_for_discovery=True)
            my_dhcpserver.server()
            
            #get sample infos################################
            for i in range(3):
                try:
                    sd = ServiceDiscovery("239.120.1.1", 30490)
                    sd.connect()
                    sd_msg = sd.getSDMessage(sender="192.168.120.10", timeout=2)
                    sd.disconnect()
                    configuration = sd_msg.configuration()
                    print("1")
                    rxpacket, exPacket = someip_commands.getCamIdentification()
                    print("2")
                    rxpayload = rxpacket.get_payload()
                    break
                except:
                    print('ERROR: no getPayload')  
                    testresult.append(['no getPayload', 'ERROR'])
                    if i >= 3:
                        testresult.append(['no getPayload possible', 'ERROR'])
                        testenv.breakdown()
                    else:
                        sleep(15)
                        testresult.append(['retry getCamIndentification', 'INFO'])
                        continue
                    
            #define camera index#############################
            if configuration["device_type"] is not None:
                if configuration["device_type"] == 'acam_2s':
                    indexNr = "01"
                elif configuration["device_type"] == 'rcam_2':
                    indexNr = "02"
                elif configuration["device_type"] == 'acam_2':
                    indexNr = "03"
                else:
                    print("Camera typ is not defined")
            else:
                print("Camera have no device_type")
                
            if rxpayload[0:10] is not None:
                volvoNrCam = rxpayload[0:10][2:]
                s = str(rxpayload[0:10][:2])
                #CamIndex = chr(int(s, 16)) + str(indexNr)
                if rxpayload[0:10][:1] == '4':
                    CamIndex = ''
                    CamIndex = 'B' + '0' + str(rxpayload[0:10][1:2])
                    
    
            else:
                print("error: Camera have no snpn")
            
            #Compare DMC#####################################
            testresult.addCompareCE(str(dmc),   "==", str(dic["DMC"]),   0, "compare DMC")

            #Compare camera memory data
            #testresult.addCompareCE(configuration['scan-------'],   "==", dic["MEKRA-Nr"],      0, "compare MEKRA-Nr")
            testresult.addCompareCE(str(configuration['device_type']),   "==", dic["device_type"],   0, "compare device_type")
            testresult.addCompareCE(str(volvoNrCam),                        "==", str(dic["volvoNr_cam"]),       0, "compare volvoNr")
            #testresult.addCompareCE(configuration['???--------'],   "==", dic["volvoIndex_rev"],0, "compare volvoIndex_rev")
            testresult.addCompareCE(str(CamIndex),                       "==", str(dic["cam_index"]),     0, "compare cam_index")
            testresult.addCompareCE(str(rxpayload[0:10]),                "==", str(dic["snpn"]),          0, "compare snpn")
            #testresult.addCompareCE(configuration['scan-------'],   "==", dic["PAR"],           0, "compare PAR")
            testresult.addCompareCE(str(int(configuration['serial_nb'])),     "==", str(dic["SNr"]),           0, "compare SNr")
            testresult.addCompareCE(str(configuration['mac_address']),   "==", str(dic["mac-address"]),   0, "compare mac-address")

            #print(rxpayload[0:10]) #snpn 
            #print(rxpayload[10:18]) # SN
            #print(rxpayload[18:30]) # mac
            
            #subscribe HVS and MVS#####################################
            sleep(0.5)
            rx, ex =someip_commands.subscribeROIVideo(b'\xC0\x00\x00\x03')

            rx = rx.get_formatted_packet(rx)
            ex = ex.get_formatted_packet(ex)
            testresult.addCompareCE(rx,"==", ex, 0, "compare subscribe command HVS")
            sleep(0.5)
            rx, ex =someip_commands.subscribeROIVideo(b'\xC0\x00\x00\x0A')
            rx = rx.get_formatted_packet(rx)
            ex = ex.get_formatted_packet(ex)
            testresult.addCompareCE(rx,"==", ex, 0, "compare subscribe command MVS")
            
            
            #select path#####################################
            file_path = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.abspath(os.path.join(file_path, "..", ".."))
            file_path = os.path.join(file_path, "TestReports", "Initial_Test")
            file_path = os.path.join(file_path, "TestData")
            test_rep_dir = file_path.replace("\\", "/") #importen for gStreamer ini
            if not os.path.exists(test_rep_dir):
                os.makedirs(test_rep_dir)

            #ini gStreamer#####################################
            gst = GStreamer(test_rep_dir)
            
            #Measure current#####################################
            sleep(10)
            testresult.addCheckAbsTol(
                psu.current, 0.16, abs_tol=0.08,
                descr="Check PSU current",
            )
            
            #RTP sniffer#########################################
            imageString = str(configuration["mac_address"]) + "_" + str(configuration["serial_nb"])
            try:
                rtp_info = rtpSniffer.parseStream(5015)
                if rtp_info is not None:
                    try:
                        testresult.append(["The RTP-sniffer detected frames on the HVS.", 'PASSED'])
                        sleep(0.5)
                        gst.picture(port=5015, filename=imageString + "_HVS", encoding='H264')
                        sleep(0.5)
                        testresult.append([
                            "image HVS", 
                            f"[[IMG]] {os.path.join(file_path,str(imageString) + "_HVS" + ".jpg")}", 
                            "INFO"
                        ])
                    except:
                        print("ERROR: No RTP-Packets")
                else:
                    testresult.append(["The RTP sniffer did not detect any frames on the HVS.", 'FAILED'])
                
            except:
                testresult(['There was a problem with the rtp sniffer or gStreamer.', 'ERROR'])
            sleep(0.5)
            try:
                rtp_info = rtpSniffer.parseStream(5048)
                if rtp_info is not None:
                    try:
                        testresult.append(["The RTP-sniffer detected frames on the MVS.", 'PASSED'])
                        sleep(0.5)
                        testresult.append(['It may be that metadata in the stream prevents a .jpg from being created.', 'INFO'])
                        gst.picture(port=5048, filename=imageString + "_MVS", encoding='H264')
                        sleep(0.5)
                        testresult.append([
                            "image MVS", 
                            f"[[IMG]] {os.path.join(file_path,str(imageString) + "_MVS" + ".jpg")}", 
                            "INFO"
                        ])
                    except:
                        print("ERROR: No RTP-Packets")
                else:
                    testresult.append(["The RTP sniffer did not detect any frames on the MVS.", 'FAILED'])
                
            except:
                testresult(['There was a problem with the rtp sniffer or gStreamer.', 'ERROR'])

        
            #unSubscribe HVS and MVS#####################################
            sleep(1)
            rx, ex =someip_commands.unSubscribeROIVideo(b'\xC0\x00\x00\x03')
            rx = rx.get_formatted_packet(rx)
            ex = ex.get_formatted_packet(ex)
            testresult.addCompareCE(rx,"==", ex, 0, "compare unSubscribe command HVS")
            sleep(0.5)
            rx, ex =someip_commands.unSubscribeROIVideo(b'\xC0\x00\x00\x0A')
            rx = rx.get_formatted_packet(rx)
            ex = ex.get_formatted_packet(ex)
            testresult.addCompareCE(rx,"==", ex, 0, "compare unSubscribe command MVS")
            sleep(2)
            

            cleanup()
            sleep(3)
                
        except KeyboardInterrupt:
            loop = False
            print("Test interrupted")


finally:
    # #########################################################################
    cleanup()
    my_dhcpserver.s.close()
    someip_commands.someip_cleanup()
    sleep(0.5)
    testenv.breakdown()
    # #########################################################################

print("Done.")

#******************************************************************************
# -*- coding: utf-8 -*-
# File: MVC-92869_-_getCamIdentification.py
# Task: SOME/IP Camera Service REQUEST for SNPN (Slave Node Part Number),
#       serialNumber and macAddress. SOME/IP Camera Service REQUEST is not 
#       defined in ISO 17215. Request is needed for Volvo Diagnosis-Tool.
#       Link: MVC-92869 - getCamIdentification (https://erg-polarion-p1.mekra.net/polarion/redirect/project/11_P_01467_MEKRA_Vision_Controller/workitem?id=MVC-92869)
# 
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 24.02.2026 | Völler J.  | initial  
#******************************************************************************
import os
from time import sleep

from _automation_wrapper_ import TestEnv
from tools.SOMEIP import someip_commands
from tools.dhcp.dhcp_server import DHCPServer

from tools.ServiceDiscovery.servicediscovery import ServiceDiscovery

from tools.DUT_Settings import prod, to_dict


abc = to_dict(prod)
    
print(abc)

with TestEnv(testcase_id="MVC-92869 - getCamIdentification") as testenv:
    
    
    #ini##################################
    testresult = testenv.getResults()
    psu = testenv.getPSU()

 

    #Power#################################
    psu.channelOutputEnable(4, False)
    sleep(1)
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

    #dhcp######################################
    
    my_dhcpserver = DHCPServer(67, [0xC0, 0xA8, 0x78, 0x01],
                               68, [0xC0, 0xA8, 0x78, 0x0A],
                               [51, 4, 0xFF, 0xFF, 0xFF, 0xFF], 1024,
                               renew_ip=True, wait_for_discovery=True)
    my_dhcpserver.server()
    
    
    
    #get sample infos################################
   



    #print(rxpayload[0:10]) #snpn 
    #print(rxpayload[10:18]) # SN
    #print(rxpayload[18:30]) # mac



finally:
    # #########################################################################
    #cleanup#################################
    my_dhcpserver.s.close()
    cleanup()
    sleep(0.5)
    testenv.breakdown()
    # #########################################################################

print("Done.")

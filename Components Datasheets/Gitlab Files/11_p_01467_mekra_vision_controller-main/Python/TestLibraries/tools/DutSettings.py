# this file represents the settings assigned to the DUT (device under test)
# these are:
# 1 variant-settings: parameter file
# 2 software information
# 3 camera settings for communication

import pathlib
from tools.CameraSettings import CameraSettings

class VariantSettings:
    # for tests that use the parameter-file as test-input/as expected values.
    # may be relevant for variant-tests and feature-tests
    #pythonParameterFile = pathlib.Path("ParameterFiles/MCPV02C_PAR39A_SN2563_98D3D2001003.py")
    #pythonParameterFile = pathlib.Path("ParameterFiles/MCPI10C_PAR41A1_SN4201_98D3D2001069.py")
    #pythonParameterFile = pathlib.Path("ParameterFiles/MCPV02C_PAR45A2_SN4189_98D3D200105d.py")
    #pythonParameterFile = pathlib.Path("ParameterFiles/MCPV02C_PAR50A_SN4100_98D3D2001004.py")
    #pythonParameterFile = pathlib.Path("ParameterFiles/MCPI09D_PAR41A_SN4101_98D3D2001005.py")
    #pythonParameterFile = pathlib.Path("ParameterFiles/MCPV02C_PAR48B_SN60_98D3D200003c.py")
    #pythonParameterFile = pathlib.Path("ParameterFiles/MCPV02C_PAR39B_SN55_98D3D2000037.py")
    pythonParameterFile = pathlib.Path("ParameterFiles/MCPI09D_PAR32B_SN65_98D3D2000041.py")
    pythonParameterFile = 0
    
    
    #pythonParameterFile = pathlib.Path("ParameterFiles/PAR99E05.py")

class ExpectedSoftwareInfo:
    # expected SW version, compared with values from getDataSheet.
    # Also used as string for test report
    uc_sw_version = "02C"
    uc_sw_timestamp = "20230315_1333"

#------------- Example CameraSettings ---------------------#
camera_settings_SOW2_Gbit = CameraSettings(camera_ip="192.168.120.10",
                                 camera_service_port= 50501,    # istr der Ziel-Port, an dem die cam die SOMI-IP msg erwartet. TestPC->cam
                                 sd_ip="239.0.0.1", # ist die IP an die die cam die SD-msg sendet
                                 sd_port=30490, # ist der Ziel-port, an den die cam die SD-msg sendet. cam->TestPC
                                 rtp_dest_port=5015)




                                     
camera_settings = camera_settings_SOW2_Gbit


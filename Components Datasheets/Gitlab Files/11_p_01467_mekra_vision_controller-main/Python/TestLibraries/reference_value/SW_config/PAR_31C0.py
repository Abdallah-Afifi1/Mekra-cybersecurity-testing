#SW Configuration Data: Renault Slim 100Mbit


parVer = bytes([0x33, 0x31, 0x43, 0x30]) # --> "31C0"


device_type = acam_2s

#someIpSdConfigurationOption = 0x18 + "mac_address=" + macAddress (in Ascii) + 0x12 + "serial_nb=" + serialNumber (in Ascii) + 0x12 + "device_type=acam_2s" + 0x00

someIpSdSourcePort = 0x771A #(30490)
someIpSdDestinationPort = 0x771A #30490)
someIpSdDestinationIp = bytes([0xef, 0x78, 0x01, 0x01]) #0xEF780101 (239.120.1.1)
cameraServicePort = 0x7725 #(30501)
shutterSupported = 0x01
T_imager_auto_on = 0x00F0 # --> 15,0°C
T_imager_auto_off = 0x0140 # --> 20,0°C
T_imager_protection_on = 0x0410 # --> 65,0°C
T_imager_protection_off = 0x03C0 # --> 60,0°C
numbersOfRegionOfInterest = 0x02
RtpSourcePort1 = 0x138C #(5004)
RtpSourcePort2 = 0x1396 #(5014)
RtpDestinationIp1 = bytes([0x00, 0x00, 0x00, 0x00]) #0x00000000 (0.0.0.0)
RtpDestinationIp2 = bytes([0x00, 0x00, 0x00, 0x00]) #0x00000000 (0.0.0.0)
RtpDestinationPort1 = 0x138d #(5005)
RtpDestinationPort2 = 0x13ae #(5038)
RtpVlanId1 = 0x00
RtpVlanId2 = 0x00

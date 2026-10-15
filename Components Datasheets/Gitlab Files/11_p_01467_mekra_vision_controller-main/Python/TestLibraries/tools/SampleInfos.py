from tools.helpFunctions import helperModule
import scapy.all as scapy

import tools.DutSettings

class BasicInfo:
    def __init__(self, camera_settings):
    # camera settings of type SystemTestCases.General.CameraSettings.CameraSettings
        #self.sw_version = f"{tools.DutSettings.ExpectedSoftwareInfo.uc_sw_version}_{tools.DutSettings.ExpectedSoftwareInfo.uc_sw_timestamp}"
        #self.hw_version = tools.TestReportSettings.hw_version
        #self.department = tools.TestReportSettings.department
        #self.customer = tools.TestReportSettings.customer
        #self.project_name = tools.TestReportSettings.project_name

        # serveral ips are used for running tests that require SOME/IP messages from different clients
        self.client_ip = [192,168,120,1]
        #self.client_ip_2 = tools.TestEnvironmentSettings.client_ip_2
        #self.client_ip_3 = tools.TestEnvironmentSettings.client_ip_3
        #self.client_source_port = tools.TestEnvironmentSettings.client_source_port
        # Climate chamber
        #self.voetsch_ip = tools.TestEnvironmentSettings.voetsch_ip
        #self.voetsch_port = tools.TestEnvironmentSettings.voetsch_port

        # search for network-interface using client_ip
        # this is required for sniffing with scapy, not requred for most of the tests
        for iface in scapy.conf.ifaces.values():
            # iface.ips is a dictionary with '4' and '6' as keys representing ipv4 resp. ipv6 addresses
            # only search ipv4 addresses for our address
            if self.client_ip in iface.ips[4]:
                self.sniffing_interface = iface
                break
        else:
            self.sniffing_interface = "no interface selected"  

        # expected SW version, compared with values from getDataSheet
        self.uc_sw_version = tools.DutSettings.ExpectedSoftwareInfo.uc_sw_version
        self.uc_sw_timestamp = tools.DutSettings.ExpectedSoftwareInfo.uc_sw_timestamp

        # SX-SysTest: what's the difference between "server_ip" and "default_ip"?
        # "server_ip" is used for most test-cases as destination ip for sending SOME/IP requests
        # "default_ip" is used mostly by DHCP-test-cases that modify the IP during the test to
        # "reset" the ip to a known-value (aka default) at the end of a test.
        # why is "last octet of server_ip" = "last octet of default_ip+1"?
        # this is due to implementation of the dhcp_server-python module, which, if renew_ip is not set
        # to true, increments the ip that is assigend to the dhcp-client (the camera) by one (+1).
        # sroehrl: this really is not very nice

        # camera_ip as string
        self.server_ip = str(camera_settings.camera_ip)

        # default_ip as list
        default_ip_to_be_modifed = list(camera_settings.camera_ip.packed)       
        # substrating 1 only works if the last octet of ip is at least 2
        assert(default_ip_to_be_modifed[3] >= 2)
        default_ip_to_be_modifed[3]-=1

        self.default_ip = default_ip_to_be_modifed

        self.client_destination_port = camera_settings.camera_service_port

        self.sd_ip = camera_settings.sd_ip
        self.sd_port = camera_settings.sd_port
        # destination RTP-port from camera point of view, NOT the RPT-base-port from parameter file
        self.rtp_port = camera_settings.rtp_dest_port

        print("\n\n===========================================")
        print("self.sd_ip = {}".format(self.sd_ip))
        print("self.sd_port = {}".format(self.sd_port))
        print("self.server_ip = {}".format(self.server_ip))
        print("===========================================\n\n")

        self.serial_nb = helperModule.get_sample_serial_nb(self.sd_ip, self.sd_port, sender=self.server_ip)
        self.mac_address = helperModule.get_sample_mac_address(self.sd_ip, self.sd_port, sender=self.server_ip)
        self.device_type = helperModule.get_sample_device_type(self.sd_ip, self.sd_port, sender=self.server_ip)
        self.part_number = helperModule.get_sample_configstring(self.sd_ip, self.sd_port, sender=self.server_ip)

        # SX-SysTest: used by all test-implementations as part of the test-report file name
        # use values from camera as file name
        self.type = f"{self.device_type}_{self.serial_nb}"   

        print("Using the following settings for communication:\n")
        print(camera_settings)
        print("using the following device for scapy-sniffing:")
        print(f"{self.sniffing_interface.name}: {self.sniffing_interface.description}")
        print("\n")

class Info(BasicInfo):
    # SX-SysTest: this class is used by all test-implemenations.To avoid the refactoring of all test
    # implementations when improving this "configuration"-file (SampleInfos.py), we keep the "Info"-class and its member variables
    # as legacy interface to all test implementations. If this is ever to be refactored, it probably should be designed differently.

    def __init__(self):
        super().__init__(tools.DutSettings.camera_settings)



import ipaddress
from tools.helpFunctions import helperModule
from tools.ServiceDiscovery.servicediscovery import ServiceDiscovery
# required when camera starts with no ip-address (like in realDHCP use case)
from tools.dhcp.dhcp_server import DHCPServer



class CameraSettings:
# this class keeps the information required to communicate with a camera and receive video stream
    def __init__(self, camera_ip, camera_service_port, sd_ip, sd_port, rtp_dest_port):
        self.camera_ip = ipaddress.ip_address(camera_ip)

        # port where the SOME/IP-messages are sent to
        self.camera_service_port = camera_service_port

        self.sd_ip = sd_ip
        self.sd_port = sd_port
        # destination RTP-port from camera point of view, NOT the RPT-base-port from parameter file
        self.rtp_dest_port = rtp_dest_port
    def __str__(self) -> str:
        return_string = f"""camera ip: {self.camera_ip}
camera service port: {self.camera_service_port}
service discovery address: {self.sd_ip}
service discovery port: {self.sd_port}
RTP destination port: {self.rtp_dest_port}
"""
        return return_string

class ParameterCameraSettings(CameraSettings):
    # create CameraSettings object by using information from passed parameter file
    # utilizes service discovery to detect camera service port and camera ip-address
    # if assign_ip_address is True, an ip-address is assigned to camera before getting values from service discovery
    def __init__(self, parameter_file_path, assign_ip_address : bool = False):
        if assign_ip_address:

            dhcp_server_bind_address = [192,168,120,1]
            ip_address_to_assign = [192,168,120,10]
            dhcpserver = DHCPServer(67, dhcp_server_bind_address.packed,
                                    68, ip_address_to_assign,
                                    [51, 4, 0x00, 0x00, 0x00, 0x3C], # lease-time option (53) set to 20 seconds, should be enough to retrieve values from SD
                                    1024,
                                    renew_ip=True, # assign ip passed in this constructor and do not increment ip magically in dhcp-server
                                    wait_for_discovery=True)
            dhcpserver.server()

        self.parameter_file_path = parameter_file_path
        parameter_module = helperModule.read_file_as_python_module(parameter_file_path)
      
        some_ip_dest_ip_int = int.from_bytes(parameter_module.someIpSdDestinationIp, byteorder='big', signed=False)
        some_ip_dest_ip = ipaddress.ip_address(some_ip_dest_ip_int)

        sd = ServiceDiscovery(str(some_ip_dest_ip), parameter_module.someIpSdDestinationPort)
        sd.connect()
        sd_msg = sd.get_sd_message_noevent()
        if sd_msg is None:
            raise TimeoutError("""no service discovery message received to auto-detect settings.
Either camera is not running or the parameter file on which the auto-detection 
of settings is based on, is wrong. Check Config/DutSettings.py""")
        
        else:
            camera_ip_str = sd_msg.address()
            camera_ip = ipaddress.ip_address(camera_ip_str)
            camera_service_port = sd_msg.port()

        rtp_base_port = parameter_module.rtpDestinationPort

        camera_ip_as_list = list(camera_ip.packed)
        rtp_destination_port = rtp_base_port + camera_ip_as_list[3]

        super().__init__(camera_ip, # from service discovery
                         camera_service_port, # from service discovery
                         str(some_ip_dest_ip), # from parameter file
                         parameter_module.someIpSdDestinationPort, # from parameter file
                         rtp_destination_port) # from parameter file + last byte of camera-ip from service discovery
        
    def __str__(self) -> str:
        return_string = f"These are auto-detected settings based on the following parameter-file:\n {self.parameter_file_path}\n"
        return return_string + super().__str__()

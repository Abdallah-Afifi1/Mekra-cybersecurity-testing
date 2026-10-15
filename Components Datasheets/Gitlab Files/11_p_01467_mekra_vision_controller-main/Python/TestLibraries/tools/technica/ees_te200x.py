#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : ees_te200x.py
# Package : tools.technica
# Task    : Access to Technica TE-200x Enhanced Ethernet Switch Remote Control API
#
# See also:
#          * TE-200x Remote_API_for EES_v1.0.pdf
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 16.06.2025 | Tremmel   | initial
# 1.1.0  | 18.06.2025 | Tremmel   | added configuration methods
#******************************************************************************
"""
@package tools.technica.ees_te200x
Access to Technica TE-200x Enhanced Ethernet Switch Remote Control API.
"""
import json
import msgpack
import requests
import random

import re
from pprint import pprint

# from enum import IntEnum
# from collections import namedtuple

# from ttk_base.errors import TTkException
# from ttk_base._variables_base import VarBase

# #############################################################################
class TE200x:
    """ Configure Technica TE-200x Enhanced Ethernet Switchws via its
        Remote Control API
    """

    # "http://192.168.10.30/api/get/equipment.json"

    # #########################################################################
    def __init__(self, ip_addr):
        """ Parameters:
                ip_addr     -  IP address of ethernet switch
        """
        self.ip_addr = ip_addr = str(ip_addr).strip()
        print("#" * 80)
        self.getEquipmentInfo(verbosity=1)
        print("#" * 80)

       
    # #########################################################################
    def __str__(self):
        return (f"{self.__class__.__name__} @ {self.ip_addr}")

    # #########################################################################
    def getEquipmentInfo(self, verbosity=0):
        """ Get info on EES. 
            Parameters:
                verbosity - 0: silent
                            1: log overview info 
            Retruns a data dict, see json output for full structure
        """
        url_equipment  = f"http://{self.ip_addr}/api/get/equipment.json"
        resp = requests.get(url=url_equipment)
        equip = json.loads(resp.content)
        
        if verbosity >= 1:
            print(f"# Technica TE-{equip['versions']['hw']['product_id']} @ {self.ip_addr}")
            print(f"# Hardware: Release {equip['versions']['hw']['release']}")
            print(f"# System:   Release {equip['versions']['sys']['release']}")
            print(f"# App:      Release {equip['versions']['app']['release']}")
            print(f"# S/N {equip['license_info']['sn']}")
        return equip
        
    # #########################################################################
    def checkAlive(self, check_value=None, verbosity=0, timeout_s=1):
        """ Check if the device is able to accept HTTP requests. 
            An 8-digit number must be sent along with the alive command request. 
            The alive command will respond with the same number.
            
            Parameters:
                check_value - value to send to alive check
                              None: use a random value
                verbosity   - 0: silent
                              1: log status
                              2: log status with used check value
                              
                timeout_s   - connection/query timeout in [s] for device to respond.

            Note: timeout_s
                 About 1s should be sufficient if device is connected (more or 
                 less) directly. This will provide a more direct "is-not-alive"
                 result if the device does not respond. 
                 
                 Otherwise Requests documentation suggests timeout as multiples 
                 of 3s (due to default TCP packet retransmission delay).
            
            Returns True if the response contained the expected check_value, 
            or False if the response differs or the device did not respond
            before the timeout.
        """
        url_alive = f"http://{self.ip_addr}/api/cmd/alive"
        if check_value is None:
            check_value = random.randint(0, 99999999)
        check_value = min(99999999, abs(check_value)) # just in case
        check = f"{check_value:08d}"
        
        if verbosity >= 1:
            extra = f" (check: {check})" if verbosity >= 2 else ""
            print(f"# Checking if EES is alive{extra}...", end=" ")
        
        try:
            response = requests.post(url=url_alive, data=check, timeout=timeout_s) 
            alive = response.text == check 
            info = response.text
            
        except requests.Timeout:
            # i.e. ConnectTimeout, ReadTimeout
            alive = False
            info  = "<timeout>"
            
        if verbosity >= 1:
            print("...ok, alive" if alive else f"...dead ({info})", flush=True)
            
        return alive

    # #########################################################################
    def warmReset(self):
        """ Reset the EES to temporary configuration stored in RAM.
        
            Note: Warm Reset
                Saves the current configuration in a dedicated RAM area that 
                is retained after reboot and then restarts the device. 
                On boot, the configuration is taken from that RAM, processed, 
                and applied to into the device. The processed configuration 
                is not saved, so it’s faster than a cold reset but the 
                configuration is not persistent. 
        """
        reset_url = f"http://{self.ip_addr}/api/cmd/reset_warm"
        response = requests.post(url=reset_url) 
        print(f"# warm reset: {response.text}") 
        response.raise_for_status()
        
        
    # #########################################################################
    def coldReset(self):
        """ Reset the EES to configuration stored in NVM.
            A (cold) reset is necessary for new configurations to be activated.
            
            Note: Cold Reset
                Discards the current configuration stored in RAM and restarts 
                the device. At boot time, the configuration is taken from the 
                NVM. 
                If the configuration was modified before this request, the boot 
                process may take some time to process the new configuration and 
                save it in a special area to avoid this process on subsequent 
                reboots if there are no changes to the configuration.  

        """
        reset_url = f"http://{self.ip_addr}/api/cmd/reset_cold"
        response = requests.post(url=reset_url) 
        print(f"# cold reset: {response.text}") 
        response.raise_for_status()


    # #########################################################################
    def setPTP(self, ptp_data):
        """ Precision Time Protocol reconfiguration, reset the initial time of 
            PTP grandmaster partitions.
            
            Parameters:
                ptp_data - a list of dicts with ptp data, follows the json data 
                           structure, see Note
            
            Note: ptp_data
                See 2.2.4.3  PTP reconfiguration 
                
                The (msgpack) data to send embedded in the POST request shall 
                have the following format:
                [ 
                  {"partition": 0, "init_time": 1716894119, "init_time_ns": 500000000 }, 
                  {"partition": 3, "init_time": 1716894119, "init_time_ns": 0 }
                ] 
                * All numbers shall be coded in decimal base. 
                * Partitions not set in the remote command are not modified. 

        """
        url = f"http://{self.ip_addr}/api/ptp/origin_timestamp.msgpack"
        assert isinstance(ptp_data, (list, tuple))
        # print(json.dumps(ptp_data))
        msgpack_data = msgpack.packb(ptp_data)
        
        response = requests.post(url=url, data=msgpack_data) 
        print(f"# setPTP: {response.text}") 
        response.raise_for_status()

    # #########################################################################
    def getMKAKey(self, pos=0):
        """ Retrieve the MKA key stored in the given position 
            Parameters:
                pos - position of MKA key
                
            Note: Data format
               See 2.2.4.4  MKA keys 
               The (msgpack) data to send embedded in the POST request shall 
               have the following format:
               { 
                  "label": "100", 
                  "cak":   [ 16, 32, 48, 64, 16, 32, 48, 64, 16, 32, 48, 64, 16, 32, 48, 64 ], 
                  "ckn":   [ 24, 132, 250, 45, 201 ], 
                  "ports": [ 0, 1 ] 
               } 
               * `cak` field must be an array of 16 or 32 bytes. 
               * `ports` field code to which ports this key is assigned. 
               
            Returns a data dict or None if now MKA key was available for `pos`
        """
        get_key_url = f"http://{self.ip_addr}/api/mka/{pos}/get_key.msgpack"
        try:
            # normally, this would be sufficient:
            # response = requests.get(url=get_key_url) 
            
            # ... but undefined MKA-positions cause the response to contain 
            # fewer bytes than announced (see below for more details)
            
            with requests.get(url=get_key_url, stream=True) as response:
                # stream=True first downloads the header and defers downloading 
                # of the response body until response.content is accessed
                if response.status_code == 200:
                    # valid response (200 OK) 
                    data = msgpack.unpackb(response.content)
                else:
                    # non-ok response, content may contain only partial data
                    # (in this specific case, normally the declared Content-Length
                    # should match regardless of response status)
                    data = None
                    print(f"[getMKAKey] {response.status_code = }")
                    # accessing the raw response will side-step Content-Length
                    # checks and thus ChunkedEncodingError 
                    content = response.raw.read(1024).decode("latin-1", errors="ignore")
                    content = re.sub(r"<[^>]*>", "", content.strip()) # q&d de-htmlify
                    print(f"[getMKAKey] {content}")
                
        except requests.exceptions.ChunkedEncodingError as ex:
            # error handler kept just-in-case
            # 
            # Looks like EES sends fewer bytes than announced (in GET requests) 
            # if MKA key is not available at the given `pos`
            # => * "Status" 400 (Bad Request),
            #    * error response content "400: The requested data could not be gathered."
            #    * but "Content-Length" header is 85 and only 83 bytes were sent
            #      (b'<html><body><h2>400: The requested data could not be gathered.</h2></body></html>\r\n')
            #
            # Amusingly, using POST as alternative works neither but in a 
            # slightly weird way:
            #    * get_key is not available as POST request (only with GET)
            #    * POST with get_key results in:
            #        * "Status" 200 (OK) (no, really)
            #        * content "ERROR: Invalid URL!"
            print(f"> getMKAKey({pos=}): {type(ex).__name__}: {ex}")
            data = None

        # pprint(data)
        return data
        
    # #########################################################################
    def setMKAKey(self, data, pos=0):
        """ Retrieve the MKA key stored in the given position 
            Parameters:
                data - dict with MKA key data, see Note at getMKAKey
                pos  - position of MKA key
            Returns the data dict
        """
        set_key_url = f"http://{self.ip_addr}/api/mka/{pos}/set_key.msgpack"
        assert isinstance(data, dict)
        assert set(data.keys()) == {"label", "cak", "ckn", "ports"}
        
        pprint(json.dumps(data))

        msgpack_data = msgpack.packb(data)
        response = requests.post(url=set_key_url, data=msgpack_data) 
        print(f"[set_key] {response.text}") 
        response.raise_for_status()
        return data
               
    # #########################################################################
    def getStatus(self):
        """ Retrieve full status information
            Returns a data dict (see json data for full structure)
        """
        status_url = f"http://{self.ip_addr}/api/get/status.msgpack"
        response = requests.get(url=status_url) 
        response.raise_for_status()
        data = msgpack.unpackb(response.content)
        return data
    
    # #########################################################################
    def getPortStatus(self, port=0, verbosity=0):
        """ Get (link) status information for a specific port
            Parameters:
                port - main port number (0..7)
             Returns a data dict (see json data for full structure)
        """
        # sub-paths are only available for JSON view
        # Note: just retrieving port status as JSON is still about 1/7 of the 
        #       size of full status as msgpack 
        status_url = f"http://{self.ip_addr}/api/get/status.json/ports/main/{int(port)}"
        response = requests.get(url=status_url) 
        response.raise_for_status()
        data = json.loads(response.content)
        
        if verbosity >= 2:
            print(f"# Port {port}: ")
            pprint(data, width=120)
            
        elif verbosity >= 1:
            print(f"# Port {port}: ")
            print(f"  linkup    {data['linkup']}")
            print(f"  dropcount {data['statistics']['link']['dropcount']}")
            print(f"  uptime    {data['statistics']['link']['uptime']}")
            print(f"  time      {data['statistics']['time']}")
            
        return data
    
    
    # #########################################################################
    def getConfig(self, default=False):
        """ Get complete configuration.
            Parameters:
                default - False: return current configuration
                          True:  return default configuration
                          
            Note: Data structure
                See JSON output for detailed structure:
                * current: /api/get/config.json 
                * default: /api/get/default_config.json 
            
            Returns a data dictionary 
        """
        cmd = "default_config" if default else "config"
        config_url = f"http://{self.ip_addr}/api/get/{cmd}.msgpack"
        response = requests.get(url=config_url) 
        response.raise_for_status()
        data = msgpack.unpackb(response.content)
        return data
    
    # #########################################################################
    def validateConfig(self, config_data):
        """ Validate an EES configuration
            * Checks if all fields are within the limits. 
              If any field is out of its limits the configuration is rejected.  
            * Any missing fields are added and filled with their default value. 
            * Any field not defined in the EES configuration is discarded.  

            Parameters:
                config_data - configuration data dict
                
            Returns a corrected config_data if possible or 
            None if config was invalid. 
            May raise an error if validation response was not OK.
        """
        val_url = f"http://{self.ip_addr}/api/validate/config.msgpack"
        msgpack_data = msgpack.packb(config_data)
        response = requests.post(url=val_url, data=msgpack_data) 
        response.raise_for_status()
        
        # special-case handling for rather nonstandard "OK, but actually ERROR"
        # behavior:
        if response.status_code == 200 and response.content.startswith(b"ERROR:"):
            print(f"[validateConfig]: {response.text.strip()}")
            updated_data = None
        else:
            updated_data = msgpack.unpackb(response.content)
        return updated_data
    
    # #########################################################################
    def writeConfig(self, config_data, allow_partial=False, persistent=False):
        """ Write EES configuration data
            Parameters:
                config_data   - a config data dictionary
                allow_partial - True: only write data in supplied fields
                                False: require all fields to be present
                persistent    - True: write data to NVM/non-volatile memory.
                                      Requires a coldReset() for config to become active.
                                False: write data to RAM
                                      Requires a warmReset() for config to become active.
            
            Note: config_data
                 allow_partial=False:
                     data must fully comply with the structure used to define 
                     the EES configuration (no missing fields, no extra fields)
                 allow_partial=True:
                     data may contain a subset of the EES configuration,
                     parameters not present in sent data are not modified
                
            Returns True on successful configuration, otherwise False
            May raise an error if configuration response was not OK.
        """
        mode = "partial" if allow_partial else "strict"
        persistence = "persistent" if persistent else "non_persistent"
        set_url = f"http://{self.ip_addr}/api/set/{mode}/config_{persistence}.msgpack"
        
        msgpack_data = msgpack.packb(config_data)
        response = requests.post(url=set_url, data=msgpack_data) 
        # print(f"{response.status_code = }, {response.content = }")
        response.raise_for_status()
        
        # sadly, ERRORs are also status 200 OK, content contains an error message 
        success = (response.status_code == 200 and not response.content.startswith(b"ERROR:"))

        print(f"[writeConfig] {response.text.strip()}")
        return success

        
# #############################################################################
if __name__ == "__main__":
   
   
    ees = TE200x(ip_addr="192.168.10.30")
    
    print(ees)
    print(f"{ees.checkAlive() = }")
    
          
    ees.setPTP(ptp_data = [])

    print("-- setMKAKey -----------------------------------------------------")
    # Note: setting an MKA key only works if MACSec is enabled on EES
    # (setting will still report "OK" if MACSec functionality is disabled, 
    #  but the key will not be set and cannot be retrieved with getMKAKey)
    ees.setMKAKey(pos=0, data={ 
      "label": "100", 
      "cak":   [ 16, 32, 48, 64, 16, 32, 48, 64, 16, 32, 48, 64, 16, 32, 48, 64 ], 
      "ckn":   [ 24, 132, 250, 45, 201 ], 
      "ports": [ 0, 1 ] 
    })

    print("-- getMKAKey(pos=0) ----------------------------------------------")
    pprint(ees.getMKAKey(pos=0))

    print("-- getMKAKey(pos=1) ----------------------------------------------")
    pprint(ees.getMKAKey(pos=1))


    # print(f"{ees.checkAlive() = }")
    # print("-- warmReset ------------------------------------------------------")
    # ees.warmReset()
    # start_time = time.time()
    # while time.time() - start_time < 10.0:
    #     if ees.checkAlive(verbosity=2):
    #         break
    #     time.sleep(.100)
    
    # print(f"{ees.checkAlive() = }")
    # print("-- coldReset ------------------------------------------------------")
    # ees.coldReset()
    # start_time = time.time()
    # while time.time() - start_time < 10.0:
    #     if ees.checkAlive(verbosity=2):
    #         break
    #     time.sleep(.100)


    #pprint(ees.getStatus(), width=120)
    ees.getStatus()
    ees.getPortStatus(port=0, verbosity=1)
    
    print("-- getConfig -----------------------------------------------------")
    cfg = ees.getConfig()
    pprint(cfg, width=400)
    print(cfg.keys())

    print("-- getConfig(default=True) ---------------------------------------")
    cfg_default = ees.getConfig(default=True)
    #pprint(cfg, width=400)
    print(cfg.keys())


    print("-- validateConfig ------------------------------------------------")
    cfg2 = ees.validateConfig(cfg)
    print("PASSED" if cfg == cfg2 else "FAILED")
    assert cfg == cfg2
    
    print("-" * 120)
    print("# empty dict as config")
    cfg3 = ees.validateConfig({})
    
    print("-" * 120)
    print("# only advanced_filter section")
    cfg4 = ees.validateConfig({'advanced_filter': {'enable': False, 'rules': []},})

    print("-" * 120)
    print("# current config w/o power section")
    cfg_current = ees.getConfig()
    cfg5 = cfg_current.copy() # shallow
    del(cfg5['power'])
    cfg5 = ees.validateConfig(cfg5)
    print("PASSED" if cfg5 == cfg_current else "FAILED")
    
    print()
    print("-- writeConfig ------------------------------------------------")
    print("# current config w/o power section, disallow partial config")
    cfg5 = cfg_current.copy() # shallow
    del(cfg5['power'])
    # this should fail
    assert not ees.writeConfig(cfg5, persistent=False, allow_partial=False)

    print("-" * 120)
    print("# current config w/o power section, allow partial config")
    assert ees.writeConfig(cfg5, persistent=False, allow_partial=True)
    
    print("-" * 120)
    print("# current config, disallow partiol, make persistent")
    cfg_current = ees.getConfig()
    assert ees.writeConfig(cfg_current, persistent=True, allow_partial=False)
    
     
    
     
    
    print("Done.")
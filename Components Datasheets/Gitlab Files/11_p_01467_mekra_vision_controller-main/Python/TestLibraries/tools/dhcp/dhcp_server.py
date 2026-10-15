#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : dhcp_server.py
# Package : tools.dhcp
# Task    : dhcp server.
#
#
#   See also:
#              -Project MCP and MCP MoPf
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 02.07.2025 | Völler J. | initial 
# 1.1.0  | 03.08.2026 | EHu Li    | added serve_one_lease()
#******************************************************************************
#
#Imports:
import socket
import binascii
import select
import threading 


class DHCPServer(object):

    def __init__(self, a_server_port, siaddr, a_client_port, yiaddr, ip_timeout, a_max_bytes, renew_ip=False,
                 wait_for_discovery=False, exit_counter=3, dhcp_client_ip="any"):
        self.MAX_BYTES = a_max_bytes
        self.serverPort = a_server_port
        self.yiaddr = yiaddr
        self.clientPort = a_client_port
        self.dhcp_client_ip = dhcp_client_ip
        self.siaddr = siaddr
        self.ip_timeout = ip_timeout
        self.renew_ip = renew_ip  # if true, DHCP server assigns the current ip again, otherwise increments ip address
        self.wait_for_discovery = wait_for_discovery  # if true, DHCP server waits for DHCP Discover message,
        # otherwise for DHCP Request
        self.runDHCP = True
        self.ip_overflow_cntr = 0  # counts, how often the ip address range has been assigned to the client
        self.exit_counter = exit_counter
        self.ack_sent = False
        self.actual_ip = [0x00, 0x00, 0x00, 0x00]
        self.ip_str = (str(self.siaddr[0]) + "." + str(self.siaddr[1]) + "." +
                       str(self.siaddr[2]) + "." + str(self.siaddr[3]))

    def server(self):
        print("DHCP server is starting...")

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.s.bind((self.ip_str, self.serverPort))
        
        #self.s.bind(('', self.serverPort))

        dest = ('255.255.255.255', self.clientPort)
        #dest = ('255.255.255.255', 67)
        #dest = ('239.120.1.1', 30490)
        #dest = ('', self.clientPort)
        timeout_cnt = 0

        if self.wait_for_discovery:  # Waiting for a DHCP Discover packet
            while self.runDHCP:
                try:
                    l_readable, l_writable, l_exceptional = select.select([self.s], [], [], 0.3)

                    if self.s in l_readable:
                        data, address = self.s.recvfrom(self.MAX_BYTES)
                        l_decoded_data = (binascii.hexlify(data)).decode('utf-8')
                        l_transaction_id = [int(l_decoded_data[n:n + 2], 16) for n in range(8, 15, 2)]
                        client_mac_addr = [int(l_decoded_data[n:n + 2], 16) for n in range(56, 68, 2)]
                        l_padding_index = l_decoded_data.rfind("f") + 1
                        l_padding = len(l_decoded_data[l_padding_index:len(l_decoded_data)]) // 2

                        if self.dhcp_client_ip == "any" or address[0] == self.dhcp_client_ip:
                            if str(l_decoded_data[480:486]) != "350101":  # received data is not of type DHCP Discover
                                print("Waiting for DHCP Discover.")
                                continue

                            else:
                                print("DHCP Discover received.")

                                # increment / reset IP address
                                if not self.renew_ip:
                                    self.inc_ip_address()

                                print("Sending DHCP Offer.")
                                data = self.offer_get(l_transaction_id, l_padding, client_mac_addr, self.yiaddr,
                                                      self.siaddr, self.ip_timeout)
                                self.s.sendto(data, dest)

                                while self.runDHCP:
                                    try:
                                        print("Waiting for DHCP Request after Offer.")

                                        l_readable, l_writable, l_exceptional = select.select([self.s], [], [], 0.5)
                                        print("l_readable: ", l_readable)

                                        if self.s in l_readable:
                                            data, address = self.s.recvfrom(self.MAX_BYTES)
                                            l_decoded_data = (binascii.hexlify(data)).decode('utf-8')
                                            l_transaction_id = [int(l_decoded_data[n:n + 2], 16) for n in range(8, 15, 2)]
                                            client_mac_addr = [int(l_decoded_data[n:n + 2], 16) for n in range(56, 68, 2)]
                                            l_padding_index = l_decoded_data.rfind("f") + 1
                                            l_padding = len(l_decoded_data[l_padding_index:len(l_decoded_data)]) // 2

                                            if str(l_decoded_data[480:486]) != "350103":  # received data is not a Request
                                                print("No DHCP Request received. Restarting...")
                                                timeout_cnt += 1
                                                if timeout_cnt >= self.exit_counter:
                                                    self.stop_dhcp()
                                                else:
                                                    continue

                                            else:
                                                print("DHCP Request received. Sending DHCP Acknowledge.")
                                                data = self.pack_get(l_transaction_id, l_padding, client_mac_addr,
                                                                     self.yiaddr, self.siaddr, self.ip_timeout)
                                                self.s.sendto(data, dest)
                                                self.ack_sent = True
                                                self.actual_ip = self.yiaddr
                                                print("ACK client IP: " + str(self.yiaddr) + " cycles: " +
                                                      str(self.ip_overflow_cntr))
                                                self.stop_dhcp()
                                                # break
                                    except():
                                        self.stop_dhcp()
                except():
                    self.stop_dhcp()
        else:
            print("Waiting for DHCP Request...")
            while self.runDHCP:
                try:
                    l_readable, l_writable, l_exceptional = select.select([self.s], [], [], 0.3)
                    print("l_readable: ", l_readable)

                    if self.s in l_readable:
                        data, address = self.s.recvfrom(self.MAX_BYTES)
                        l_decoded_data = (binascii.hexlify(data)).decode('utf-8')
                        l_transaction_id = [int(l_decoded_data[n:n + 2], 16) for n in range(8, 15, 2)]
                        client_mac_addr = [int(l_decoded_data[n:n + 2], 16) for n in range(56, 68, 2)]
                        l_padding_index = l_decoded_data.rfind("f") + 1
                        l_padding = len(l_decoded_data[l_padding_index:len(l_decoded_data)]) // 2

                        if str(l_decoded_data[480:486]) != "350103":  # received data is not a Request
                            print("Waiting for DHCP Request. None received, restarting...")
                            timeout_cnt += 1
                            if timeout_cnt >= self.exit_counter:
                                self.stop_dhcp()
                            else:
                                continue
                        else:
                            print("DHCP Request received.")

                            # increment / reset IP address
                            if not self.renew_ip:
                                self.inc_ip_address()

                            print("Sending DHCP Acknowledge.")
                            data = self.pack_get(l_transaction_id, l_padding, client_mac_addr, self.yiaddr,
                                                 self.siaddr, self.ip_timeout)
                            self.s.sendto(data, dest)

                            print("ACK client IP: " + str(self.yiaddr) + " cycles: " +
                                  str(self.ip_overflow_cntr))
                            self.ack_sent = True
                            self.actual_ip = self.yiaddr
                            self.stop_dhcp()
                except():
                    self.stop_dhcp()
                    
    def serve_one_lease(self, timeout_s=60):
        """Serve one lease with a timeout and release the port again.

        server() loops until a Discover arrives and never returns if the client
        does not ask for an address, so it runs in a thread here and is stopped
        through runDHCP.

        Returns True when an Acknowledge was sent.
        """
        worker = threading.Thread(target=self.server, daemon=True)
        worker.start()
        worker.join(timeout_s)

        if worker.is_alive():
            self.stop_dhcp()
            worker.join(5)

        if hasattr(self, "s"):
            self.s.close()

        return self.ack_sent
    def stop_dhcp(self):
        self.runDHCP = False
        return
    
    

    @staticmethod
    def offer_get(a_transaction_id, a_padding, param_client_mac_address, param_yiaddr, param_siaddr, param_ip_timeout):

        OP = bytes([0x02])
        HTYPE = bytes([0x01])
        HLEN = bytes([0x06])
        HOPS = bytes([0x00])
        # XID = bytes([0x39, 0x03, 0xF3, 0x26])
        XID = bytes(a_transaction_id)
        SECS = bytes([0x00, 0x00])
        FLAGS = bytes([0x80, 0x00])
        CIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        YIADDR = bytes(param_yiaddr)  # [0xC0, 0xA8, 0x78, 0x07] == 192.168.120.7
        SIADDR = bytes(param_siaddr)  # [0xC0, 0xA8, 0x78, 0x42] == 192.168.120.1
        GIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR1 = bytes([param_client_mac_address[0], param_client_mac_address[1], param_client_mac_address[2],
                         param_client_mac_address[3]])
        CHADDR2 = bytes([param_client_mac_address[4], param_client_mac_address[5], 0x00, 0x00])
        CHADDR3 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR4 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR5 = bytes(192)
        Magiccookie = bytes([0x63, 0x82, 0x53, 0x63])  # Magic cookie
        DHCPOptions1 = bytes([53, 1, 2])  # DHCP Offer
        DHCPOptions2 = bytes([1, 4, 0xFF, 0xFF, 0xFF, 0x00])  # 255.255.255.0 subnet mask
        DHCPOptions3 = bytes([3, 4, 0x00, 0x00, 0x00, 0x00])  # 192.168.1.1 router
        DHCPOptions4 = bytes(param_ip_timeout)  # [51, 4, 0x00, 0x00, 0x00, 0x3C] == 1min IP address lease time
        DHCPOptions5 = bytes([54, 4, param_siaddr[0], param_siaddr[1], param_siaddr[2], param_siaddr[3]])  # DHCP server
        DHCPOptions6 = bytes([46, 1, 8])
        END_OPTION = bytes([255])  # Marking end of dhcp packet
        PADDING = bytes(a_padding)  # Padding after end option

        package = (OP + HTYPE + HLEN + HOPS + XID + SECS + FLAGS + CIADDR + YIADDR + SIADDR + GIADDR + CHADDR1 +
                   CHADDR2 + CHADDR3 + CHADDR4 + CHADDR5 + Magiccookie + DHCPOptions1 + DHCPOptions2 +
                   DHCPOptions4 + DHCPOptions5 + DHCPOptions6 + END_OPTION + PADDING)

        return package

    @staticmethod
    def pack_get(a_transaction_id, a_padding, param_client_mac_address, param_yiaddr, param_siaddr, param_ip_timeout):
        OP = bytes([0x02])
        HTYPE = bytes([0x01])
        HLEN = bytes([0x06])
        HOPS = bytes([0x00])
        # XID = bytes([0x39, 0x03, 0xF3, 0x26])
        XID = bytes(a_transaction_id)
        SECS = bytes([0x00, 0x00])
        FLAGS = bytes([0x80, 0x00])
        CIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        YIADDR = bytes(param_yiaddr)  # [0xC0, 0xA8, 0x78, 0x07] == 192.168.120.7
        SIADDR = bytes(param_siaddr)  # [0xC0, 0xA8, 0x78, 0x42] == 192.168.120.1
        GIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR1 = bytes([param_client_mac_address[0], param_client_mac_address[1], param_client_mac_address[2],
                         param_client_mac_address[3]])
        CHADDR2 = bytes([param_client_mac_address[4], param_client_mac_address[5], 0x00, 0x00])
        CHADDR3 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR4 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR5 = bytes(192)
        Magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
        DHCPOptions1 = bytes([53, 1, 5])  # DHCP ACK(value = 5)
        DHCPOptions2 = bytes([1, 4, 0xFF, 0xFF, 0xFF, 0x00])  # 255.255.255.0 subnet mask
        DHCPOptions3 = bytes([3, 4, 0x00, 0x00, 0x00, 0x00])  # 192.168.1.1 router
        DHCPOptions4 = bytes(param_ip_timeout)  # [51, 4, 0x00, 0x00, 0x00, 0x3C] == 1min IP address lease time
        DHCPOptions5 = bytes([54, 4, param_siaddr[0], param_siaddr[1], param_siaddr[2], param_siaddr[3]])  # DHCP server
        DHCPOptions6 = bytes([46, 1, 8])
        END_OPTION = bytes([255])
        PADDING = bytes(a_padding)  # Padding after end option

        package = (OP + HTYPE + HLEN + HOPS + XID + SECS + FLAGS + CIADDR + YIADDR + SIADDR + GIADDR + CHADDR1 +
                   CHADDR2 + CHADDR3 + CHADDR4 + CHADDR5 + Magiccookie + DHCPOptions1 + DHCPOptions2 +
                   DHCPOptions4 + DHCPOptions5 + DHCPOptions6 + END_OPTION + PADDING)

        return package

    def inc_ip_address(self):
        if self.yiaddr[-1] == 254:  # reset IP to 2 if maximum is reached
            self.yiaddr[-1] = 2
            self.ip_overflow_cntr += 1
        # these exceptional IP-addresses are used by the test environment, see TestEnvironmentSettings
        elif (self.yiaddr[-1] + 1 == self.siaddr[-1] or self.yiaddr[-1] + 1 == 66 or self.yiaddr[-1] + 1 == 110 or
              self.yiaddr[-1] + 1 == 120 or self.yiaddr[-1] + 1 == 8 or self.yiaddr[-1] + 1 == 1):
            # jump over server's ip address
            self.yiaddr[-1] += 2
        else:  # increment IP address
            self.yiaddr[-1] += 1

#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : dhcp_thread.py
# Package : tools.dhcp
# Task    : dhcp server as a thread.
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
#******************************************************************************
#
#Imports:
from threading import Thread
from dhcp_server import DHCPServer


class DhcpServerThread(Thread):

    def __init__(self, a_server_port, siaddr, a_client_port, yiaddr, ip_timeout, a_max_bytes, renew_ip=False,
                 wait_for_discovery=False):
        Thread.__init__(self)
        self.dhcpServer = DHCPServer(a_server_port, siaddr, a_client_port, yiaddr, ip_timeout, a_max_bytes, renew_ip,
                                     wait_for_discovery)

    def run(self):
        self.dhcpServer.server()

    def exit_dhcp(self):
        self.dhcpServer.stop_dhcp()





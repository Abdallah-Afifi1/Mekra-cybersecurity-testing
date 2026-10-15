#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : _simserv_vt4007.py
# Package : tools.voetsch
# Task    : Basis Mock-server simulating a Vötsch VT4007 climatic test chamber
#           via TPC / "S!MPAC 1.x"/simserv protocol
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 12.06.2025 | Tremmel   | initial
# 1.1.0  | 16.06.2025 | Tremmel   | moved commend handling to _sim7004
#******************************************************************************
"""
@package tools.voetsch._simserv_vt4007
Basis Mock-server simulating a Vötsch VT4007 climatic test chamber
via TPC / "S!MPAC 1.x"/simserv protocol
"""
import sys
import socketserver
sys.path.insert(0, ".") # for convenience on command line

# Note:
#    Basic SimServTCPHandler will close the connection after each request,
#    so client has to re-open the connection each time.
#    This fits the documented Simpac behavior:
#
#    "It is not possible to open a permanent connection to the server. 
#     Therefore a server can operate with a lot of clients.
#
#     For each command the following terminate is to be used: 
#       1.  Open connection 
#       2.  Send command 
#       3.  Read response 
#       4.  Close connection"
#
#    However, it seems "real" climatic chambers might support communication 
#    using a single kept-alive connection


from tools.voetsch._sim7004 import handleSimpacCommand
     
# adapted from https://docs.python.org/3/library/socketserver.html#examples
class SimServTCPHandler(socketserver.BaseRequestHandler):
    """ Request handler class for our server.
        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        pieces = [b'']
        total = 0
        while b'\r' not in pieces[-1] and b'\n' not in pieces[-1] and total < 10000:
            chunk = self.request.recv(2000)
            pieces.append(chunk)
            total += len(chunk)
        
        self.data = b''.join(pieces)

        print("―" * 96)
        data = self.data.decode("latin-1")
        print(f"Received from {self.client_address[0]}:")
        print(f"► {data!r}")
        
        response = handleSimpacCommand(data)

        # just send back the same data, but upper-cased
        print(f"◄ {response!r}")
        self.request.sendall(response.encode("latin-1"))
        # after we return, the socket will be closed.

        
# #############################################################################
if __name__ == "__main__":

    try:
        from ansi_console import Highlighter, HL, DEFAULT_LINEMARKERS #, ANSI_AVAILABLE
        linemarkers = DEFAULT_LINEMARKERS.copy()
        linemarkers["► "] = HL.cyan
        linemarkers["◄ "] = HL.cyan
        linemarkers["――"] = HL.blue
        
        highlighter = Highlighter(
            linemarkers = linemarkers,
            keywords={
                "[command]": HL.igreen, 
                "[chamber]": HL.igreen, 
                "[args]":    HL.igreen, 
                "[data]":    HL.iyellow, 
        })
        # if ANSI_AVAILABLE:
        #     # clear console (move cursor to 0/0, clear buffer after cursor)
        #     print("\033[H\033[3J", end="")
        #     print("hm.")
        # => cursor positioning seems to work on w32, but not clearing the buffer
    except ImportError:
        print("Highlighter n/a")
    

    import os 
    os.system('cls') # quick&dirty

    print("== Mock-SimServ: VT7004 ==========================================")
    host, port = "localhost", 2049

    try:
        # Create the server, binding to localhost on port 9999
        with socketserver.TCPServer((host, port), SimServTCPHandler) as server:
        #with socketserver.TCPServer((host, port), SimServStreamHandler) as server:
            
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
            
    except KeyboardInterrupt:
        print("shutting down...")
        
    print("Done.")
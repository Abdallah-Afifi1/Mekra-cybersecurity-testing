#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : _simserv_vt4007_selector.py
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
# 1.0.0  | 16.06.2025 | Tremmel   | server variant using selectors
# 1.1.0  | 16.06.2025 | Tremmel   | moved commend handling to _sim7004
#******************************************************************************
"""
@package tools.voetsch._simserv_vt4007
Basis Mock-server simulating a Vötsch VT4007 climatic test chamber
via TPC / "S!MPAC 1.x"/simserv protocol
"""
import sys
import socket
import selectors

sys.path.insert(0, ".") # for convenience on command line

from tools.voetsch._sim7004 import handleSimpacCommand
     
     
sel = selectors.DefaultSelector()
# c.f. https://docs.python.org/3/library/selectors.html

def accept(sock, mask):  # @UnusedVariable: mask
    conn, addr = sock.accept()  # should be ready
    print(f"# accepted {conn} from {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask): # @UnusedVariable: mask
    data = conn.recv(2048)  # should be ready
    if data:
        print("―" * 96)
        data = data.decode("latin-1")
        print(f"Received from {conn}:")
        print(f"► {data!r}")
        
        response = handleSimpacCommand(data)
        
        print(f"◄ {response!r}")
        conn.sendall(response.encode("latin-1"))
        
    else:
        print('# closing', conn)
        sel.unregister(conn)
        conn.close()

        
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
        sock = socket.socket()
        sock.bind((host, port))
        sock.listen(100) # backlog=100
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ, accept)
        
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


    except KeyboardInterrupt:
        print("shutting down...")
        
    print("Done.")
#******************************************************************************
# -*- coding: utf-8 -*-
# File    : .py
# Task    : *insert test script objective here*
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver. | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0  | 22.04.2025 | JoTremmel | initial  
#******************************************************************************
# from _automation_wrapper_ import TestEnv
# import sys
import pyvisa


# print(sys.version)

rm = pyvisa.ResourceManager()

# https://pyvisa.readthedocs.io/en/latest/introduction/communication.html
# Once that you have a ResourceManager, you can list the available resources 
# using the list_resources method. The output is a tuple listing the VISA 
# resource names. You can use a dedicated regular expression syntax to filter 
# the instruments discovered by this method. The syntax is described in 
# details in list_resources(). 
# The default value is ‘?*::INSTR’ which means that by default only instrument
# whose resource name ends with ‘::INSTR’ are listed (in particular USB RAW 
# resources and TCPIP SOCKET resources are not listed). 
# To list all resources present, pass ‘?*’ to list_resources.

# Note: Our FLUKE 8845A can be added manually as a TCPIP SOCKET connection 
# (and will only be listed with rm.list_resources("?*")), but VISA support 
# is a bit hit-and-miss

print(rm)
print()

for res in rm.list_resources():
    print(f"-- {res} --{'-' * (80 - 6 - len(res))}")
    # inst = rm.open_resource('GPIB0::12::INSTR')
    try:
        if res.startswith("ASRL"):
            print("# skipped serial connection (gets added by default for each COM port)")
            continue
        with rm.open_resource(res) as inst: 
            print(inst.query("*IDN?"))
    except Exception as ex:
        print(f"> {type(ex).__name__}: {ex}")
print("Done.")

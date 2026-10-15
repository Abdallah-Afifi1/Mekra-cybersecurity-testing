#******************************************************************************
# -*- coding: utf-8 -*-
# File: DUT_Settings.py
# Task: Selection the expected values for the connected DUT
# 
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 24.02.2026 | Völler J.  | initial  
#******************************************************************************
import pathlib
from dut_config_loader import read_production_data, read_sw_config, to_dict

class DUTSettings:
    pythonProductionDataFile = pathlib.Path(
        "Python/TestLibraries/reference_value/production_data/Volvo_Standard_1Gbit_SN00012315.py"
    )

class PARSettings:
    pythonSwConfigFile = pathlib.Path(
        "Python/TestLibraries/reference_value/SW_config/PAR_10C0.py"
    )

if __name__ == "__main__":
    dut_file = str(DUTSettings.pythonProductionDataFile)
    par_file = str(PARSettings.pythonSwConfigFile)

    prod = read_production_data(dut_file)
    sw   = read_sw_config(par_file)

    print("=== Production Data ===")
    print(to_dict(prod))
    print("=== SW Config ===")
    print(to_dict(sw))
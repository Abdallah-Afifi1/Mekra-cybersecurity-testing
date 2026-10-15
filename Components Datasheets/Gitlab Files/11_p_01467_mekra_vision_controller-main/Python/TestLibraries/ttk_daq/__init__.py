#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : __init__.py
# Package : ttk_daq
# Task    : Package ttk_daq - data acquisition/signal/measurement evaluation \
#           utilities
# Python  : 3.6+
#
# Copyright 2015 - 2020 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev. | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0  | 03.02.2015 | J.Tremmel | initial package (restructured from original daq_utils.py)
# 1.1  | 18.12.2015 | J.Tremmel | 1.0.0 => release
# 1.2  | 25.01.2016 | L.Morgus  | wrapper for _init_
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2.0  | 22.06.2020 | J.Tremmel | migrated to Python 3
#******************************************************************************
"""
@package ttk_daq
Utilities for data acquisition/signal/measurement evaluation
"""
from ttk_daq._init_ import version      # @UnresolvedImport (compiled extension)
from ttk_daq._init_ import version_info # @UnresolvedImport
 
# #############################################################################
if __name__ == "__main__":
    print(f"# Package ttk_daq, version {version}")
    

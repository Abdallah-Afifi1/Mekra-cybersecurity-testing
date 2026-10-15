#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : __init__.py
# Package : ttk_selftest
# Task    : Package ttk_selftest - test functions for HIL system self test.
# Copyright 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 05.04.2018 | C. Haas   | initial
# 2.0.0  | 09.01.2024 | M. Jellen | Python3 update
#******************************************************************************
"""
@package ttk_selftest
Test functions for HIL system self test and abstraction layer for "HIL devices".
"""
from ttk_selftest._init_ import version      # @UnresolvedImport (compiled extension)
from ttk_selftest._init_ import version_info # @UnresolvedImport

# #############################################################################
if __name__ == "__main__":
    print(f"# Package ttk_selftest, version {version}")

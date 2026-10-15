#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : ttk_version.py
# Task    : Version information for TestToolkit releases (i.e. which packages
#           are included in this release)
#
# Author  : J.Tremmel
# Date    : 01.10.2012
# Copyright 2012 - 2020 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev. | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0  | 01.10.2012 | J.Tremmel | initial
# 1.1  | 11.02.2013 | J.Tremmel | functionality moved to ttk_base
# 1.2  | 05.06.2020 | J.Tremmel | migrated to Python 3
#******************************************************************************
""" 
Version information for TestTooklkit releases 
"""
# #############################################################################
if __name__ == "__main__":
    import ttk_base
    ttk_base.showReleaseInfo()

#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : __init__.py
# Package : ttk_base
# Task    : Package ttk_base - common functions, base definitions and 
#           abstraction layer for calibrations / real time variables
# Python  : 3
#
# Copyright 2011 - 2022 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Rev. | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0  | 13.10.2011 | J.Tremmel | initial
# 1.1  | 08.12.2011 | J.Tremmel | added package version info
# 1.2  | 02.01.2012 | J.Tremmel | set version: beta release
# 1.3  | 30.07.2012 | J.Tremmml | => 1.1.0 - updates, added values_base
# 1.4  | 01.10.2012 | J.Tremmml | => 1.2.0 - updates, added Snapshot
# 1.5  | 06.02.2013 | J.Tremmel | added package path
# 1.6  | 11.02.2013 | J.Tremmel | merged functionality from ttk_version;
#                               | TTk release now follows version of ttk_base
# 1.7  | 20.02.2013 | J.Tremmel | => 1.3.0
# 1.8  | 08.05.2013 | J.Tremmel | => 1.3.1
# 1.9  | 10.10.2013 | J.Tremmel | => 1.3.2 beta
# 1.10 | 31.07.2014 | J.Tremmel | => 1.3.3 intermediate build
# 1.11 | 11.09.2014 | J.Tremmel | => 1.3.4 rc2 (intermediate release before 1.4.0)
# 1.12 | 24.09.2014 | J.Tremmel | => 1.3.4 rc3 (intermediate release before 1.4.0)
# 1.13 | 24.10.2014 | J.Tremmel | => 1.3.4 rc4 (yet another intermediate release before 1.4.0)
#                               | => 1.3.4 final
# 1.14 | 18.12.2015 | J.Tremmel | => 1.4.0
# 1.15 | 14.03.2016 | J.Tremmel | => 1.4.1 (additional class-config for ttk_bus)
# 1.16 | 18.03.2016 | J.Tremmel | => 1.4.2 (additional bugfixes)
# 1.17 | 04.04.2016 | L.Morgus  | wrapper for _init_
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2.0.0  | 22.12.2016 | J.Tremmel | => 2.0.0
# 2.1.0  | 08.06.2020 | J.Tremmel | migrated to Python 3, => 2.1.0
# 2.2.0  | 20.01.2022 | J.Tremmel | show ttk_build.info on init error (Feature #5665)
#******************************************************************************
try:
    from ttk_base._init_ import version         # @UnresolvedImport (compiled extension)
    from ttk_base._init_ import version_info    # @UnresolvedImport
    from ttk_base._init_ import showReleaseInfo # @UnresolvedImport
    from ttk_base._init_ import _package_path   # @UnresolvedImport
except ImportError as import_err:
    import os
    import sys
    import inspect 
    ttk_path = os.path.dirname(os.path.dirname(
        os.path.abspath(inspect.currentframe().f_code.co_filename)
    ))
    
    # prevent double-printing info if package marker gets called as __main__
    if __name__ != "__main__":
        print(">----------------------------------<")
        print("> TestToolkit failed to initialize <")
        print(">----------------------------------<")
        
        print("# Current System:")
        version = ".".join(str(v) for v in sys.version_info[:3])
        arch    = "x64" if sys.maxsize > 2**32 else "x86"
        plat    = "Windows" if sys.platform == "win32" else \
                  "Linux"   if sys.platform.startswith("linux") else \
                   sys.platform
        print(f"  Python {version} ({arch}, {plat})")
        print(f"  Python Executable: {sys.executable}")
        print(f"  TestToolkit Path:  {ttk_path}")
        print()
        
        print("# TestToolkit Build:")
        try:
            build_info_path = os.path.join(ttk_path, "ttk_build.info")
            with open(build_info_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    print(f"  {line.strip()}")
                
        except Exception:
            print("  ttk_build.info not available")
        
        
        print()
        sys.tracebacklimit = 0
    raise import_err

# #############################################################################
if __name__ == "__main__":
    print(f"package path: {_package_path}")
    showReleaseInfo()

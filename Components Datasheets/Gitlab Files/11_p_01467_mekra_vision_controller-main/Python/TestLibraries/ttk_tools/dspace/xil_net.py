#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : xil_net.py
# Package : ttk_tools.dspace
# Task    : Import helper module as workaround for current import hook 
#           compatibility issues between packages Cython and pythonnet.
#             
#           Requires "Python for .NET" (pythonnet) for .NET access
#           (which is provided in dSPACE releases that have XIL-API support)
#
# Type    : Implementation
# Python  : 3.6+
#
# Copyright 2020 - 2024 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 06.08.2020 | J.Tremmel  | initial
# 1.1.0  | 30.09.2021 | J.Tremmel  | explicitly load System.Collections
# 1.2.0  | 11.04.2023 | J.Tremmel  | added listing of available Testbenches
# 1.3.0  | 12.04.2023 | J.Tremmel  | added detection of used XIL API versions
# 1.3.1  | 21.07.2023 | J.Tremmel  | AddReference gets dynamically added to clr
#                                  | namespace in pythonnet 3.0. Added assertion
#                                  | to avoid "unresolved" warnings
# 1.3.2  | 16.01.2024 | J.Tremmel  | compare enums as ints in _checkEnums
#******************************************************************************
"""
@package ttk_tools.dspace.xil_net
Import helper module as workaround for current import hook compatibility issues 
between packages Cython and pythonnet.
See https://github.com/pythonnet/pythonnet/issues/941
    https://github.com/cython/cython/issues/3084
    
Note:
    If a specific XIL API version should be used (and auto detection is not 
    sufficient), a version can be defined in project settings
    
Example:
    # define a specific XIL API version to use in hil_project.ini
    
    [TestToolkit]
    # currently supported versions: 2.0.1, 2.1.0, 2.2.0
    xil_api_version = 2.1.0

"""
import os
from xml.dom.minidom import parse
try:
    # "Python for .NET": initially load the clr extension module
    import clr
except ImportError as ex:
    # Extend error message to be a bit more informative
    raise ImportError(
        'Package "Python for .NET" (pythonnet) is required for .NET access'
    ) from ex

from ttk_base import configuration

# We'll import all required .NET-based packages/modules here, using pythonnet's
# modified "classic" import hook (which is not supported in in cythonized code
# since Python 3). 
# Later on, _xil_api will import them from this namespace, so the compiled 
# code can resolve the already loaded packages/modules

# implicit loading is deprecated in more recent pythonnet builds.
# => explicitly load Collections
assert hasattr(clr, "AddReference") # pythonnet 3.x builds load attributes dynamically 
clr.AddReference('System.Collections')

# .NET namespaces & Co. are only available after (dynamically) loading the clr 
# extension module (if CLR support has been installed into the existing Python 
# installation)
from System import Int64, UInt64, Double, Boolean   # @UnresolvedImport @UnusedImport
from System import String                           # @UnresolvedImport @UnusedImport
from System import Array                            # @UnresolvedImport @UnusedImport
from System import Exception as DotNetException     # @UnresolvedImport @UnusedImport
from System import TimeoutException                 # @UnresolvedImport @UnusedImport
from System.Collections.Generic import Dictionary   # @UnresolvedImport @UnusedImport


# #############################################################################
# @cond DOXYGEN_IGNORE 
def _detectXilVersions(verbose=False):
    """ Detect XIL API versions used by available .NET Testbench 
        implementations (extracted from present Implementation Manifests, 
        works without loaded XIL assemblies).
        
        Parameters:
            verbose    -    True: print info on found Manifests
        
        Returns a list of version strings (sorted in ascending order),
        e.g. ["2.1.0", "2.2.0"]
    """
    xil_versions = set()
    # Storage location for Implementation Manifest files
    # (Windows Vista, 7, 10, and presumably 11):
    # %PROGRAMDATA%\ASAM\XIL\Implementation
    manifests_path = os.path.join(
        os.environ.get("PROGRAMDATA", ""), "ASAM", "XIL", "Implementation"
    )
    if not os.path.isdir(manifests_path):
        print( "> XIL Version detection:")
        print( "> Storage location for XIL Implementation Manifest files does not exist")
        print(f"> (expected: {manifests_path})")
        return []
        
    try:
        for file_name in os.listdir(manifests_path):
            _, ext = os.path.splitext(file_name)
            if ext.lower() != ".imf":
                continue
            dom = parse(os.path.join(manifests_path, file_name))
            for element in dom.getElementsByTagName("NetTestbenchImplementation"):
                attr = element.getAttribute
                if verbose:
                    print(f"# {file_name}")
                    print(f"  XIL Version: {attr('XilVersion')} | Vendor: {attr('VendorName')} |"
                          f" Product Name: {attr('ProductName')}, Version: {attr('ProductVersion')}")
                try:
                    # ensure all version entries have 3 elements
                    version = [int(v) for v in attr("XilVersion").split(".")]
                    version += [0, 0, 0]
                    xil_versions.add(tuple(version[:3]))
                except (TypeError, ValueError):
                    print(f"> XIL Version detection: {file_name}")
                    print(f"> skipped invalid XIL version entry: {attr('XilVersion')!r}")
        
    except Exception as ex:
        print("> XIL Version detection:")
        print("> Failed to access Implementation Manifests:")
        print(f"> {type(ex).__name__}: {ex}")
    
    return [".".join(str(v) for v in ver) for ver in sorted(xil_versions)]


# #############################################################################
def _checkEnums():
    """ Paranoia: compare local Enum definitions against Enums from
        ASAM.XIL.Interfaces in the .NET Assembly.
        Note: Requires loaded XIL API assemblies for the desired API version.
    """
    from ASAM.XIL.Interfaces.Testbench.Common.SignalGenerator.Enum import SignalGeneratorState  # @UnresolvedImport
    from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer.Enum  import DataType              # @UnresolvedImport
    from ASAM.XIL.Interfaces.Testbench.Common.Signal.Enum          import InterpolationTypes    # @UnresolvedImport
    from ASAM.XIL.Interfaces.Testbench.Common.Capturing.Enum       import CaptureState          # @UnresolvedImport
    from ASAM.XIL.Interfaces.Testbench.MAPort.Enum                 import MAPortState           # @UnresolvedImport
    
    from ttk_tools.dspace import xil_api_common as xc
    
    def compareEnums(py_enum, dotnet_enum):
        print(f"\n{py_enum.__name__}:")
        for member in list(py_enum):
            print(f"    {member.name:<20} = 0x{member.value:02X}", end=" ")
            if not hasattr(dotnet_enum, member.name):
                if member.name == "eSIMULATION_PAUSED":
                    print(" [missing] => was added in XIL 2.1.0")
                    continue
                names = ', '.join(v for v in vars(dotnet_enum) if v.startswith("e"))
                raise KeyError(f".NET {py_enum.__name__} has no member {member.name}\n"
                               f"Available member names: {names}")
            
            dotnet_value = int(getattr(dotnet_enum, member.name))
            if dotnet_value != member.value:
                raise ValueError(f"{member}: value mismatch: "
                                 f"Python: {member.value}, .NET: {dotnet_value}")
            print("   [OK]")
    
    compareEnums(xc.DataType, DataType)
    compareEnums(xc.CaptureState, CaptureState)
    compareEnums(xc.MAPortState, MAPortState)
    compareEnums(xc.InterpolationTypes, InterpolationTypes)
    compareEnums(xc.SignalGeneratorState, SignalGeneratorState)
# @endcond DOXYGEN_IGNORE


# #############################################################################
# Load ASAM assemblies from global assembly cache (GAC)
# See also "Assembly Names": https://msdn.microsoft.com/en-us/library/k8xx4k69.aspx
# ASAM.XIL.Implementation.TestbenchFactory seems to automatically add a reference 
# to ASAM.XIL.Interfaces.

# XIL-API 2.0.1 (released 2013)    dSPACE Releases 2014-B .. 2018-A
# XIL-API 2.1.0 (released 2017)    dSPACE Releases 2018-B .. 2021-B
# XIL-API 2.2.0 (released 2020)    dSPACE Releases 2022-A .. tbd.
# XIL-API 3.0.0 (tbd.)

## fallback/default version
default_xil_version = "2.2.0"
## detected versions in ascending order (if any)
available_xil_versions = _detectXilVersions(verbose=False)
## used specified version (from current hil_project.ini)
preferred_xil_version = configuration.getSettings().get(
    "TestToolkit", "xil_api_version", ""
)
candidates = [default_xil_version] 
candidates += available_xil_versions
if preferred_xil_version:
    candidates.append(preferred_xil_version)

xil_version = candidates[-1]
if xil_version == "2.0.1":
    print("[xil_net] using XIL API version 2.0.1") 
    clr.AddReference("ASAM.XIL.Implementation.TestbenchFactory, Version=2.0.1.0, Culture=neutral, PublicKeyToken=fc9d65855b27d387")
    clr.AddReference("ASAM.XIL.Interfaces, Version=2.0.1.0, Culture=neutral, PublicKeyToken=bf471dff114ae984")
    
elif xil_version == "2.1.0":
    print("[xil_net] using XIL API version 2.1.0") 
    clr.AddReference("ASAM.XIL.Implementation.TestbenchFactory, Version=2.1.0.0, Culture=neutral, PublicKeyToken=fc9d65855b27d387")
    clr.AddReference("ASAM.XIL.Interfaces, Version=2.1.0.0, Culture=neutral, PublicKeyToken=bf471dff114ae984")
    
elif xil_version == "2.2.0":
    print("[xil_net] using XIL API version 2.2.0") 
    clr.AddReference("ASAM.XIL.Implementation.TestbenchFactory, Version=2.2.0.0, Culture=neutral, PublicKeyToken=bf471dff114ae984")
    clr.AddReference("ASAM.XIL.Interfaces, Version=2.2.0.0, Culture=neutral, PublicKeyToken=bf471dff114ae984")
else:
    print("[xil_net] unrecognized XIL API version: %r"%(xil_version)) 
    # following imports will fail
    

# Import XIL API .NET classes from .NET assemblies
from ASAM.XIL.Implementation.TestbenchFactory.Testbench  import TestbenchFactory        # @UnresolvedImport @UnusedImport
from ASAM.XIL.Interfaces.Testbench.Common.Error          import TestbenchPortException  # @UnresolvedImport @UnusedImport 


# #############################################################################
# @cond DOXYGEN_IGNORE 
# #############################################################################
if __name__ == '__main__':  # pragma: no cover (contains only sample code)
    def header(label, width=96):
        print(f"\n== {label}", "=" * (width - len(label) - 4))
    
    # #########################################################################
    header(".NET Assemblies")
    for index, assembly in enumerate(clr.ListAssemblies(True), 1): # @UndefinedVariable ListAssemblies
        print(f"{index:3d}. {assembly}")
    
    # #########################################################################
    header(u"Mapped ENUMs")
    _checkEnums()
    # #########################################################################
    header("Available XIL Testbench Implementation Manifests")
    _detectXilVersions(verbose=True)
    
    # #########################################################################
    header("Available XIL Testbenches")
    try:
        for tb_info in TestbenchFactory().GetAvailableTestbenches():
            print(f"  XIL Version: {tb_info.XILVersion} | Vendor: {tb_info.VendorName} |"
                  f" Product Name: {tb_info.ProductName}, Version: {tb_info.ProductVersion}")
    except AttributeError as ex:
        # GetAvailableTestbenches officially only available in XIL API 2.2.0+
        print(f"> n/a in this XIL API version: {ex}")
        
    except Exception as ex:
        print( "> Failed to access available Testbenches:")
        print(f"> {type(ex).__name__}: {ex}")
        
    
# @endcond DOXYGEN_IGNORE
# #############################################################################

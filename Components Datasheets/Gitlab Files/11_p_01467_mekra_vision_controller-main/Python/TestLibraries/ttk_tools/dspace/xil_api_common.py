#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : xil_api_common.py
# Package : ttk_tools.dspace
# Task    : Common shared definitions and error classes for xil_api
#
# Type    : Implementation
# Python  : 3.6+
#
# Copyright 2016 - 2020 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0.0  | 18.10.2016 | J.Tremmel | initial, refactored error classes
# 1.1.0  | 21.12.2016 | J.Tremmel | moved writeMAPortConfigXML here 
# 1.2.0  | 02.02.2018 | J.Tremmel | added Python 2.5 compatibility tweaks
# 1.3.0  | 19.06.2020 | J.Tremmel | migrated to Python 3, 
#                                 | updated writeMAPortConfigXML examples
# 1.4.0  | 07.08.2020 | J.Tremmel | moved XIL enums to xil_api_common
# 1.5.0  | 09.09.2020 | J.Tremmel | fixed "invalid escape sequence" warnings 
#                                 | in docstrings (sample paths)
#******************************************************************************
"""
@package ttk_tools.dspace.xil_api_common
Common shared definitions and error classes for xil_api.
"""
import os
from ttk_base.errors import TTkException
from ttk_base.baseutils import EnumInfo


# #############################################################################
class DataType(EnumInfo):
    """ Data Types.
        See ASAM.XIL.Interfaces.Testbench.Common.ValueContainer.Enum.DataType
    """
    ## No explicit data type.
    eNO_TYPE          = 0x00
    ## A_BOOLEAN (simple data type)
    eBOOLEAN          = 0x01
    ## A_INT64 (simple data type) 
    eINT              = 0x02
    ## A_UINT64 (simple data type)
    eUINT             = 0x03
    ## A_FLOAT64 (simple data type)
    eFLOAT            = 0x04
    ## A_UNICODE2STRING (simple data type)
    eSTRING           = 0x05
    
    ## integer vector (complex data type)
    eINT_VECTOR       = 0x06
    ## float vector (complex data type)
    eFLOAT_VECTOR     = 0x07
    ## string vector (complex data type)
    eSTRING_VECTOR    = 0x08
    ## boolean vector (complex data type)
    eBOOLEAN_VECTOR   = 0x09
    
    ## integer matrix (complex data type)
    eINT_MATRIX       = 0x0A
    ## float matrix (complex data type)
    eFLOAT_MATRIX     = 0x0B
    ## string matrix (complex data type)
    eSTRING_MATRIX    = 0x0C
    ## boolean matrix (complex data type)
    eBOOLEAN_MATRIX   = 0x0D
    
    ## map (complex data type)
    eMAP              = 0x0E
    ## curve (complex data type)
    eCURVE            = 0x0F
    ## x-y value (complex data type)
    eXYVALUE          = 0x10
   
    ## unsigned integer vector (complex data type) 
    eUINT_VECTOR      = 0x11
    ## unsigned integer matrix (complex data type)
    eUINT_MATRIX      = 0x12
    ## signal value (complex data type)
    eSIGNALVALUE      = 0x13
    ## signal group value (complex data type)    
    eSIGNALGROUPVALUE = 0x14
    

# #############################################################################
class InterpolationTypes(EnumInfo):
    """ Data Interpolation Types.
        See ASAM.XIL.Interfaces.Testbench.Common.Signal.Enum.InterpolationTypes
    """
    ## Next data point will be used immediately (staircase forward) 
    eFORWARD    = 0
    ## Actual data point will be used until next data point (staircase backward) 
    eBACKWARD   = 1
    ## Linear interpolation between data points
    eLINEAR     = 2
    
    
# #############################################################################
class MAPortState(EnumInfo):
    """ Model Access Port States.
        See ASAM.XIL.Interfaces.Testbench.MAPort.Enum.MAPortState
     """
    eSIMULATION_STOPPED = 0x0000
    eSIMULATION_RUNNING = 0x0001
    eDISCONNECTED       = 0x0002
    eSIMULATION_PAUSED  = 0x0003 # available since XIL 2.1.0
    

# #############################################################################
class CaptureState(EnumInfo):
    """ Data Capture States.
        See ASAM.XIL.Interfaces.Testbench.Common.Capturing.Enum.CaptureState
     """
    ## capture created/setup (and is stopped)
    eCONFIGURED         = 0x00 
    ## waiting for trigger (if any)
    eACTIVATED          = 0x01 
    ## capture running
    eRUNNING            = 0x02 
    ## stop trigger reached (if any)
    eFINISHED           = 0x03 


# #############################################################################
class SignalGeneratorState(EnumInfo):
    """ Signal Generator States. 
        See ASAM.XIL.Interfaces.Testbench.Common.SignalGenerator.Enum.SignalGeneratorState
    """
    ## not yet loaded to target (or destroyed/unloaded)
    eIN_CONFIGURATION   = 0x00
    ## loaded to target
    eREADY              = 0x01
    ## stimulus finished running
    eFINISHED           = 0x02
    ## paused while running
    ePAUSED             = 0x03
    ## stimulus started and running
    eRUNNING            = 0x04
    ## running stopped 
    eSTOPPED            = 0x05
    

# #############################################################################
class TestbenchError(TTkException):
    """ Base class for "other" testbench errors that are not handled
        by XIL TestbenchPortExceptions
    """
    def __init__(self, msg, source=None, orig_exception=None):
        TTkException.__init__(self, msg)
        self.source         = source
        self.orig_exception = orig_exception
        

# #############################################################################
class StimulusError(TestbenchError):
    """ Errors during Stimulus setup/execution."""
    

# #############################################################################
def writeMAPortConfigXML(sdf_file_path, platform_name="DS1006", xml_file_path=None):
    """ Write a simple MAPort XML configuration file for dSPACE implementations
        to the specified path.
        
        Parameters:
            sdf_file_path  -  path to system description file (*.sdf).  
                              Note that this file does not have to exist to 
                              write the XML 
            platform_name  -  name of target platform hardware
            xml_file_path  -  file path to write configuration to.  
                              If None, a default file named "MAPortConfig.xml" 
                              will be created in same folder as the SDF-file.
        Note:
            `sdf_file_path` can be specified as an absolute path or as relative 
            to the location of the XML file (i.e. `xml_file_path`).
        
        Example:
            writeMAPortConfigXML(
                sdf_file_path = "D:/HIL-Projekte/Demo/Modell/demo.sdf",
                platform_name = "DS1006"
            )
            # => configuration will be written to 
            # D:/HIL-Projekte/Demo/Modell/MAPortConfig.xml
        
        Example:
            maport_config_path = os.path.join(
                _base_project_path, "ControlDesk", "MAPortConfig.xml"
            )
            sdf_file_path = os.path.join(
                # "scalexio" is the project folder below <hil_project>/ControlDesk/
                "scalexio", "Variable Descriptions", 
                "Inbetriebnahme.sdf", "Inbetriebnahme.sdf" # yep, folder and file are named the same
            )
            xil_api_common.writeMAPortConfigXML(
                sdf_file_path = sdf_file_path, # a relative path
                platform_name = "SCALEXIO",    # see platform properties in ControlDesk
                xml_file_path = maport_config_path
            )
            
        
        Returns the path to the written MAPort configuration file.
    """
    sdf_file_path = os.path.normpath(os.path.abspath(sdf_file_path))
    if xml_file_path is None:
        xml_file_path = os.path.join(
            os.path.dirname(sdf_file_path), "MAPortConfig.xml"
        )
    
    def escape(s):
        # just in case: escape "special" XML characters
        return s.replace("&", "&amp;") \
                .replace("<", "&lt;")  \
                .replace(">", "&gt;")
    
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<PortConfigurations>
    <MAPortConfig>
        <PlatformName>{escape(platform_name.strip())}</PlatformName>
        <SystemDescriptionFile>{escape(sdf_file_path)}</SystemDescriptionFile>
    </MAPortConfig>
</PortConfigurations>
"""
    with open(xml_file_path, "w", encoding="utf-8") as fh:
        fh.write(xml)
    
    return xml_file_path
    

# #############################################################################
# @cond DOXYGEN_IGNORE 
# #############################################################################
if __name__ == '__main__':  # pragma: no cover (contains only sample code)
    import tempfile
    
    xml_path = writeMAPortConfigXML(
        sdf_file_path = os.path.join(tempfile.gettempdir(), "demo.sdf"),
        platform_name = "DS1006"
    )
    print("#", xml_path)
    print("--8<%s"%("-" * 76))
    with open(xml_path, "r", encoding="utf-8") as f:
        print(f.read())
    print("%s>8--"%("-" * 76))
    
# @endcond DOXYGEN_IGNORE
# #############################################################################

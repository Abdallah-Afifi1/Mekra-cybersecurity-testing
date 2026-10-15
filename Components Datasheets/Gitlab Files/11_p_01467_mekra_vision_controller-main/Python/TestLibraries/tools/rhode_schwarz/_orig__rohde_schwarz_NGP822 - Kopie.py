"""********************Information, Version, History*************************
 -*- coding: UTF-8 -*-
 
 File    : C:/Users/voellerj/eclipse-workspace/MCP-HIL/generic_unicast_multicast/Lib/RodeSchwarz/Rode_Schwarz_NGP822.py
 Task    : "Define Rohde & Schwarz NGP 822 power supply"
 Author  : voellerj
 Date    : 07.02.2024


******************************************************************************
********************************* Version ************************************
******************************************************************************
 Rev. | Date       | Name        | Description
------------------------------------------------------------------------------
 1.0  | 07.02.2024 | voellerj    | initial
 1.1  | 14.03.2024 | reslc       | expanding library
 1.2  | 12.04.2024 | reslc       | enableOutput, disableOutput functions added
******************************************************************************
"""

#Imports######################################################################
import pyvisa as visa
from Lib.General import eventList
import numpy as np
import time

#******************************************************************************
class Rohde_Schwarz_NGP822:
    """
    Used to communicate with- and control the Rode_Schwarz_NGP822 power supply.
    """
    MAX_VOLTAGE = 64
    MAX_SET_VOLTAGE = 60
    MAX_CURRENT = 10
    MAX_SET_CURRENT = 10    
    
    def __init__(self, adress='', queryDelay=2):
        """
        Initializes the object.
        Searches for devices if no address is given.
        :param adress: The VISA adress
        :type adress: str.
        """
        self._psu = None #power supply unit
        self._queryDelay = queryDelay
        self.connected = False
        if not adress:
            self.adress = Rohde_Schwarz_NGP822.find()[0]
            print(self.adress)
        else:
            self.adress = adress

    @staticmethod
    def find(query='?*::INSTR'):
        """
        Finds all devices currently available.
        :param query: String pattern to look for.
        :type query: str.
        :return: list -- All devices.
        """
        _rm = visa.ResourceManager()
        devices = _rm.list_resources(query)
        _rm.close()
        return devices

    def connect(self):
        """
        Establishes the connection.
        :return: bool -- True if connected, else False.
        """
        self._rm = visa.ResourceManager()
        try:
            self._psu = self._rm.open_resource(self.adress)
            self.connected = False if self.getID() == "" else True
        except visa.VisaIOError as ex:
            self.connected = False
            print('Connect error: ' + ex.description)
        return self.connected

    def disconnect(self):
        """
        Closes the active connection.
        """
        self.send('SYST:LOC')
        self._psu.close()
        self._rm.close()

    def send(self, data):
        """
        General send method which is used by every command.
        :param data: The given data/command.
        :type data: str.
        """
        self._psu.write(data)

    def requestVal(self,data):
        """
        General request method which will use query() to request data.
        :param data: The given data/request.
        :type data: str.
        :param delay: The given delay in seconds.
        :type delay: int.
        :return: float -- Response.
        """
        return float(self._psu.query(data, delay=self._queryDelay))

    def requestStr(self, data):
        """
        General request method which will use query() to request data.
        :param data: The given data/request.
        :type data: str.
        :return: str -- Response.
        This method will block until newline is received or timeout is exceeded.
        """
        return self._psu.query(data, delay=self._queryDelay)


    #Common setting commands##############################################################

    def clearStatus(self):
        """
        Sets the status byte (STB), the standard event register (ESR) and the EVENt part of
        the QUEStionable and the OPERation registers to zero. The command does not
        alter the mask and transition parts of the registers. It clears the output buffer.
        """
        self.send('*CLS')

    def waitForReady(self):
        """
        Prevents servicing of the subsequent commands until all preceding commands have
        been executed and all signals have settled
        """
        self.send('*WAI')

    def getID(self):
        """
        Request the devices identification number.
        :return: str -- Identification number. 
                        "Rohde&Schwarz,<device type>,<part number>,<serial number>,<
                        firmware version>"
        """
        return self.requestStr('*IDN?')
    
    def storeInstrumentSettings(self, slot):
        """
        Stores the current instrument settings under the specified number in an internal memory.
        :param slot: int range 0-9
        """
        self.send('*SAV ' + slot)

    def loadInstrumentSettings(self, slot):
        """
        Loads the instrument settings from an internal memory identified by the specified number.
        :param slot: int range 0-9
        """
        self.send('*RCL ' + slot)

    #System settings commands############################################################


    #Display commands####################################################################
        
    def getDisplayBrightness(self):
        """
        Queries the display brightness.
        :return: float -- display brightness value
                            range 0.0 - 1.0; increment 0.1; RST 0.8
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getDisplayBrightness()')
        return float(self.requestStr('DISP:BRIG?'))
    
    def setDisplayBrightness(self, value):
        """
        Sets the display brightness to specified value
        :param value: float  Range: 0.0 to 1.0
        """
        if 0 <= value <= 1:
            eventList.addEvent('Rode_Schwarz_NGP822.setDisplayBrightness('+str(value)+')')
            self.send('DISP:BRIG ' + str(value))
        else:
            raise ValueError("Value must be between 0 and 1")
        
    def setDisplayText(self, text):
        """
        Shows the text message box on the front display.
        :param text: The given text message.
        :type text: str.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.showDisplayText('+ text +')')
        self.send('DISP:TEXT ' + text)

    def clearDisplay(self):
        """
        Clears the text message from the display.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.clearDisplay()')
        self.send('DISP:TEXT:CLE')
        
    #Trigger commands#####################################################################
        

    #Configuration commands###############################################################
    def setSafetyLimitState(self, value, channel=1):
        """
        sets the safety limit state
        :param  value: used to select safety level
                        0 -- deactivate safety limit
                        1 -- activate safety limit
                channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type   value: int
                channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.setSafetyLimitState('+ str(value) + ', ' + str(channel) + ')')
        self.send('ALIM ' + str(value) +', (@' + str(channel) + ')')

    def getSafetyLimitState(self, channel=1):
        """
        queries the safety limit state
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Safety Limit state.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getSafetyLimitState('+ str(channel) + ')')
        return self.requestStr('ALIM? ' + '(@'+str(channel)+')')

    def getMasterOutputState(self):
        """
        queries the master output state.
        """
        return self.requestStr('OUTP:GEN?')
    
    def setMasterOutputState(self, value):
        """
        Sets the master output state.
        :param value: used to select the state.
                        0 -- Switches off the master output
                        1 -- Switches on the master output
        :type value: int
        """
        self.send('OUTP:GEN '+ str(value))

    def getOutputState(self, channel=1):
        """
        queries the output state of selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        return self.requestStr('OUTP:SEL? ' +'(@'+str(channel)+')')
    
    def setOutputState(self, value, channel=1):
        """
        sets the output state of selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
                value: 
                        0 -- Deactivates the selected channel
                        1 -- Activates the selected channel
        :type channel: int
                value: int
        """
        self.send('OUTP:SEL ' + str(value) + ', (@' + str(channel) +')')

    def disableOutput(self, value=0, channel=1):
        """
        sets the output state of selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
                value: 
                        0 -- Deactivates the selected channel
                        1 -- Activates the selected channel
        :type channel: int
                value: int
        """
        self.send('OUTP:SEL ' + str(value) + ', (@' + str(channel) +')')

    def enableOutput(self, value=1, channel=1):
        """
        sets the output state of selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
                value: 
                        0 -- Deactivates the selected channel
                        1 -- Activates the selected channel
        :type channel: int
                value: int
        """
        self.send('OUTP:SEL ' + str(value) + ', (@' + str(channel) +')')

    def setVoltageLimit(self, value, channel=1):
        """
        Sets the output voltage limit on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :param value: The given voltage limit.
        :type value: float.
        """
        if value < 0 or value > Rohde_Schwarz_NGP822.MAX_VOLTAGE:
            return False
        else:
            eventList.addEvent('Rode_Schwarz_NGP822.setVoltageLimit(' + str(channel) + ', ' + str(value) + ')')
            Rohde_Schwarz_NGP822.MAX_SET_VOLTAGE = value
            return self.send('INST OUT' + str(channel) + ';:VOLT:ALIM ' + str(value))
        
    def setCurrentLimit(self, value, channel=1):
        """
        Sets a limit for the maximum current on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :param value: The given current limit.
        :type value: float.
        :return: bool -- True if successful, else False.
        """
        if value < 0 or value > Rohde_Schwarz_NGP822.MAX_CURRENT:
            return False
        else:
            eventList.addEvent('Rode_Schwarz_NGP822.setCurrentLimit(' + str(channel) + ', ' + str(value) + ')')
            Rohde_Schwarz_NGP822.MAX_SET_CURRENT = value
            return self.send('INST OUT' + str(channel) + ';:CURR:ALIM ' + str(value))

    def getVoltageLimit(self, channel=1):
        """
        Requests the set output voltage limit.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Voltage limit.
        :raises: ValueError
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getVoltageLimit(' + str(channel) + ')')
        return self.requestVal('VOLT:PROT:LEV? ' + '(@'+str(channel)+')')
        #return float(self.requestStr('INST OUT'+ str(channel) +';:VOLT:LIM?'))

    def getCurrentLimit(self, channel=1):
        """
        Requests the limit for the set maximum output current.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Current limit.
        :raises: ValueError
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getCurrentLimit(' + str(channel) + ')')
        return self.requestVal('POW:PROT:LEV? '+ '(@'+str(channel)+')')
        #return float(self.requestStr('INST OUT'+ str(channel) +';:CURR:LIM?'))
    
    def getPowerProtectionLevel(self, channel=1):
        """
        Queries the overvoltage protection value of the selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Current limit.
        :raises: ValueError
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getCurrentLimit()')
        return self.requestVal('POW:PROT:LEV? ' + '(@'+str(channel)+')')
    #Measurement commands#################################################################
        
    def getEnergy(self, channel=1):
        """
        Queries the measured accumulated released energy value (in Wh) of the previous selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Energy.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getEnergy(' + str(channel) + ')')
        return self.requestVal('MEAS:ENER? ' + '(@'+str(channel)+')')
    
    def getSampleNumber(self, channel=1):
        """
        Returns the number of samples measured in the statistics for voltage/current/power; number of measurements
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return:
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getSampleNumber(' + str(channel) + ')')
        return self.requestVal('MEAS:STAT:COUN? ' + '(@'+str(channel)+')')

    def resetStatistic(self, channel=1):
        """
        Resets the minimum, maximum and average statistic values for voltage, current, and power.
        Additionally this command resets the measured energy.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.resetStatistic(' + str(channel) + ')')
        return self.send('MEAS:STAT:RES '+'(@'+channel+')')
    
    def setCurrent(self, value, channel=1):
        """
        Sets the output current on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :param value: The given voltage.
        :type value: float.
        :return: bool -- True if successful, else False.
        """
        if value < 0 or value > Rohde_Schwarz_NGP822.MAX_SET_VOLTAGE:
            return False
        else:
            eventList.addEvent('Rode_Schwarz_NGP822.setCurrent(' + str(value) + ')')
            return self.send('INST OUT' + str(channel) + ';:CURR ' + str(value))
        
    def getCurrent(self, channel=1):
        """
        Requests the set maximum output current.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Current.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getCurrent(' + str(channel) + ')')
        return float(self.requestStr('INST OUT'+ str(channel) +';:CURR?'))
            
    def measureCurrent(self, channel=1):
        """
        Queries the actual emitted current of the selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Voltage.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.measureCurrent('+str(channel)+')')
        return self.requestVal('MEAS:CURR? ' + '(@'+str(channel)+')')

    def getCurrentAverage(self, channel=1):
        """
        Queries the average measured output current.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Voltage.
        :raises: ValueError
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getCurrentAverage('+str(channel)+')')
        return self.requestVal('MEAS:CURR:AVG? ' + '(@'+str(channel)+')')

    def getCurrentMax(self, channel=1):
        """
        Queries the maximum measured output current.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getCurrentMax('+str(channel)+')')
        return self.requestVal('MEAS:CURR:MAX? ' + '(@'+str(channel)+')')

    def getCurrentMin(self, channel=1):
        """
        Queries the minimum measured output current.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getCurrentMin('+str(channel)+')')
        return self.requestVal('MEAS:CURR:MIN? ' + '(@'+str(channel)+')')
    
    def getCurrentStatistic(self, channel=1):
        """
        Queries the current statistics of the selected channel.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return str
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getCurrentStatistic('+str(channel)+')')
        return self._psu.query('MEAS:CURR:STAT? ' + '(@'+str(channel)+')')
    
    def setPower(self, value, channel=1):
        """
        Sets the output power on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :param value: The given voltage.
        :type value: float.
        :return: bool -- True if successful, else False.
        """
        #if value < 0 or value > Rode_Schwarz_NGP822.MAX_SET_VOLTAGE:
        #    return False
        #else:
        eventList.addEvent('Rode_Schwarz_NGP822.setPower(' + str(channel) + ', '+ str(value) + ')')
        return self.send('INST OUT' + str(channel) + ';:POW ' + str(value))
            
    def measurePower(self, channel=1):
        """
        Queries the actual emitted power of the selected channel.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Power.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.measurePower('+str(channel)+')')
        return self.requestVal('MEAS:POW? ' + '(@'+str(channel)+')')

    def getPowerAverage(self, channel=1):
        """
        Queries the average measured output power.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Voltage.
        :raises: ValueError
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getPowerAverage('+str(channel)+')')
        return self.requestVal('MEAS:POW:AVG? ' + '(@'+str(channel)+')')

    def getPowerMax(self, channel=1):
        """
        Queries the maximum measured output power.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getPowerMax('+str(channel)+')')
        return self.requestVal('MEAS:POW:MAX? ' + '(@'+str(channel)+')')

    def getPowerMin(self, channel=1):
        """
        Queries the minimum measured output power.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getPowerMin('+str(channel)+')')
        return self.requestVal('MEAS:POW:MIN? ' + '(@'+str(channel)+')')
    
    def getPowerStatistic(self, channel=1):
        """
        Queries the power statistics of the selected channel.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return str
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getPowerStatistic('+str(channel)+')')
        return self._psu.query('MEAS:POW:STAT? ' + '(@'+str(channel)+')')
    
    def setVoltage(self, value=0, channel=1):
        """
        Sets the output voltage on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :param value: The given voltage.
        """
        if value < 0 or value > Rohde_Schwarz_NGP822.MAX_SET_VOLTAGE:
            return False
        else:
            eventList.addEvent('Rode_Schwarz_NGP822.setVoltage('+ str(channel)+ ', ' + str(value) + ')')
            return self.send('INST OUT' + str(channel) + ';:VOLT ' + str(value))
            
    def getVoltage(self, channel=1):
        """
        Requests the set output voltage from Channel on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Voltage.
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getVoltage(' + str(channel) + ')')
        return float(self.requestStr('INST OUT'+ str(channel) +';:VOLT?'))
    

    def measureVoltage(self, channel=1):
        """
        Requests the actual output voltage from Channel on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Voltage.
        :raises: ValueError
        """
        eventList.addEvent('Rode_Schwarz_NGP822.measureVoltage('+str(channel)+')')
        return self.requestVal('MEAS:VOLT? ' + '(@'+str(channel)+')')

    
    def getVoltageAverage(self, channel=1):
        """
        Requests the average measured output voltage from Channel on channel 1 or 2.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Voltage.
        :raises: ValueError
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getVoltage('+str(channel)+')')
        return self.requestVal('MEAS:VOLT:AVG? ' + '(@'+str(channel)+')')


    
    def getVoltageMax(self, channel=1):
        """
        Queries the maximum measured output voltage.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getVoltageMax('+str(channel)+')')
        return self.requestVal('MEAS:VOLT:MAX? ' + '(@'+str(channel)+')')

    
    def getVoltageMin(self, channel=1):
        """
        Queries the minimum measured output voltage.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getVoltageMin('+str(channel)+')')
        return self.requestVal('MEAS:VOLT:MIN? ' + '(@'+str(channel)+')')
    
    def getVoltageStatistic(self, channel=1):
        """
        Queries the voltage statistics of the selected channel.        
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return str eg. "(0.000000E+00, 0.000000E+00, 0.000000E+00)"
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getVoltageStatistic('+str(channel)+')')
        return self._psu.query('MEAS:VOLT:STAT? ' + '(@'+str(channel)+')')


    #Advanced operating commands#########################################################
    def setVoltageReading(self, value):
        """
        Sets the DMM reading after setting the output voltage level in channel adjustment process.
        :param value: voltage
        :type value: int/float
        """
        eventList.addEvent('Rode_Schwarz_NGP822.setVoltageReading('+str(value)+')')
        #self.send('INST OUT'+ str(channel) +';:CAL:VOLT:DATA')
        self.send('CAL:VOLT:DATA ' + str(value))

    def getVoltageReading(self, channel=1):
        """
        queries the DMM reading after setting the output voltage level in channel adjustment process.
        :param channel: used to select the channel.
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getVoltageReading('+str(channel)+')')
        return float(self.requestStr('INST OUT'+ str(channel) +';:CAL:VOLT:DATA?'))
    
    def setVoltageToVmax(self):
        """
        Sets the output voltage to high value 100 % of Vmax during voltage adjustment
        """
        self.send('CAL:VOLT:UMAX')

    def setVoltageToVmin(self):
        """
        Sets the output voltage to low value 1 % of Vmax during voltage adjustment
        """
        self.send('CAL:VOLT:UMIN')

    def measureTemperature(self, channel=1):
        """
        Returns the temperature of selected channel
        :param channel: used to select the channel
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Temperature
        """
        eventList.addEvent('Rode_Schwarz_NGP822.measureTemperature('+str(channel)+')')
        return float(self.requestStr('INST OUT'+ str(channel) +';:CAL:TEMP?'))

    #Data and file management commands#################################################

    def getTemperature(self, channel=1):
        """
        Returns the temperature of selected channel
        :param channel: used to select the channel
                        1 -- channel 1 is used
                        2 -- channel 2 is used
        :type channel: int
        :return: float -- Temperature
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getTemperature('+str(channel)+')')
        return float(self.requestStr('INST OUT'+ str(channel) +';:CAL:TEMP?'))
    
    
    #Status reporting commands##########################################################

    #Custom commands####################################################################

    def ramp(self, Ustart, Uend, step, wait, channel=1):
        """
        Increases/decreases voltage in predifined steps until final voltage 
        :param channel: used to select the channel
                        1 -- channel 1 is used
                        2 -- channel 2 is used
                Ustart: starting voltage 
                Uend: final voltage
                step: interval in which voltage will be increased/decreased
                wait: time for waiting between steps
        :type channel: int
                Ustart: int/float
                Uend: int/float
                step: int/float 
                wait: int -- seconds
        """
        eventList.addEvent('Rode_Schwarz_NGP822.getTemperature('+str(channel)+ ', ' + str(Ustart) + ', ' + str(Uend) + ', ' + str(step) + ', ' + str(wait) +')')

        self.setVoltage(Ustart, channel) #setting voltage for starting measurement
        
        #prepare device for measurement
        self.setMasterOutputState(1)
        self.setOutputState(1, channel)

        time.sleep(10) #waiting step for oscilloscope
        
        #ramp
        for s in np.arange(start=Ustart, stop=Uend, step=step):
            self.setVoltage(s, channel)
            time.sleep(wait)

        #stop measurement
        self.setOutputState(0, channel)
        self.setMasterOutputState(0)


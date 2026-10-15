"""
.. module:: sdmessage
    :platform: Unix, Windows
    :synopsis: Service Discovery Message
"""

from ipaddress import IPv4Address

ADDR_FLAGS = 0x10
ADDR_LENGTH_ENTRIES = 0x14
ADDR_TYPE = 0x18
ADDR_OPTION1_INDEX = 0x19
ADDR_OPTION2_INDEX = 0x1A
ADDR_OPTION_NUMBER = 0x1B
ADDR_SERVICE_ID = 0x1C
ADDR_INSTANCE_ID = 0x1E
ADDR_MAJOR_VERSION = 0x20
ADDR_TTL = 0x21
ADDR_MINOR_VERSION = 0x24
ADDR_LENGTH_OPTIONS = 0x28
ADDR_OPTION1_LENGTH = 0x2C
ADDR_OPTION1_TYPE = 0x2E
ADDR_ADDRESS = 0x30
ADDR_PROTOCOL = 0x35
ADDR_PORT = 0x36
ADDR_OPTION2_LENGTH = 0x38
ADDR_OPTION2_TYPE = 0x3A
ADDR_CONFIG = 0x3C


def ba2int(ba, startidx=0, size=1, bigEndian=True):
    """
    This helper is used to convert a ba to int.
    :param ba: Bytearray.
    :param startidx: Starting index.
    :param size: Size of int.
    :param bigEndian: True if bigendien, else false.
    :return: int
    """
    result = 0
    if len(ba) >= startidx + size:
        for byte in range(0, size):
            shifter = size - byte - 1 if bigEndian else byte
            result += ba[startidx + byte] << (shifter * 8)
    return result


class SDMessage:
    """
    Access to fields of Service Discovery message.
    """

    def __init__(self, ba):
        """
        :param ba: The byte array.
        :type ba: str.
        """
        self.ba = ba

    def flags(self):
        """
        :return: int - flags
        """
        return ba2int(self.ba, ADDR_FLAGS, 1)

    def lengthOfEntriesArray(self):
        """
        :return: int - lengthOfEntriesArray
        """
        return ba2int(self.ba, ADDR_LENGTH_ENTRIES, 4)

    def serviceType(self):
        """
        :return: int - serviceType
        """
        return ba2int(self.ba, ADDR_TYPE, 1)

    def option1Index(self):
        """
        :return: int - option1Index
        """
        return ba2int(self.ba, ADDR_OPTION1_INDEX, 1)

    def option2Index(self):
        """
        :return: int - option2Index
        """
        return ba2int(self.ba, ADDR_OPTION2_INDEX, 1)

    def option1Number(self):
        """
        :return: int - option1Number
        """
        return (ba2int(self.ba, ADDR_OPTION_NUMBER, 1) >> 4) & 0x0F

    def option2Number(self):
        """
        :return: int - option2Number
        """
        return ba2int(self.ba, ADDR_OPTION_NUMBER, 1) & 0x0F

    def serviceID(self):
        """
        :return: int - serviceID
        """
        return ba2int(self.ba, ADDR_SERVICE_ID, 2)

    def instanceID(self):
        """
        :return: int - instanceID
        """
        return ba2int(self.ba, ADDR_INSTANCE_ID, 2)

    def majorVersion(self):
        """
        :return: int - majorVersion
        """
        return ba2int(self.ba, ADDR_MAJOR_VERSION, 1)

    def ttl(self):
        """
        :return: int - ttl
        """
        return ba2int(self.ba, ADDR_TTL, 3)

    def minorVersion(self):
        """
        :return: int - minorVersion
        """
        return ba2int(self.ba, ADDR_MINOR_VERSION, 4)

    def lengthOfOptionsArray(self):
        """
        :return: int - lengthOfOptionsArray
        """
        return ba2int(self.ba, ADDR_LENGTH_OPTIONS, 4)

    def option1Length(self):
        """
        :return: int - length (= 9)
        """
        return ba2int(self.ba, ADDR_OPTION1_LENGTH, 2)

    def option1Type(self):
        """
        :return: int - type (IPv4 = 0x04)
        """
        return ba2int(self.ba, ADDR_OPTION1_TYPE, 1)

    def address(self):
        """
        :return: int - address
        """
        return str(IPv4Address(ba2int(self.ba, ADDR_ADDRESS, 4)))

    def l4protocol(self):
        """
        :return: int - protocol
        """
        return ba2int(self.ba, ADDR_PROTOCOL, 1)

    def port(self):
        """
        :return: int - port
        """
        return ba2int(self.ba, ADDR_PORT, 2)

    def option2Length(self):
        """
        :return: int - length
        """
        return ba2int(self.ba, ADDR_OPTION2_LENGTH, 2)

    def option2Type(self):
        """
        :return: int - type (Configuration = 0x01)
        """
        return ba2int(self.ba, ADDR_OPTION2_TYPE, 1)

    def configurationString(self):
        """
        :return: bytearray - configuration string ([len]id=value[len]id=value...)
        """
        totalLength = self.option2Length() - 1
        return self.ba[ADDR_CONFIG:ADDR_CONFIG + totalLength]

    def configuration(self):
        """
        :return: dict - configuration string as disctionary
        """
        config = {}
        totalLength = self.option2Length() - 1
        i = ADDR_CONFIG
        print("i: ", i)
        while i < ADDR_CONFIG + totalLength:
            length = ba2int(self.ba, i)
            print("length: ", length)
            if not length == 0x00:
                pair = self.ba[i + 1:i + 1 + length].decode('utf-8').split('=')
                print(pair)##################
                config[pair[0]] = None if len(pair) <= 1 else pair[1]
                i += length + 1
            else:
                break
        return config

    def __str__(self):
        """
        String representation of the object.
        :return: str -- All parameters.
        """
        obj_as_str = "flags = " + str(self.flags()) + \
                     "\nlengthOfEntriesArray = " + str(self.lengthOfEntriesArray()) + \
                     "\nserviceType = " + str(self.serviceType()) + \
                     "\noption1Index = " + str(self.option1Index()) + \
                     "\noption2Index = " + str(self.option2Index()) + \
                     "\noption1Number = " + str(self.option1Number()) + \
                     "\noption2Number = " + str(self.option2Number()) + \
                     "\nserviceID = " + str(self.serviceID()) + \
                     "\ninstanceID = " + str(self.instanceID()) + \
                     "\nmajorVersion = " + str(self.majorVersion()) + \
                     "\nttl = " + str(self.ttl()) + \
                     "\nminorVersion = " + str(self.minorVersion()) + \
                     "\nlengthOfOptionsArray = " + str(self.lengthOfOptionsArray()) + \
                     "\noption1Length = " + str(self.option1Length()) + \
                     "\noption1Type = " + str(self.option1Type()) + \
                     "\naddress = " + str(self.address()) + \
                     "\nl4protocol = " + str(self.l4protocol()) + \
                     "\nport = " + str(self.port()) + \
                     "\noption2Length = " + str(self.option2Length()) + \
                     "\noption2Type = " + str(self.option2Type()) + \
                     "\nconfigurationString = " + str(self.configuration())

        return obj_as_str

    def str_entry_rec_type_a(self):
        """
        String representation of the object.
        :return: str -- only parameters of entry record type A
        """
        obj_as_str = ("flags = " + str(self.flags()) +
                      "\nlengthOfEntriesArray = " + str(self.lengthOfEntriesArray()) +
                      "\nserviceType = " + str(self.serviceType()) +
                      "\noption1Index = " + str(self.option1Index()) +
                      "\noption2Index = " + str(self.option2Index()) +
                      "\noption1Number = " + str(self.option1Number()) +
                      "\noption2Number = " + str(self.option2Number()) +
                      "\nserviceID = " + str(self.serviceID()) +
                      "\ninstanceID = " + str(self.instanceID()) +
                      "\nmajorVersion = " + str(self.majorVersion()) +
                      "\nttl = " + str(self.ttl()) +
                      "\nminorVersion = " + str(self.minorVersion()))

        return obj_as_str

    def str_ipv4_endpoint_option(self):
        """
        String representation of the object.
        :return: str -- All parameters.
        """
        obj_as_str = ("lengthOfOptionsArray = " + str(self.lengthOfOptionsArray()) +
                      "\noption1Length = " + str(self.option1Length()) +
                      "\noption1Type = " + str(self.option1Type()) +
                      "\naddress = " + str(self.address()) +
                      "\nl4protocol = " + str(self.l4protocol()) +
                      "\nport = " + str(self.port()))

        return obj_as_str

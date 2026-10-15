import sys
import importlib.util
import pathlib
import numpy as np
import serial

from tools.SOMEIP import someip_packet
from datetime import datetime


def evaluate_response(param_testreport, send_packet, expected_packet, actual_packet, description, info=""):

    someippacket = someip_packet.SomeipPacket
    if expected_packet is not None:
        payload_expected = expected_packet.get_payload()

        if payload_expected == "Ignored":
            if expected_packet.compare_packet_ignore_payload(actual_packet) is True:
                print("   --> PASSED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Passed",
                                              "Payload ignored for packet compare! " + info)
            else:
                print("--> FAILED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Failed",
                                              "Payload ignored for packet compare! " + info)
        else:
            if expected_packet == actual_packet:
                print("   --> PASSED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Passed",
                                              info)
            else:
                print("--> FAILED")
                param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                              someippacket.get_formatted_packet(expected_packet),
                                              description,
                                              someippacket.get_formatted_packet(actual_packet),
                                              "Failed",
                                              info)
    else:
        if expected_packet == actual_packet:
            print("   --> PASSED")
            param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                          someippacket.get_formatted_packet(expected_packet),
                                          description,
                                          someippacket.get_formatted_packet(actual_packet),
                                          "Passed",
                                          info)
        else:
            print("--> FAILED")
            param_testreport.add_teststep(someippacket.get_formatted_packet(send_packet),
                                          someippacket.get_formatted_packet(expected_packet),
                                          description,
                                          someippacket.get_formatted_packet(actual_packet),
                                          "Failed",
                                          info)

"""
def add_teststep(send, expected, description, actual, verdict, info="testinfo"):
        teststep = [datetime.now().strftime("%H:%M:%S"), send, expected, description, actual, verdict, info]
        #return teststep
        teststeps.append(teststep)
"""

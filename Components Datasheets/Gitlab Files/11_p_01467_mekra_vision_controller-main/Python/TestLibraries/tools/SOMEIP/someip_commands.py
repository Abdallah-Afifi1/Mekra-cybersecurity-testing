#******************************************************************************
# -*- coding: utf-8 -*-
# File : dhcp_test.py
# Task : basic test for dhcp server
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 07.07.2025 | Reiner S | initial  
#******************************************************************************
#
#
#Imports:
#
import sys
import os
import datetime
from time import sleep
#from TestPool._automation_wrapper_ import TestEnv 
from tools.SOMEIP.someip_packet import SomeipPacket
from tools.SOMEIP.someip_client import SomeipClient
from time import perf_counter
from tools.helpFunctions import evaluate

test_report = []
"""
someip_client = SomeipClient(
        client_ip="192.168.120.1",
        server_ip="192.168.120.10",
        client_source_port="0",
        client_destination_port="62509")
"""
    
<<<<<<< HEAD
=======

>>>>>>> cd6bea95eb16eb82cfdd1fad980b69f85f9eab72


someip_client = SomeipClient(
        client_ip="192.168.120.1",
        server_ip="192.168.120.10",
        client_source_port="0",
        client_destination_port="30501")


def someip_cleanup():
    someip_client.close_socket()


def setCamControl():

    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0201,
        length=0x0000000d,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=None)
    

    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0201,
        length=0x0000000d,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)
    
    return sendPack(txpacket), exppacket

def getCamControl():

    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0203,
        length=0x00000009,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=None)

    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0203,
        length=0x00000009,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)
    
    return sendPack(txpacket), exppacket

def getCamStatus():

    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0002,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=None)

    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0002,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)
    
    return sendPack(txpacket), exppacket

def setCamExclusive(payload):

    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0011,
        length=0x0000000c,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=payload)

    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0011,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)
    
    return sendPack(txpacket), exppacket

def getDataSheet():

    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0001,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=None)

    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0201,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)
    
    return sendPack(txpacket), exppacket

def getCamIdentification():

    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0010,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=None)

    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0010,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)
    
    return sendPack(txpacket), exppacket


def subscribeROIVideo(payload):
    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0131,
        length=0x0000000c,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=payload)
    
    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0131,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)

    return sendPack(txpacket), exppacket

    
def unSubscribeROIVideo(payload):
    
    txpacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0132,
        length=0x0000000c,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x00,
        return_code=0x00,
        payload=payload)

    exppacket = SomeipPacket(
        service_id=0x433f,
        method_id=0x0132,
        length=0x00000008,
        request_id=0x12345678,
        protocol_version=0x01,
        interface_version=0x01,
        message_type=0x80,
        return_code=0x00,
        payload=None)
    
    return sendPack(txpacket), exppacket



def sendPack(txpacket):
    someip_client.send_packet(
        packet=txpacket,
        target_ip=someip_client.serverIP,
        destination_port=someip_client.destinationPort)
    rxpacket = someip_client.someip_rx_packet
    #print(rxpacket.get_packet_stream)
    
    return rxpacket


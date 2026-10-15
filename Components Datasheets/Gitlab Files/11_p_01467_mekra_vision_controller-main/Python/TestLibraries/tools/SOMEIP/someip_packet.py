from binascii import hexlify
#from Lib.General import helperModule


class SomeipPacket:

    _SOMEIP_PARAMETERLENGTH = 9

    def __init__(self, service_id=0x433F,
                 method_id=0x0203,
                 length=0x09,
                 request_id=0x12345678,
                 protocol_version=0x01,
                 interface_version=0x01,
                 message_type=0x00,
                 return_code=0x00,
                 payload=b'\x02',
                 copypacket=None):

        self._someip_fields = {
            'service_id': None,
            'method_id': None,
            'length': None,
            'request_id': None,
            'protocol_ver': None,
            'interface_ver': None,
            'message_type': None,
            'ret_code': None,
            'payload': None
        }

        self.set_service_id(service_id)
        self.set_method_id(method_id)
        self.set_length(length)
        self.set_request_id(request_id)
        self.set_protocol_version(protocol_version)
        self.set_interface_version(interface_version)
        self.set_message_type(message_type)
        self.set_return_code(return_code)
        self.set_payload(payload, 0, raw_data=True)

        if copypacket:

            if isinstance(copypacket, SomeipPacket):
                self._someip_fields = copypacket.get_fields()
            else:
                raise ValueError

    @staticmethod
    def parse_someip_input(value):

        if type(value) is str:
            # Set to lowercase
            value = value.lower()
            # Check if string should be treated as hex
            if value[0:2] == "0x":
                # String - Now check if string is hex
                valid_hex_chars = set('1234567890ABCDEFabcdef-+x')

                if set(value[2:]) <= valid_hex_chars:
                    parsed_value = int(value, 16)
                else:
                    raise ValueError("Incorrect string provided. After 0x detected wrong characters")

            else:
                valid_int_chars = set('1234567890-+')

                if set(value) <= valid_int_chars:
                    parsed_value = int(value)
                else:
                    raise ValueError("Incorrect string provided to be interpreted as integer")

        elif type(value) is int:
            # Since its an integer we do not convert
            parsed_value = value

        else:
            raise ValueError("Wrong datatype provided use either string or integer")

        return parsed_value

    def packet(self):

        if self._someip_fields['payload']:
            data = self._someip_fields['service_id'] +\
                   self._someip_fields['method_id'] +\
                   self._someip_fields['length_id'] +\
                   self._someip_fields['request_id'] +\
                   self._someip_fields['protocol_ver'] +\
                   self._someip_fields['interface_ver'] +\
                   self._someip_fields['message_type'] +\
                   self._someip_fields['ret_code'] +\
                   self._someip_fields['payload']
        else:

            data = self._someip_fields['service_id'] +\
                   self._someip_fields['method_id'] +\
                   self._someip_fields['length_id'] +\
                   self._someip_fields['request_id'] +\
                   self._someip_fields['protocol_ver'] +\
                   self._someip_fields['interface_ver'] +\
                   self._someip_fields['message_type'] +\
                   self._someip_fields['ret_code']

        return data

    def set_service_id(self, service_id):
        service_id_parsed = SomeipPacket.parse_someip_input(service_id)
        self._someip_fields['service_id'] = service_id_parsed.to_bytes(2, byteorder='big')
        return

    def get_service_id(self):
        service_id_field = self._someip_fields.get('service_id')
        service_id = hexlify(service_id_field).decode('ascii')
        return service_id

    def set_method_id(self, method_id):
        method_id_parsed = SomeipPacket.parse_someip_input(method_id)
        self._someip_fields['method_id'] = method_id_parsed.to_bytes(2, byteorder='big')
        return

    def get_method_id(self):
        method_id_field = self._someip_fields.get('method_id')
        method_id = hexlify(method_id_field).decode('ascii')
        return method_id

    def set_length(self, length):
        length_parsed = SomeipPacket.parse_someip_input(length)
        self._someip_fields['length_id'] = length_parsed.to_bytes(4, byteorder='big')
        return

    def get_length(self):
        length_field = self._someip_fields.get('length_id')
        length = hexlify(length_field).decode('ascii')
        return length

    def set_request_id(self, request_id):
        request_id_parsed = SomeipPacket.parse_someip_input(request_id)
        self._someip_fields['request_id'] = request_id_parsed.to_bytes(4, byteorder='big')
        return

    def get_request_id(self):
        request_id_field = self._someip_fields.get('request_id')
        request_id = hexlify(request_id_field).decode('ascii')
        return request_id

    def set_protocol_version(self, protocol_version):
        protocol_version_parsed = SomeipPacket.parse_someip_input(protocol_version)
        self._someip_fields['protocol_ver'] = protocol_version_parsed.to_bytes(1, byteorder='big')
        return

    def get_protocol_version(self):
        protocol_version_field = self._someip_fields.get('protocol_ver')
        protocol_version = hexlify(protocol_version_field).decode('ascii')
        return protocol_version

    def set_interface_version(self, interface_version):
        interface_version_parsed = SomeipPacket.parse_someip_input(interface_version)
        self._someip_fields['interface_ver'] = interface_version_parsed.to_bytes(1, byteorder='big')
        return

    def get_interface_version(self):
        interface_version_field = self._someip_fields.get('interface_ver')
        interface_version = hexlify(interface_version_field).decode('ascii')
        return interface_version

    def set_message_type(self, message_type):
        message_type_parsed = SomeipPacket.parse_someip_input(message_type)
        self._someip_fields['message_type'] = message_type_parsed.to_bytes(1, byteorder='big')
        return

    def get_message_type(self):
        message_type_field = self._someip_fields.get('message_type')
        message_type = hexlify(message_type_field).decode('ascii')
        return message_type

    def set_return_code(self, ret_code):
        ret_code_parsed = SomeipPacket.parse_someip_input(ret_code)
        self._someip_fields['ret_code'] = ret_code_parsed.to_bytes(1, byteorder='big')
        return

    def get_return_code(self):
        ret_code_field = self._someip_fields.get('ret_code')
        ret_code = hexlify(ret_code_field).decode('ascii')
        return ret_code

    def set_payload(self, payload, payload_size, raw_data=False):

        self._someip_fields['payload'] = None
        if payload is not None and not raw_data:
            payload_parsed = SomeipPacket.parse_someip_input(payload)
            self._someip_fields['payload'] = payload_parsed.to_bytes(payload_size, byteorder='big')
        elif raw_data:
            self._someip_fields['payload'] = payload

        return

    def get_payload(self):
        payload_field = self._someip_fields.get('payload')
        payload = None

        if payload_field == "Ignored":
            payload = "Ignored"
        else:
            if payload_field is not None:
                payload = hexlify(payload_field).decode('ascii')
        return payload
    
    def get_payload_as_bytes(self) -> bytes:
        payload_field = self._someip_fields.get('payload')
        payload = None

        if payload_field == "Ignored":
            payload = None
        else:
            if payload_field is not None:
                payload = payload_field
        return payload

    @staticmethod
    def get_packet_stream(packet):

        if packet is not None:
            someip_packet_stream = [
                packet.get_service_id(),
                packet.get_method_id(),
                packet.get_length(),
                packet.get_request_id(),
                packet.get_protocol_version(),
                packet.get_interface_version(),
                packet.get_message_type(),
                packet.get_return_code(),
            ]

            payload = packet.get_payload()
            if payload is not None:
                someip_packet_stream.append(payload)
        else:
            someip_packet_stream = None

        return someip_packet_stream

    def __eq__(self, other):

        if isinstance(other, SomeipPacket):
            # Compare each field to check for equality
            if self.get_method_id() == other.get_method_id()\
                    and self.get_service_id() == other.get_service_id()\
                    and self.get_interface_version() == other.get_interface_version() \
                    and self.get_protocol_version() == other.get_protocol_version()\
                    and self.get_length() == other.get_length()\
                    and self.get_message_type() == other.get_message_type() \
                    and self.get_request_id() == other.get_request_id()\
                    and self.get_return_code() == other.get_return_code()\
                    and self.get_payload() == other.get_payload():
                return True
            else:
                return False

        return NotImplemented

    def compare_packet_ignore_payload(self, other):

        if isinstance(other, SomeipPacket):

            # Compare each field except payload to check for equality
            if self.get_method_id() == other.get_method_id()\
                    and self.get_service_id() == other.get_service_id()\
                    and self.get_interface_version() == other.get_interface_version() \
                    and self.get_protocol_version() == other.get_protocol_version()\
                    and self.get_length() == other.get_length()\
                    and self.get_message_type() == other.get_message_type() \
                    and self.get_request_id() == other.get_request_id()\
                    and self.get_return_code() == other.get_return_code():
                return True
            else:
                return False

        return NotImplemented

    @staticmethod
    def get_formatted_packet(packet):

        data = SomeipPacket.get_packet_stream(packet)

        if data is not None:
            formatted_data = [
                "Service Id: " + data[0],
                "Method Id: " + data[1],
                "Length: " + data[2],
                "Request Id: " + data[3],
                "Protocol Version: " + data[4],
                "Interface Version: " + data[5],
                "Message Type: " + data[6],
                #"Return Code: " + data[7] + " (" + helperModule.get_human_readable_return_code(data[7]) + ")"
            ]

            try:
                if len(data[8]) > 25:
                    formatted_data.append("Payload: " + data[8][0:24] + " ...")
                else:
                    formatted_data.append("Payload: " + data[8])
            except IndexError:
                pass

        else:
            formatted_data = "No response from camera."

        return formatted_data

    def get_fields(self):
        return self._someip_fields

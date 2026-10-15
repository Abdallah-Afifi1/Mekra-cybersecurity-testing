"""
.. module:: rtpInfo
    :platform: Unix, Windows
    :synopsis: Store information about RTP packets.
"""

class RTPInfo:
    """
    Used to store information about RTP packets.
    """

    def __init__(self):
        """
        Initializes the object.
        The framerate has to be calculated from timestamp and sequence number of multiple packets.
        """
        self.version = None
        self.padding = None
        self.extension = None
        self.csic = None
        self.marker = None
        self.payload_type = None
        self.sequence_number = None
        self.timestamp = None
        self.framerate = None
        self.ssi = None
        self.payload = None

    def __str__(self):
        """
        String representation of the object.
        :return: str -- All parameters.
        """
        obj_as_str = "version = " + str(self.version) + \
                     "\npadding = " + str(self.padding) + \
                     "\nextension = " + str(self.extension) + \
                     "\ncsic = " + str(self.csic) + \
                     "\nmarker = " + str(self.marker) + \
                     "\npayload_type = " + str(self.payload_type) + \
                     "\nsequence_number = " + str(self.sequence_number) + \
                     "\ntimestamp = " + str(self.timestamp) + \
                     "\nframerate = " + str(self.framerate) + \
                     "\nssi = " + str(self.ssi) + \
                     "\npayload = \n" + str(self.payload)
        
        return obj_as_str
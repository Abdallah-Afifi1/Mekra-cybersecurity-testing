"""
.. module:: jpegInfo
    :platform: Unix, Windows
    :synopsis: Store information about JPEG packets.
"""

class JPEGInfo:
    """
    Used to store information about JPEG packets.
    """

    def __init__(self):
        """
        Initializes the object.
        """
        self.type_specific = None
        self.fragment_offset = None
        self.type = None
        self.q = None
        self.width = None
        self.height = None

    def __str__(self):
        """
        String representation of the object.
        :return: str -- All parameters.
        """
        obj_as_str = "type_specific = " + str(self.type_specific) + \
                     "\nfragment_offset = " + str(self.fragment_offset) + \
                     "\ntype = " + str(self.type) + \
                     "\nq = " + str(self.q) + \
                     "\nwidth = " + str(self.width) + \
                     "\nheight = " + str(self.height)
        
        return obj_as_str
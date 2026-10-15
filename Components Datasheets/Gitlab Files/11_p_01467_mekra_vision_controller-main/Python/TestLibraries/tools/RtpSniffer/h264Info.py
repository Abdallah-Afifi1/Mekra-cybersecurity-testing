"""
.. module:: h264Info
    :platform: Unix, Windows
    :synopsis: Store information about H264 packets.
"""

class H264Info:
    """
    Used to store information about H264 packets.
    """

    def __init__(self):
        """
        Initializes the object.
        """
        self.f_bit = None
        self.nal_ref_idc = None
        self.type = None
        self.profile_idc = None
        self.profile_iop = None
        self.level_idc = None
        self.width = None
        self.height = None

    def __str__(self):
        """
        String representation of the object.
        :return: str -- All parameters.
        """
        obj_as_str = "f_bit = " + str(self.f_bit) + \
                     "\nnal_ref_idc = " + str(self.nal_ref_idc) + \
                     "\ntype = " + str(self.type) + \
                     "\nprofile_idc = " + str(self.profile_idc) + \
                     "\nprofile_iop = " + str(self.profile_iop) + \
                     "\nlevel_idc = " + str(self.level_idc) + \
                     "\nwidth = " + str(self.width) + \
                     "\nheight = " + str(self.height)
        
        return obj_as_str
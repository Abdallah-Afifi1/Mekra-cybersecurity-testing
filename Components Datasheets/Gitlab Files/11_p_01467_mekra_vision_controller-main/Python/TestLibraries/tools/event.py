"""
.. module:: event
    :platform: Unix, Windows
    :synopsis: Event with timestamp and description.
"""

class Event:
    """
    Used to store Events with timestamp and description.
    """
    def __init__(self, timestamp, description):
        """ 
        Creates an event with timestamp and description.
        :param description: Description of the event.
        :type description: str.
        :param timestamp: Event timestamp in seconds.
        :type timestamp: float.
        """
        self.timestamp = timestamp
        self.description = description

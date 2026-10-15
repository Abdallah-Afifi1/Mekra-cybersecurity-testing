"""
.. module:: eventList
    :platform: Unix, Windows
    :synopsis: Global EventHistory where all Events are stored.
"""

import time
from tools.event import *

evtlist = []
t_start = time.perf_counter()


def addEvent(description):
    """
    Creates an Event and adds it to the list.
    :param description: Description of the Event.
    :type description: str.
    :return: int -- Index of Event.
    """
    t_event = time.perf_counter()
    temp = Event(t_event, description)
    evtlist.append(temp)


def getDescription(index):
    """
    Returns the description of an Event at the specified index.
    Use -1 for the latest (last) Event.
    :param index: Index of element in list.
    :type index: int.
    :return: str -- Description of Event.
    :raises: IndexError
    """
    return evtlist[index].description


def getTimestamp(index):
    """
    Returns the timestamp of an Event at the specified index.
    Use -1 for the latest (last) Event.
    :param index: Index of element in list.
    :type index: int.
    :return: float -- Timestamp of Event.
    :raises: IndexError
    """
    return evtlist[index].timestamp


def getTimestampDifference(index1, index2):
    """
    Calculates the difference between two Event timestamps.
    Use -1 for the latest (last) Event.
    :param index1: Index of first element in list.
    :type index1: int.
    :param index2: Index of second element in list.
    :type index2: int.
    :return: float -- Timestamp difference.
    :raises: IndexError
    """
    t1 = evtlist[index1].timestamp
    t2 = evtlist[index2].timestamp
    return abs(t2 - t1)


def getLastIndex():
    """
    Returns the index of for the last added Event.
    :return: int -- Index
    """
    return len(evtlist) - 1


def getLength():
    """
    Returns the length of the evtlist.
    :return: int -- Length
    """
    return len(evtlist)


def clearList():
    evtlist.clear()

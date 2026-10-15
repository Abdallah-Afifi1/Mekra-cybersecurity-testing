#******************************************************************************
# -*- coding: utf-8 -*-
#
# File    : bridged.py
# Task    : bridging decorator to supplement static analysis efforts
# Python  : 3
#
# Copyright 2025 iSyst Intelligente Systeme GmbH
#
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name      | Description
#------------------------------------------------------------------------------
# 1.0.0  | 19.03.2025 | Tremmel   | adapted from automation wrapper tests
#******************************************************************************
from functools import wraps

# #############################################################################
def bridged(method):
    """ A bridging decorator (bridges method call to parent class).
        Can be used  for explicitly adding inherited methods that static code 
        analysis otherwise cannot "see" (like modules in compiled extensions or 
        (pyd) or pyz files...).
        This may help auto-completion features
        
        Example:
            class Foo(Bar):
                @bridged
                def qux(self, baz):
                    ''' qux something '''
                    # method body will be skipped, instead, Bar.qux(self, baz)
                    # gets called and its result returned.
     """
    @wraps(method) # => preserves name and docstring of wrapped function
    def wrapper(self, *args, **kwargs):
        return getattr(super(type(self), self), method.__name__)(*args, **kwargs)
    return wrapper


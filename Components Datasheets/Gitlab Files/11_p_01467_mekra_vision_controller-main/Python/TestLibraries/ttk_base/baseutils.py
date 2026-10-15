#******************************************************************************
# -*- coding: utf-8 -*-
# File    : baseutils.py
# Package : ttk_base
# Task    : General utility functions and classes 
#
# Type    : Interface
# Python  : 3.6
#
# Copyright 2016 - 2022 iSyst Intelligente Systeme GmbH
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.| Date       | Name       | Description
#------------------------------------------------------------------------------
# 1.0 | 11.08.2016 | J.Tremmel  | initial
# 1.1 | 19.09.2016 | J.Tremmel  | added CustomRepr
# 1.2 | 18.10.2016 | J.Tremmel  | added EnumInfo
# 1.3 | 21.12.2016 | J.Tremmel  | added sleepWithFeedback
# 1.4 | 09.03.2017 | J.Tremmel  | added fsEncode
# 1.5 | 02.05.2018 | J.Tremmel  | added EnumInfo.getName
# 1.6 | 29.08.2018 | J.Tremmel  | added fsDecode
# 1.7 | 20.05.2020 | J.Tremmel  | ustr now always returns unicode text, added bstr 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2.0.0  | 10.06.2020 | J.Tremmel | migrated to Python 3.
# 2.3.0  | 16.12.2021 | J.Tremmel | added getSpacedHexString (Feature #954)
# 2.3.1  | 27.06.2022 | J.Tremmel | docstring tweaks&cleanup
#******************************************************************************
""" 
@package ttk_base.baseutils
Interface wrapper for general utility functions and classes in ttk_base._baseutils.
"""
from ttk_base import _baseutils # @UnresolvedImport (compiled extension)
from ttk_base._baseutils import DEFAULT_ENCODING  # @UnresolvedImport @UnusedImport, see ttk_base.configuration
from ttk_base._baseutils import BYTES_ENCODING    # @UnresolvedImport @UnusedImport


# #############################################################################
# HexList
# #############################################################################
class HexList(_baseutils.HexList):
    """ A list that returns a representation in hexadecimal notation (for 
        easier reading). This - obviously - makes the most sense for numeric 
        values, especially bytes.
        
        Notes:
            * Getting an indexed item will return the numeric byte value, 
              even if "bytes" have been added as (single) characters.
            * Float values that are "close enough" (see FLOAT_CONVERSION_LIMIT)
              will be rounded to the nearest natural number before creating
              a hex representation
            * if an entry cannot be interpreted, it will be represented as-is
            * Only representation and indexed access is modified, the original 
              list contents will not be modified
        
        Examples:
            HexList([0, 1, 2, 3, 4, 252, 253, 254, 255])
            >>> [0x00, 0x01, 0x02, 0x03, 0x04, 0xFC, 0xFD, 0xFE, 0xFF]
            
            HexList("\x00\x01\x02\x03\x04\xFC\xFD\xFE\xFF")
            >>> [0x00, 0x01, 0x02, 0x03, 0x04, 0xFC, 0xFD, 0xFE, 0xFF]
            
            HexList([1023, 1024, 0xFFFF, "\xAA", 0, -1, -0xFFFFFFFF])
            >>> [0x3FF, 0x400, 0xFFFF, 0xAA, 0x00, -0x01, -0xFFFFFFFF]
            
            HexList([1, 2, "some string", u"ö", 1.000001, 2.99999, 1.123, None])
            >>> [0x01, 0x02, 'some string', 0xF6, 0x01, 0x03, 1.123, None]
            
            list(HexList([1, 2, "three", u"ö", 1.123, 1.0, None]))
            >>> [1, 2, 'three', u'\xf6', 1.123, 1.0, None]
            
            HexList([1, 2, "three", u"ö", 1.123, 1.0, None])[:]
            >>> [1, 2, 'three', u'\xf6', 1.123, 1.0, None]
    """
    def __getitem__(self, index):
        """ Get item at index. 
            
            Note: 
                If the item is a single character, its ordinal number will be 
                returned.
            
            Parameters:
                index - index of item to get
            
            Returns the specified item as a numeric value (if possible).
        """
        return _baseutils.HexList.__getitem__(self, index)
    
    def __repr__(self):
        """ Get list contents in hexadecimal formatting (if possible). """
        return _baseutils.HexList.__repr__(self)


# #############################################################################
def getSpacedHexString(value, min_bytes=1, spacer=" "):
    """ Get a hex string representation of Bytes in the supplied (unsigned) 
        integer value. Bytes will be shown in big endian order.
        
        Parameters:
            value     - unsigned numeric source value
            min_bytes - minimum number of bytes to return. Padding with 
                        zero bytes will be added at start of string.
                        At least one byte will always be shown.
            spacer    - spacer character(s) between hex-bytes
        
        Example: 
            >>> getSpacedHexString(0x123456, 4, " ")
            "00 12 34 56" 
        
        Returns a hex string with extra (white) space added between bytes.
    """
    return _baseutils.getSpacedHexString(
        value=value, min_bytes=min_bytes, spacer=spacer
    )


# #############################################################################
class EnumInfo(_baseutils.EnumInfo):
    """ Utility/convenience class for "enum-like" value container classes. 
        Provides a getInfo (class-)method that can be used to get a textual 
        representation of contained values.
        
        Example:
            # default text is the (first) matching numeric member name:
            class SOME_ENUM(EnumInfo):
                ONE   = 1
                TWO   = 2
                THREE = 3
            
            >>> SOME_ENUM.ONE
            1 
            >>> SOME_ENUM.getInfo(2)
            'TWO'
            >>> SOME_ENUM.getInfo(0xFF)
            '<undefined: 255>'
        
        Example:
            # customized text representations can be supplied via a 
            # member __info_mapping__:
            class SOME_ENUM(EnumInfo):
                ONE   = 1
                TWO   = 2
                THREE = 3
                __info_mapping__ = {
                     ONE:     "number one",
                     TWO:     "number two",
                     THREE:   "number three",
                }
            >>> SOME_ENUM.ONE
            1
            >>> SOME_ENUM.getInfo(2)
            'number two'
            >>> SOME_ENUM.getInfo(0xFF)
            '<undefined: 255>'
    """
    # #########################################################################
    @classmethod
    def getInfo(cls, value, fallback="<undefined: %(value)s>"):
        """ Get a textual info for the supplied value (if one is available).
            Info will be taken from a member dictionary __info_mapping__ with
            a fallback to the first member name that matches the supplied 
            value.
            
            Parameters:
                value     - one of this class' "constants"
                fallback  - fallback text for unknown values
            
            Returns an info string.
        """
        return _baseutils.EnumInfo.getInfo.__func__( # @UndefinedVariable
            # __func__ (in Py2: im_func) is not really undefined, 
            # it is available at run time
            cls, value=value, fallback=fallback
        )
    
    # #########################################################################
    @classmethod
    def getName(cls, value, fallback="<undefined: %(value)s>"):
        """ Get a textual representation for the supplied value from matching 
            "constant" in class members
            
            Parameters:
                value     - one of this class' "constants"
                fallback  - fallback text for unknown values
            
            Returns a  name string.
        """
        return _baseutils.EnumInfo.getName.__func__( # @UndefinedVariable __func__
            cls, value=value, fallback=fallback
        )
    
    # #########################################################################
    @classmethod
    def values(cls):
        """ Get all defined values as a list """
        return _baseutils.EnumInfo.values.__func__(cls) # @UndefinedVariable
    
    # #########################################################################
    @classmethod
    def printDefinedValues(cls, min_width=8):
        """ Print all defined (int) values of this enum-ish container,
            along with their text descriptions.
            Parameters:
                min_width - minimum width used for key formatting
        """
        _baseutils.EnumInfo.printDefinedValues.__func__(cls, min_width) # @UndefinedVariable __func__
        

# #############################################################################
def getCustomRepr(value, fmt=None):
    """ Get a custom string representation of a value.
        
        Parameters:
            value - value to get a representation of
            fmt   - string format (e.g. "%.2f") or one of the predefined format 
                    keywords
        
        Info: Predefined format keywords
            * "hex" - hexadecimal representation with leading 0x and uppercase digits  
                      e.g. 0xC0FFEE  
            * "int" - integer decimal representation  
                      e.g. 42  
            * "dec" - as "int", but with leading 0d  
                      e.g. 0d42  
            * "oct" - octal representation with leading 0o  
                      e.g. 0o777  
            * "bin" - binary representation with leading 0b  
                      e.g. 0b101010  
            * "pct" - percentage representation with trailing %.  
                      Note that value will be interpreted as a factor,  
                      e.g. 0.05 will be formatted as 5 %
            * "flt" - float representation with decimal places (just for convenience)
        
        Note:
            Float values for hex/int/dec/oct/bin will be *rounded* towards the
            nearest integer number (fractional part will not just be cut-off)
        
        Info: Format keyword options
            Each keyword may be followed by a number to give additional 
            representation hints.
            
            For integer numbers in hex/int/dec/oct/bin, this will specify a 
            minimum width (in nibbles, digits, octets or bits) that will be 
            filled with leading zeroes, e.g. 
               * "hex8": 0x00C0FFEE
               * "dec8": 0d00004711
               * "bin8": 0b01000010
            
            For pct and flt, the number will represent the number of decimal
            places, e.g.
               * "pct2": 2.21 %
               * "flt3": 2.212
    
    """
    return _baseutils.getCustomRepr(value=value, fmt=fmt)
    

# #############################################################################
def isCustomRepr(s):
    """ Check if s is formatted using a custom representation or just a 
        default/fallback string representation (or anything else).
        
        Parameters:
            s - string/object to check
        
        Returns True if s is a string containing a custom representation, 
        otherwise False.
    """
    return _baseutils.isCustomRepr(s)
    

# #############################################################################
# byte-string / unicode text utilities
# #############################################################################


# #############################################################################
def bstr(obj, encoding=DEFAULT_ENCODING):
    """ Get a byte string representation of an object, that is, like str()
        but returns a raw bytes string.
        
        Note:
            If characters in `obj`'s string representation cannot be mapped 
            using the given `encoding`, a backslashed replacement sequence 
            will be added in their stead.
            
        Examples:
            >>> bstr("foö") # default encoding, should match source encoding
            b'fo\xc3\xb6'   # two bytes for "ö" in utf-8 
            
            >>> bstr("foö", "ASCII")
            b'fo\\xf6'      # replacement sequence for "ö", as it is n/a in 7-bit ASCII
            
            >>> bstr("foö", "latin-1")
            b'fo\xf6'       # "ö" maps to a single byte in latin-1 
            
            >>> bstr(b"fo\x00\xff") 
            b'fo\x00'       # bytes in, bytes out 
            
            >>> bstr(bytearray((102, 111, 0, 255)))
            bytearray(b'fo\x00\xff') # bytearray in, bytearray out
            
        
        Parameters:
            obj      - object to represent as byte string
            encoding - encoding to use to encode unicode/text-strings.
                       Defaults to DEFAULT_ENCODING
        
        Returns a byte string (or bytearray if obj was already a bytearray)
    """
    return _baseutils.bstr(obj, encoding)


# #############################################################################
def ustr(obj, encoding=DEFAULT_ENCODING):
    """ Get a unicode/text string representation of an object. 
        Raw byte strings will be decoded using the supplied `encoding`.
        
        Parameters:
            obj      - object to represent as text string
            encoding - encoding to use to decode byte-strings.
                       Defaults to DEFAULT_ENCODING
        
        Returns a unicode text string
    """
    return _baseutils.ustr(obj, encoding)
    

# #############################################################################
def uni(s):
    """ Enforce unicode/text strings. 
        Raw byte strings will be decoded according to `DEFAULT_ENCODING`.
        Non-byte-string values will be left as-is.
        
        Examples:
            uni("foo")
            >>> u'foo'
            
            uni(u"foo")
            >>> u'foo'
            
            uni([1, 2])
            >>> [1, 2]
        
        Parameters:
            s     -    original string/object
        
        Returns s as unicode if it was a string to begin with, 
        otherwise the unmodified object.
    """
    return _baseutils.uni(s)
    

# #############################################################################
def fsEncode(s):
    """ Get a representation of (unicode/ASCII) string s, using the current 
        file system encoding. This is mainly useful for subprocess calls to 
        treat command line arguments or file names that may contain non-ASCII 
        characters.
        
        Note: 
            If a raw byte-string is supplied, it will first be decoded using
            the `DEFAULT_ENCODING` (see ustr()), so "special" characters may 
            raise a UnicodeDecodeError.  
            Always supply unicode strings if special characters are necessary.
        
        Parameters:
            s - (unicode) string to encode
        
        Returns a byte string suitable for use with file system functions.
    """
    return _baseutils.fsEncode(s)
    

# #############################################################################
def fsDecode(s):
    """ Get a unicode representation of byte string s, using the current file 
        system encoding (if available). This is mainly useful to treat file 
        names that may contain non-ASCII characters.
        Note that any decoding errors will be ignored.
        
        Parameters:
            s - (byte) string to decode
        
        Returns a unicode representation of s.
    """
    return _baseutils.fsDecode(s)
    

# #############################################################################
# odds & ends
# #############################################################################

# #############################################################################
def sleepWithFeedback(delay_ms, comment=None, step_ms=100, done_msg=None):
    """ Sleep for the specified delay and print some feedback/progress to 
        console/log. This is just a convenience function.
        
        Parameters:
            delay_ms   -  delay in milliseconds
            comment    -  comment to print at beginning, 
                          None: use default comment
            step_ms    -  step size for feedback
            done_msg   -  comment to print when done
                          None: use default comment
        
        Example:
            >>> sleepWithFeedback(1000)
            Waiting 1000 ms... ......... ...done
        
    """
    _baseutils.sleepWithFeedback(
        delay_ms = delay_ms, 
        comment  = comment, 
        step_ms  = step_ms, 
        done_msg = done_msg,
    )
    

# #############################################################################
# @cond DOXYGEN_IGNORE
# #############################################################################
if __name__ == "__main__": # pragma: no cover (main contains only sample code)
    
    print("\n== HexList ======================================================")
    print("numbers:    ", HexList([0, 1, 2, 3, 4, 252, 253, 254, 255]))
    print("text-string:", HexList("\x00\x01\x02\x03\x04\xFC\xFD\xFE\xFF"))
    print("byte-string:", HexList(b"\x00\x01\x02\x03\x04\xFC\xFD\xFE\xFF"))
    print("mixed:      ", HexList([1023, 1024, 0xFFFF, "\xAA", 0, -1, -0xFFFFFFFF]))
    print("other:      ", HexList([1, 2, "some string", "ö", 1.000001, 2.99999, 1.123, None]))
    
    print("\n== HexList vs. list =============================================")
    hl = HexList([1, 2, "three", "ö", 1.123, 1.0, None])
    print("hexlist:        ", hl)
    print("indexed access: ", hl[0], hl[1], hl[2], hl[3], hl[4], hl[5], hl[6], end=' ')
    print("# (values returned as natural numbers, as far as sensible)")
    print("hexlist as list:", list(hl))
    print("sliced hexlist: ", hl[:], "# (again a normal list)")
    
    print("\n== byte-string / unicode utilities ==============================")
    
    def demo(func, *args, width=16):
        sig = f"{func.__name__}({', '.join(repr(a) for a in args)})"
        out = func(*args)
        print(f"{sig:<{width}} => {out!r:<{width}} (type {type(out).__name__})")
    
    print("# uni: any string to unicode string")
    demo(uni, "foo")
    demo(uni, b"foo")
    demo(uni, [1, 2])
    
    print("# ustr: <x> to base string")
    demo(ustr, "foo")
    demo(ustr, b"foo")
    demo(ustr, [1, 2])
    
    print("# ustr: <x> to base string / ASCII")
    demo(ustr,  "\xbbfoo\x00\x01\xb5\xab", "ASCII", width=42)
    demo(ustr, b"\xbbfoo\x00\x01\xb5\xab", "ASCII", width=42)
    demo(ustr, [1, 2],                     "ASCII", width=42)
    
    print("# bstr: <x> to raw bytes string")
    demo(bstr, "foo")
    demo(bstr, b"foo")
    demo(bstr, [1, 2])
    
    
    print("\n== getCustomRepr ================================================")
    
    def gcr(value, fmt):
        cr = getCustomRepr(value, fmt)
        print(f"{value:<12} as {fmt!r:12} => {cr}")
        
    gcr(1234, "int")
    gcr(2**400, "hex")
    gcr(-0xC0FFEE, "hex8")
    
    print("# " * 42)
    gcr(1234, "pct")
    gcr(2**400, "pct")
    gcr(-0xC0FFEE, "pct")
    gcr(-0xC0FFEE, "pct2")
    
    print("# " * 42)
    gcr(0.12345678, "pct")
    gcr(0.12345678, "pct0")
    gcr(0.12345678, "pct1")
    gcr(0.12345678, "pct2")
    gcr(0.12345678, "pct3")
    gcr(0.12345678, "pct4")
    
    print("# " * 42)
    gcr(0.01499, "pct")
    gcr(0.01499, "pct0")
    gcr(0.01499, "pct1")
    gcr(0.01499, "pct2")
    
    gcr(12.11, "%.2f")
    gcr(12.11, ".2f")
    
    print("# " * 42)
    gcr(12.11499, "flt")
    gcr(12.11499, "flt0")
    gcr(12.11499, "flt1")
    gcr(12.11499, "flt2")
    gcr(12.11499, "flt3")
    
    gcr(12.5, "flt")
    gcr(12.5, "flt0")
    gcr(12.5001, "flt")
    gcr(12.5001, "flt0")
    
    gcr(123, "öäü %s fóo") 
    
    
    # #########################################################################
    print("# " * 42)
    print("# EnumInfo")
    
    class SOME_ENUM(EnumInfo):
        ONE   = 1
        TWO   = 2
        THREE = 3
    
    assert SOME_ENUM.ONE == 1
    assert SOME_ENUM.getInfo(2) == 'TWO'
    assert SOME_ENUM.getInfo(0xFF) == '<undefined: 255>'
    assert list(SOME_ENUM.values()) == [1, 2, 3]
    SOME_ENUM.printDefinedValues()
    
    class SOME_ENUM_TOO(EnumInfo):
        ONE   = 1
        TWO   = 2
        THREE = 3
        THREE_TOO = 3
        __info_mapping__ = {
             ONE:     "number one",
             TWO:     "number two",
        }
    assert SOME_ENUM_TOO.ONE == 1
    assert SOME_ENUM_TOO.getInfo(2) == 'number two'
    assert SOME_ENUM_TOO.getInfo(3) in ('THREE', 'THREE_TOO')
    assert SOME_ENUM_TOO.getInfo(0xFF) == '<undefined: 255>'
    assert list(SOME_ENUM_TOO.values()) == [1, 2, 3]
    SOME_ENUM_TOO.printDefinedValues()
    
    # #########################################################################
    print("\n" + "# " * 42)
    print("# sleepWithFeedback")
    print("[default]    ", end=' ')
    sleepWithFeedback(delay_ms=1000)
    print("[customized] ", end=' ')
    sleepWithFeedback(delay_ms=1000, comment="<start comment>", step_ms=200, done_msg="<stop comment>")
    print("[no_comments]", end=' ')
    sleepWithFeedback(delay_ms=1000, comment="", step_ms=50, done_msg="")
    
    print("Done.")
# @endcond DOXYGEN_IGNORE
# #############################################################################

#******************************************************************************
# -*- coding: utf-8 -*-
# File: dut_config_loader.py
# Task: Helperfile for DUT_Settings
# 
#******************************************************************************
#********************************* Version ************************************
#******************************************************************************
# Ver.   | Date       | Name     | Description
#------------------------------------------------------------------------------
# 1.0.0  | 24.02.2026 | Völler J.  | initial  
#******************************************************************************

from dataclasses import dataclass
from typing import Optional, Dict, Any
import importlib.util
import ipaddress
import datetime
import re

# ---------------------------------------------------------
# Helpers: Byte/IP/MAC conversions
# ---------------------------------------------------------
def _ensure_bytes_or_list_of_ints(val) -> bytes:
    if isinstance(val, bytes):
        return val
    if isinstance(val, (list, tuple)):
        return bytes(val)
    raise TypeError(f"Expect bytes or list/tuple of ints, received: {type(val)}")

def bytes_to_ascii(val) -> str:
    b = _ensure_bytes_or_list_of_ints(val)
    return b.decode("ascii", errors="strict")

def bytes_to_mac(val) -> str:
    b = _ensure_bytes_or_list_of_ints(val)
    if len(b) != 6:
        raise ValueError(f"MAC bytes must be 6 characters long, but are {len(b)}")
    mac = ":".join(f"{x:02x}" for x in b)
    if mac == "00:00:00:00:00:00":
        raise ValueError("Invalid MAC (0-Addr).")
    return mac

def bytes_to_ip(val) -> str:
    b = _ensure_bytes_or_list_of_ints(val)
    if len(b) != 4:
        raise ValueError(f"IP bytes must be 4 bytes long, but are {len(b)}")
    ip_str = ".".join(str(x) for x in b)
    ipaddress.ip_address(ip_str)  # validiert
    return ip_str

def ensure_int(val) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        val = val.strip()
        base = 16 if val.lower().startswith("0x") else 10
        return int(val, base)
    raise TypeError(f"Expect int or str, received: {type(val)}")

# ---------------------------------------------------------
# Temperature decoding according to Polarion specification:
# https://erg-polarion-p1.mekra.net/polarion/redirect/project/11_P_01467_MEKRA_Vision_Controller/workitem?id=MVC-92908
# Bits:
# [13]   = SignBit (1 = negativ, 0 = positiv)
# [12:4] = IntegerBits (9 Bits)
# [3:0]  = FractionBits (4 Bits)
#
# Temperature = Sign * IntegerBits + (FractionBits * 1/16)
# ---------------------------------------------------------
def decode_t_imager(value: int) -> float:
    sign_bit = (value >> 13) & 0x01
    integer_bits = (value >> 4) & 0x1FF
    fraction_bits = value & 0x0F
    sign = -1 if sign_bit == 1 else +1
    return sign * integer_bits + (fraction_bits * (1 / 16))


# ---------------------------------------------------------
# Unix Timestamp decoding
# ---------------------------------------------------------

EPOCH_MIN = 946684800    # year 2000
EPOCH_MAX = 4102444800   # year 2100

def _epoch_in_range(ts: int) -> bool:
    return EPOCH_MIN <= ts <= EPOCH_MAX


def _epoch_to_iso(ts: int) -> str:
    return datetime.datetime.utcfromtimestamp(ts).isoformat() + "Z"


def decode_ascii_unix_timestamp(text: str) -> Optional[str]:
    """
    Supports:
    - decimal Unix time (e.g. "1714038302")
    - hex Unix time (e.g. "6629051E")
    - hex with 0x prefix
    """
    s = text.strip()

    # decimal
    if s.isdigit():
        ts = int(s)
        return _epoch_to_iso(ts) if _epoch_in_range(ts) else None

    # hex with 0x
    if s.lower().startswith("0x"):
        try:
            ts = int(s, 16)
            return _epoch_to_iso(ts) if _epoch_in_range(ts) else None
        except ValueError:
            return None

    # pure hex
    if re.fullmatch(r"[0-9A-Fa-f]+", s):
        try:
            ts = int(s, 16)
            return _epoch_to_iso(ts) if _epoch_in_range(ts) else None
        except ValueError:
            return None

    return None


def decode_binary_unix_timestamp(raw: bytes) -> Optional[str]:
    """
    Tries LE and BE 4‑byte Unix time.
    """
    if len(raw) != 4:
        return None

    ts_le = int.from_bytes(raw, "little")
    if _epoch_in_range(ts_le):
        return _epoch_to_iso(ts_le)

    ts_be = int.from_bytes(raw, "big")
    if _epoch_in_range(ts_be):
        return _epoch_to_iso(ts_be)

    return None


# ---------------------------------------------------------
# Data model
# ---------------------------------------------------------
@dataclass
class ProductionData:
    mac_address: str
    batch_number: str
    part_number: int
    part_rev_raw: bytes
    serial_number: str
    ep_short: str
    hw_ver: str
    snpn: Optional[int]
    timestamp_raw: Optional[bytes]
    timestamp: Optional[str]


@dataclass
class SwConfig:
    par_ver: str
    device_type: str
    someip_sd_src_port: int
    someip_sd_dst_port: int
    someip_sd_dst_ip: str
    camera_service_port: int
    shutter_supported: int

    # Raw values (hex) of the file
    raw_t_imager_auto_on: int
    raw_t_imager_auto_off: int
    raw_t_imager_protection_on: int
    raw_t_imager_protection_off: int

    # decoded temperatures
    t_imager_auto_on_c: float
    t_imager_auto_off_c: float
    t_imager_protection_on_c: float
    t_imager_protection_off_c: float

    numbers_of_roi: int
    rtp_src_port1: int
    rtp_src_port2: int
    rtp_dst_ip1: str
    rtp_dst_ip2: str
    rtp_dst_port1: int
    rtp_dst_port2: int
    rtp_vlan_id1: int
    rtp_vlan_id2: int

# ---------------------------------------------------------
# Load Python file as module
# ---------------------------------------------------------
def _load_module_from_path(py_path: str):
    spec = importlib.util.spec_from_file_location("dyn_mod", py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module: {py_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ---------------------------------------------------------
# Productionsdata read
# ---------------------------------------------------------
def read_production_data(py_path: str) -> ProductionData:
    mod = _load_module_from_path(py_path)

    mac_address = bytes_to_mac(getattr(mod, "macAddress"))
    batch_number = bytes_to_ascii(getattr(mod, "batchNumber"))
    part_number = ensure_int(getattr(mod, "partNumber"))
    part_rev_raw = _ensure_bytes_or_list_of_ints(getattr(mod, "partRev"))
    serial_number = bytes_to_ascii(getattr(mod, "serialNumber"))
    ep_short = bytes_to_ascii(getattr(mod, "epShort"))
    hw_ver = bytes_to_ascii(getattr(mod, "hwVer"))
    snpn = getattr(mod, "snpn", None)
    if snpn is not None:
        snpn = ensure_int(snpn)

    timestamp_raw = None
    timestamp = None

    if hasattr(mod, "TimeStamp"):
        timestamp_raw = _ensure_bytes_or_list_of_ints(getattr(mod, "TimeStamp"))
        try:
            ascii_val = bytes_to_ascii(timestamp_raw)
            timestamp = decode_ascii_unix_timestamp(ascii_val)
            if timestamp is None:
                timestamp = ascii_val
        except UnicodeDecodeError:
            timestamp = decode_binary_unix_timestamp(timestamp_raw)

    return ProductionData(
        mac_address=mac_address,
        batch_number=batch_number,
        part_number=part_number,
        part_rev_raw=part_rev_raw,
        serial_number=serial_number,
        ep_short=ep_short,
        hw_ver=hw_ver,
        snpn=snpn,
        timestamp_raw=timestamp_raw,
        timestamp=timestamp,
    )

# ---------------------------------------------------------
# SW-Configuration read
# ---------------------------------------------------------
def read_sw_config(py_path: str) -> SwConfig:
    mod = _load_module_from_path(py_path)

    par_ver = bytes_to_ascii(getattr(mod, "parVer"))
    device_type = bytes_to_ascii(getattr(mod, "device_type"))
    someip_sd_src_port = ensure_int(getattr(mod, "someIpSdSourcePort"))
    someip_sd_dst_port = ensure_int(getattr(mod, "someIpSdDestinationPort"))
    someip_sd_dst_ip = bytes_to_ip(getattr(mod, "someIpSdDestinationIp"))
    camera_service_port = ensure_int(getattr(mod, "cameraServicePort"))
    shutter_supported = ensure_int(getattr(mod, "shutterSupported"))

    # >>> Load raw temperature data <<<
    raw_auto_on = ensure_int(getattr(mod, "T_imager_auto_on"))
    raw_auto_off = ensure_int(getattr(mod, "T_imager_auto_off"))
    raw_prot_on = ensure_int(getattr(mod, "T_imager_protection_on"))
    raw_prot_off = ensure_int(getattr(mod, "T_imager_protection_off"))

    # >>> Decode temperature <<<
    auto_on_c = decode_t_imager(raw_auto_on)
    auto_off_c = decode_t_imager(raw_auto_off)
    prot_on_c = decode_t_imager(raw_prot_on)
    prot_off_c = decode_t_imager(raw_prot_off)

    numbers_of_roi = ensure_int(getattr(mod, "numbersOfRegionOfInterest"))
    rtp_src_port1 = ensure_int(getattr(mod, "RtpSourcePort1"))
    rtp_src_port2 = ensure_int(getattr(mod, "RtpSourcePort2"))
    rtp_dst_ip1 = bytes_to_ip(getattr(mod, "RtpDestinationIp1"))
    rtp_dst_ip2 = bytes_to_ip(getattr(mod, "RtpDestinationIp2"))
    rtp_dst_port1 = ensure_int(getattr(mod, "RtpDestinationPort1"))
    rtp_dst_port2 = ensure_int(getattr(mod, "RtpDestinationPort2"))
    rtp_vlan_id1 = ensure_int(getattr(mod, "RtpVlanId1"))
    rtp_vlan_id2 = ensure_int(getattr(mod, "RtpVlanId2"))

    return SwConfig(
        par_ver=par_ver,
        device_type=device_type,
        someip_sd_src_port=someip_sd_src_port,
        someip_sd_dst_port=someip_sd_dst_port,
        someip_sd_dst_ip=someip_sd_dst_ip,
        camera_service_port=camera_service_port,
        shutter_supported=shutter_supported,

        raw_t_imager_auto_on=raw_auto_on,
        raw_t_imager_auto_off=raw_auto_off,
        raw_t_imager_protection_on=raw_prot_on,
        raw_t_imager_protection_off=raw_prot_off,

        t_imager_auto_on_c=auto_on_c,
        t_imager_auto_off_c=auto_off_c,
        t_imager_protection_on_c=prot_on_c,
        t_imager_protection_off_c=prot_off_c,

        numbers_of_roi=numbers_of_roi,
        rtp_src_port1=rtp_src_port1,
        rtp_src_port2=rtp_src_port2,
        rtp_dst_ip1=rtp_dst_ip1,
        rtp_dst_ip2=rtp_dst_ip2,
        rtp_dst_port1=rtp_dst_port1,
        rtp_dst_port2=rtp_dst_port2,
        rtp_vlan_id1=rtp_vlan_id1,
        rtp_vlan_id2=rtp_vlan_id2,
    )

# ---------------------------------------------------------
# Output utility
# ---------------------------------------------------------
def to_dict(obj) -> Dict[str, Any]:
    from dataclasses import asdict, is_dataclass
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError("Object cannot be converted to dict.")
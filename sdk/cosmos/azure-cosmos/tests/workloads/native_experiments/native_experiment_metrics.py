# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Process memory snapshots; platform-specific fields are deliberately distinct."""

import ctypes
import json
from pathlib import Path
import sys


def kib_fields(text, required):
    """Read required /proc kB fields, rejecting missing or malformed evidence."""
    result = {}
    for line in text.splitlines():
        name, separator, value = line.partition(":")
        if not separator or name not in required:
            continue
        parts = value.split()
        if name in result or len(parts) != 2 or parts[1] != "kB":
            raise ValueError(f"Malformed or duplicate /proc field: {name}")
        count = int(parts[0])
        if count < 0:
            raise ValueError(f"Negative /proc field: {name}")
        result[name] = count * 1024
    missing = set(required) - result.keys()
    if missing:
        raise ValueError(f"Missing /proc fields: {sorted(missing)}")
    return result


def linux_memory(status, rollup):
    """Do not interpret private resident pages as Windows private commit."""
    process = kib_fields(status, ("VmHWM", "VmSize"))
    pages = kib_fields(rollup, ("Rss", "Pss", "Private_Clean", "Private_Dirty"))
    return {
        "source": "proc/self/status+smaps_rollup",
        "rss_bytes": pages["Rss"],
        "pss_bytes": pages["Pss"],
        "private_clean_dirty_resident_bytes": pages["Private_Clean"] + pages["Private_Dirty"],
        "virtual_bytes": process["VmSize"],
        "lifetime_peak_rss_bytes": process["VmHWM"],
    }


def windows_memory():
    """Use PROCESS_MEMORY_COUNTERS_EX without adding a runtime dependency."""

    class MemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_uint32),
            ("faults", ctypes.c_uint32),
            ("peak_working_set", ctypes.c_size_t),
            ("working_set", ctypes.c_size_t),
            ("peak_paged_pool", ctypes.c_size_t),
            ("paged_pool", ctypes.c_size_t),
            ("peak_nonpaged_pool", ctypes.c_size_t),
            ("nonpaged_pool", ctypes.c_size_t),
            ("pagefile", ctypes.c_size_t),
            ("peak_pagefile", ctypes.c_size_t),
            ("private_usage", ctypes.c_size_t),
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(MemoryCounters), ctypes.c_uint32]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    counters = MemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return {
        "source": "GetProcessMemoryInfo",
        "rss_bytes": counters.working_set,
        "private_committed_bytes": counters.private_usage,
        "lifetime_peak_rss_bytes": counters.peak_working_set,
    }


def snapshot_json():
    """Return one platform-labelled snapshot; unsupported platforms fail."""
    if sys.platform == "win32":
        result = windows_memory()
    elif sys.platform.startswith("linux"):
        result = linux_memory(
            Path("/proc/self/status").read_text(encoding="ascii"),
            Path("/proc/self/smaps_rollup").read_text(encoding="ascii"),
        )
    else:
        raise RuntimeError(f"Unsupported experiment platform: {sys.platform}")
    return json.dumps(result)

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

class LocalizedMapView(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """LocalizedMapView."""

    AE = "AE"
    """United Arab Emirates (Arabic View)"""
    AR = "AR"
    """Argentina (Argentinian View)"""
    BH = "BH"
    """Bahrain (Arabic View)"""
    IN = "IN"
    """India (Indian View)"""
    IQ = "IQ"
    """Iraq (Arabic View)"""
    JO = "JO"
    """Jordan (Arabic View)"""
    KW = "KW"
    """Kuwait (Arabic View)"""
    LB = "LB"
    """Lebanon (Arabic View)"""
    MA = "MA"
    """Morocco (Moroccan View)"""
    OM = "OM"
    """Oman (Arabic View)"""
    PK = "PK"
    """Pakistan (Pakistani View)"""
    PS = "PS"
    """Palestinian Authority (Arabic View)"""
    QA = "QA"
    """Qatar (Arabic View)"""
    SA = "SA"
    """Saudi Arabia (Arabic View)"""
    SY = "SY"
    """Syria (Arabic View)"""
    YE = "YE"
    """Yemen (Arabic View)"""
    AUTO = "Auto"
    """Return the map data based on the IP address of the request."""
    UNIFIED = "Unified"
    """Unified View (Others)"""

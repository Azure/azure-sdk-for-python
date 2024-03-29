# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class AvailabilityStateValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Availability status of the resource."""

    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    UNKNOWN = "Unknown"


class ReasonChronicityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Chronicity of the availability transition."""

    TRANSIENT = "Transient"
    PERSISTENT = "Persistent"

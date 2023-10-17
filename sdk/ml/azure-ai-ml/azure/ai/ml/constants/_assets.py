# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta

from azure.ai.ml._utils._experimental import experimental


@experimental
class IPProtectionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    "Intellectual property protection level."
    ALL = "all"
    NONE = "none"

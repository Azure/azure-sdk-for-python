# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.ai.ml._utils._experimental import experimental
from azure.core import CaseInsensitiveEnumMeta


@experimental
class IPProtectionLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    ALL = "all"
    NONE = "none"

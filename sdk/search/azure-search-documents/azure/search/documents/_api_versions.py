# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    #: this is the default version
    V2020_06_30 = "2020-06-30"
    V2023_11_01 = "2023-11-01"
    V2024_07_01 = "2024-07-01"


DEFAULT_VERSION = ApiVersion.V2024_07_01

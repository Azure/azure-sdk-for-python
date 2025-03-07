# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_06_14 = "2023-06-14"
    V2024_04_15 = "2024-04-15"


DEFAULT_VERSION = ApiVersion.V2024_04_15

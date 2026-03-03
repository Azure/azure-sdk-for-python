# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_03_31 = "2023-03-31"
    V2024_07_01_PREVIEW = "2024-07-01-preview"
    V2025_09_01 = "2025-09-01"


DEFAULT_VERSION = ApiVersion.V2025_09_01

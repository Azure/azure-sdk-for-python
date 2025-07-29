# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2020_06_30 = "2020-06-30"
    V2023_11_01 = "2023-11-01"
    V2024_07_01 = "2024-07-01"
    V2025_05_01_PREVIEW = "2025-05-01-preview"


DEFAULT_VERSION = ApiVersion.V2025_05_01_PREVIEW

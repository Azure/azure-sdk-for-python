# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2022_07_18_PREVIEW = "2022-07-18-preview"
    V2023_11_01 = "2023-11-01"
    V2024_01_18_PREVIEW = "2024-01-18-preview"


DEFAULT_VERSION = ApiVersion.V2024_01_18_PREVIEW.value

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_08_24_PREVIEW = "2023-08-24-preview"
    V2024_02_01 = "2024-02-01"
    V2024_08_30 = "2024-08-30"
    V2024_11_15_preview = "2024-11-15-preview"


DEFAULT_VERSION = ApiVersion.V2024_11_15_preview.value

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_03_06 = "2023-03-06"
    V2023_06_15_PREVIEW = "2023-06-15-preview"
    V2023_10_15 = "2023-10-15"
    V2023_10_03_PREVIEW = "2023-10-03-preview"
    V2024_04_15 = "2024-04-15"
    V2024_06_15_PREVIEW = "2024-06-15-preview"
    V2024_09_15 = "2024-09-15"
    V2024_11_15_PREVIEW = "2024-11-15-preview"
    V2025_05_15 = "2025-05-15"
    V2025_03_30_PREVIEW = "2025-03-30-preview"
    V2025_06_15 = "2025-06-15"
    V2025_08_15_PREVIEW = "2025-08-15-preview"
    V2024_09_01_PREVIEW = "2024-09-01-preview"

DEFAULT_VERSION = ApiVersion.V2024_09_01_PREVIEW.value

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_03_06 = "2023-03-06"
    V2023_10_15 = "2023-10-15"
    V2024_04_15 = "2024-04-15"
    V2024_09_15 = "2024-09-15"
    V2025_05_15 = "2025-05-15"
    V2025_06_15 = "2025-06-15"


DEFAULT_VERSION = ApiVersion.V2025_06_15.value

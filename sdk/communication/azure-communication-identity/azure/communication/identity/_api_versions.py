# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2021_03_07 = "2021-03-07"
    V2022_06_01 = "2022-06-01"
    V2022_10_01 = "2022-10-01"
    V2023_10_01 = "2023-10-01"


DEFAULT_VERSION = ApiVersion.V2023_10_01

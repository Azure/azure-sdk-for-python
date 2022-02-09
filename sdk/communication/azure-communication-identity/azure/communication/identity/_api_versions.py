# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

# pylint: disable=enum-must-be-uppercase
class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2021_03_07 = "2021-03-07"
    V2021_10_31_preview = "2021-10-31-preview"
    V2022_06_01 = "2022-06-01"


DEFAULT_VERSION = ApiVersion.V2022_06_01

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2021_04_07_PREVIEW = "2021-04-07"
    V2022_02_01_PREVIEW = "2022-02-01"

DEFAULT_VERSION = ApiVersion.V2022_02_01_PREVIEW

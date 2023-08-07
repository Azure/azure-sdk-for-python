# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    #: this is the default version
    V2020_06_30 = "2020-06-30"
    V2021_04_30_PREVIEW = "2021-04-30-Preview"
    V2023_07_01_PREVIEW = "2023-07-01-Preview"


DEFAULT_VERSION = ApiVersion.V2023_07_01_PREVIEW

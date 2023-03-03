# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2021_10_01_PREVIEW = "2021-10-01-preview"
    V2023_01_15_PREVIEW = "2023-01-15-preview"


DEFAULT_VERSION = ApiVersion.V2023_01_15_PREVIEW

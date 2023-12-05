# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_06_14 = "2023-06-14"
    V2023_10_30_PREVIEW = "2023-10-30-preview"

DEFAULT_VERSION = ApiVersion.V2023_10_30_PREVIEW

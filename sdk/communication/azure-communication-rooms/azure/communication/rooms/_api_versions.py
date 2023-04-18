# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_03_31_PREVIEW = "2023-03-31-preview"

DEFAULT_VERSION = ApiVersion.V2023_03_31_PREVIEW

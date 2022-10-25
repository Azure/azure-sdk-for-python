# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2022_03_01_PREVIEW = "2022-03-01-preview"


DEFAULT_VERSION = ApiVersion.V2022_03_01_PREVIEW

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


# pylint: disable=enum-must-be-uppercase
class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2022_07_18_preview = "2022-07-18-preview"


DEFAULT_VERSION = ApiVersion.V2022_07_18_preview

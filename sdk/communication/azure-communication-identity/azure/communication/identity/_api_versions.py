# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum


class ApiVersion(str, Enum):
    V2021_03_07 = "2021-03-07"
    V2021_10_31_preview = "2021-10-31-preview"


DEFAULT_VERSION = ApiVersion.V2021_10_31_preview

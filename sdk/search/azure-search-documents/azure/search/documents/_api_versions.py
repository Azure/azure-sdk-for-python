# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum

class ApiVersion(str, Enum):
    #: this is the default version
    V2020_06_30 = "2020-06-30"
    V2021_04_30_preview = "2021-04-30-Preview"

DEFAULT_VERSION = ApiVersion.V2021_04_30_preview

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum

class ApiVersion(str, Enum):
    #: this is the default version
    V2020_06_30 = "2020-06-30"

DEFAULT_VERSION = ApiVersion.V2020_06_30

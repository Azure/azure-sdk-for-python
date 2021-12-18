# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum


class ApiVersion(str, Enum):
    V2021_05 = "2021-05"
    V2017_04 = "2017-04"


DEFAULT_VERSION = ApiVersion.V2021_05

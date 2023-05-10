# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2023_01_15_PREVIEW = "2023-01-15-preview"

DEFAULT_VERSION = ApiVersion.V2023_01_15_PREVIEW.value

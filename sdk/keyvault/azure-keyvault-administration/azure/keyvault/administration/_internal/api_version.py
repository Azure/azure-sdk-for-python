# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta

# pylint:disable=enum-must-be-uppercase
class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Key Vault API versions supported by this package"""

    #: this is the default version
    V7_2_preview = "7.2-preview"


DEFAULT_VERSION = ApiVersion.V7_2_preview

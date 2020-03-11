# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from ._enums import KeyCurveName, KeyOperation, KeyType
from ._shared.multi_api import ApiVersion
from ._models import DeletedKey, JsonWebKey, KeyProperties, KeyVaultKey
from ._client import KeyClient

__all__ = [
    "ApiVersion",
    "KeyClient",
    "JsonWebKey",
    "KeyVaultKey",
    "KeyCurveName",
    "KeyOperation",
    "KeyType",
    "DeletedKey",
    "KeyProperties",
]

from ._version import VERSION
__version__ = VERSION

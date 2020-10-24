# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from ._enums import KeyCurveName, KeyOperation, KeyType
from ._parse_id import parse_key_vault_key_id
from ._shared.client_base import ApiVersion
from ._shared import KeyVaultResourceId
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
    "parse_key_vault_key_id",
    "KeyVaultResourceId"
]

from ._version import VERSION
__version__ = VERSION

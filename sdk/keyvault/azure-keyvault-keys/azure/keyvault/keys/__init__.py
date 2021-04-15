# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from ._enums import KeyCurveName, KeyOperation, KeyType
from ._shared.client_base import ApiVersion
from ._shared import KeyVaultResourceId
from ._models import (
    DeletedKey,
    JsonWebKey,
    KeyProperties,
    KeyReleasePolicy,
    KeyReleaseResult,
    KeyVaultKey,
)
from ._client import KeyClient

__all__ = [
    "ApiVersion",
    "KeyClient",
    "JsonWebKey",
    "KeyVaultKey",
    "KeyVaultKeyIdentifier",
    "KeyCurveName",
    "KeyOperation",
    "KeyType",
    "DeletedKey",
    "KeyProperties",
    "KeyReleasePolicy",
    "KeyReleaseResult",
    "parse_key_vault_key_id",
    "KeyVaultResourceId"
]

from ._version import VERSION
__version__ = VERSION

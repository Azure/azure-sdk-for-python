# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from ._enums import KeyCurveName, KeyExportEncryptionAlgorithm, KeyOperation, KeyType
from ._shared.client_base import ApiVersion
from ._models import (
    DeletedKey,
    JsonWebKey,
    KeyProperties,
    KeyReleasePolicy,
    KeyVaultKey,
    KeyVaultKeyIdentifier,
    RandomBytes,
    ReleaseKeyResult,
)
from ._client import KeyClient

__all__ = [
    "ApiVersion",
    "KeyClient",
    "JsonWebKey",
    "KeyVaultKey",
    "KeyVaultKeyIdentifier",
    "KeyCurveName",
    "KeyExportEncryptionAlgorithm",
    "KeyOperation",
    "KeyType",
    "DeletedKey",
    "KeyProperties",
    "KeyReleasePolicy",
    "RandomBytes",
    "ReleaseKeyResult",
]

from ._version import VERSION

__version__ = VERSION

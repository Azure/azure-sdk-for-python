# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._models import DeletedSecret, KeyVaultSecret, SecretProperties
from ._parse_id import parse_key_vault_secret_id
from ._shared import KeyVaultResourceId
from ._shared.client_base import ApiVersion
from ._client import SecretClient

__all__ = [
    "ApiVersion",
    "SecretClient",
    "KeyVaultSecret",
    "SecretProperties",
    "DeletedSecret",
    "parse_key_vault_secret_id",
    "KeyVaultResourceId"
]

from ._version import VERSION
__version__ = VERSION

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._models import DeletedSecret, KeyVaultSecret, SecretProperties
from ._client import SecretClient

__all__ = ["SecretClient", "KeyVaultSecret", "SecretProperties", "DeletedSecret"]

from ._version import VERSION
__version__ = VERSION

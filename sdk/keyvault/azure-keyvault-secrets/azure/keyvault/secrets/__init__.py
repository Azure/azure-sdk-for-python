# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._client import SecretClient
from ._models import Secret, SecretAttributes, DeletedSecret

__all__ = ["SecretClient"]

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .exceptions import AuthenticationError
from .credentials import ClientSecretCredential, TokenCredentialChain

__all__ = ["AuthenticationError", "ClientSecretCredential", "TokenCredentialChain"]

try:
    from .aio import AsyncClientSecretCredential, AsyncTokenCredentialChain

    __all__.extend(["AsyncClientSecretCredential", "AsyncTokenCredentialChain"])
except SyntaxError:
    pass

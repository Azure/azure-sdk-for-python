# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .exceptions import AuthenticationError
from .credentials import (
    CertificateCredential,
    ClientSecretCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    TokenCredentialChain,
)

__all__ = [
    "AuthenticationError",
    "CertificateCredential",
    "ClientSecretCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "TokenCredentialChain",
]

try:
    from .aio import (
        AsyncCertificateCredential,
        AsyncClientSecretCredential,
        AsyncEnvironmentCredential,
        AsyncManagedIdentityCredential,
        AsyncTokenCredentialChain,
    )

    __all__.extend(
        [
            "AsyncCertificateCredential",
            "AsyncClientSecretCredential",
            "AsyncEnvironmentCredential",
            "AsyncManagedIdentityCredential",
            "AsyncTokenCredentialChain",
        ]
    )
except SyntaxError:
    pass

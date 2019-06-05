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
    ImdsCredential,
    ManagedIdentityCredential,
    MsiCredential,
    TokenCredentialChain,
)

__all__ = [
    "AuthenticationError",
    "CertificateCredential",
    "ClientSecretCredential",
    "EnvironmentCredential",
    "ImdsCredential",
    "ManagedIdentityCredential",
    "MsiCredential",
    "TokenCredentialChain",
]

try:
    from .aio import (
        AsyncCertificateCredential,
        AsyncClientSecretCredential,
        AsyncEnvironmentCredential,
        AsyncImdsCredential,
        AsyncManagedIdentityCredential,
        AsyncMsiCredential,
        AsyncTokenCredentialChain,
    )

    __all__.extend(
        [
            "AsyncCertificateCredential",
            "AsyncClientSecretCredential",
            "AsyncEnvironmentCredential",
            "AsyncImdsCredential",
            "AsyncManagedIdentityCredential",
            "AsyncMsiCredential",
            "AsyncTokenCredentialChain",
        ]
    )
except SyntaxError:
    pass

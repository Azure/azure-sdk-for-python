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


class DefaultAzureCredential(TokenCredentialChain):
    """default credential is environment followed by MSI/IMDS"""

    def __init__(self, **kwargs):
        super(DefaultAzureCredential, self).__init__(
            EnvironmentCredential(**kwargs), ManagedIdentityCredential(**kwargs)
        )


__all__ = [
    "AuthenticationError",
    "CertificateCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "TokenCredentialChain",
]

try:
    from .aio import (
        AsyncCertificateCredential,
        AsyncClientSecretCredential,
        AsyncDefaultAzureCredential,
        AsyncEnvironmentCredential,
        AsyncManagedIdentityCredential,
        AsyncTokenCredentialChain,
    )

    __all__.extend(
        [
            "AsyncCertificateCredential",
            "AsyncClientSecretCredential",
            "AsyncDefaultAzureCredential",
            "AsyncEnvironmentCredential",
            "AsyncManagedIdentityCredential",
            "AsyncTokenCredentialChain",
        ]
    )
except (ImportError, SyntaxError):
    pass

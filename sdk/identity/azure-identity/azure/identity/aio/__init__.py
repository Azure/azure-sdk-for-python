# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ------------------------------------------------------------------------
from .credentials import (
    AsyncCertificateCredential,
    AsyncClientSecretCredential,
    AsyncEnvironmentCredential,
    AsyncManagedIdentityCredential,
    AsyncTokenCredentialChain,
)


class AsyncDefaultAzureCredential(AsyncTokenCredentialChain):
    """default credential is environment followed by MSI/IMDS"""

    def __init__(self, **kwargs):
        super().__init__(AsyncEnvironmentCredential(**kwargs), AsyncManagedIdentityCredential(**kwargs))


__all__ = [
    "AsyncCertificateCredential",
    "AsyncClientSecretCredential",
    "AsyncDefaultAzureCredential",
    "AsyncEnvironmentCredential",
    "AsyncManagedIdentityCredential",
    "AsyncTokenCredentialChain",
]

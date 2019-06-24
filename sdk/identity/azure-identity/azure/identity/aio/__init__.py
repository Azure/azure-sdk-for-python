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
    AsyncChainedTokenCredential,
)


class AsyncDefaultAzureCredential(AsyncChainedTokenCredential):
    """
    A default credential capable of handling most Azure SDK authentication scenarios.

    When environment variable configuration is present, it authenticates as a service principal
    using :class:`identity.aio.AsyncEnvironmentCredential`.

    When environment configuration is not present, it authenticates with a managed identity
    using :class:`identity.aio.AsyncManagedIdentityCredential`.
    """

    def __init__(self, **kwargs):
        super().__init__(AsyncEnvironmentCredential(**kwargs), AsyncManagedIdentityCredential(**kwargs))


__all__ = [
    "AsyncCertificateCredential",
    "AsyncClientSecretCredential",
    "AsyncDefaultAzureCredential",
    "AsyncEnvironmentCredential",
    "AsyncManagedIdentityCredential",
    "AsyncChainedTokenCredential",
]

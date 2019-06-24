# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ------------------------------------------------------------------------
from .credentials import (
    CertificateCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
)


class DefaultAzureCredential(ChainedTokenCredential):
    """
    A default credential capable of handling most Azure SDK authentication scenarios.

    When environment variable configuration is present, it authenticates as a service principal
    using :class:`identity.aio.EnvironmentCredential`.

    When environment configuration is not present, it authenticates with a managed identity
    using :class:`identity.aio.ManagedIdentityCredential`.
    """

    def __init__(self, **kwargs):
        super().__init__(EnvironmentCredential(**kwargs), ManagedIdentityCredential(**kwargs))


__all__ = [
    "CertificateCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "ChainedTokenCredential",
]

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._browser_auth import InteractiveBrowserCredential
from .credentials import (
    CertificateCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    DeviceCodeCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
    UsernamePasswordCredential,
)


class DefaultAzureCredential(ChainedTokenCredential):
    """
    A default credential capable of handling most Azure SDK authentication scenarios.

    When environment variable configuration is present, it authenticates as a service principal using
    :class:`azure.identity.EnvironmentCredential`.

    When environment configuration is not present, it authenticates with a managed identity using
    :class:`azure.identity.ManagedIdentityCredential`.

    On Windows, when environment variable configuration and managed identity are unavailable, it finally
    attempts to authenticate with a token from the cache shared by Microsoft applications using
    :class:`azure.identity.SharedTokenCacheCredential`.
    """

    def __init__(self, **kwargs):
        credentials = [EnvironmentCredential(**kwargs), ManagedIdentityCredential(**kwargs)]
        if SharedTokenCacheCredential.supported():
            credentials.append(SharedTokenCacheCredential(**kwargs))

        super(DefaultAzureCredential, self).__init__(*credentials)


__all__ = [
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "DeviceCodeCredential",
    "EnvironmentCredential",
    "InteractiveBrowserCredential",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
    "UsernamePasswordCredential",
]

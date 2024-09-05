# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.credentials_async import AsyncSupportsTokenInfo, AsyncTokenCredential
from azure.identity.aio import (
    AuthorizationCodeCredential,
    CertificateCredential,
    ClientSecretCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    OnBehalfOfCredential,
    SharedTokenCacheCredential,
    VisualStudioCodeCredential,
    WorkloadIdentityCredential,
    DefaultAzureCredential,
    ChainedTokenCredential,
    AzureCliCredential,
    AzurePowerShellCredential,
    AzureDeveloperCliCredential,
    AzurePipelinesCredential,
)


def test_credential_is_async_token_credential():
    assert isinstance(AuthorizationCodeCredential, AsyncTokenCredential)
    assert isinstance(CertificateCredential, AsyncTokenCredential)
    assert isinstance(ClientSecretCredential, AsyncTokenCredential)
    assert isinstance(EnvironmentCredential, AsyncTokenCredential)
    assert isinstance(ManagedIdentityCredential, AsyncTokenCredential)
    assert isinstance(OnBehalfOfCredential, AsyncTokenCredential)
    assert isinstance(SharedTokenCacheCredential, AsyncTokenCredential)
    assert isinstance(VisualStudioCodeCredential, AsyncTokenCredential)
    assert isinstance(WorkloadIdentityCredential, AsyncTokenCredential)
    assert isinstance(DefaultAzureCredential, AsyncTokenCredential)
    assert isinstance(ChainedTokenCredential, AsyncTokenCredential)
    assert isinstance(AzureCliCredential, AsyncTokenCredential)
    assert isinstance(AzurePowerShellCredential, AsyncTokenCredential)
    assert isinstance(AzureDeveloperCliCredential, AsyncTokenCredential)
    assert isinstance(AzurePipelinesCredential, AsyncTokenCredential)


def test_credential_is_async_supports_token_info():
    assert isinstance(AuthorizationCodeCredential, AsyncSupportsTokenInfo)
    assert isinstance(CertificateCredential, AsyncSupportsTokenInfo)
    assert isinstance(ClientSecretCredential, AsyncSupportsTokenInfo)
    assert isinstance(EnvironmentCredential, AsyncSupportsTokenInfo)
    assert isinstance(ManagedIdentityCredential, AsyncSupportsTokenInfo)
    assert isinstance(OnBehalfOfCredential, AsyncSupportsTokenInfo)
    assert isinstance(SharedTokenCacheCredential, AsyncSupportsTokenInfo)
    assert isinstance(VisualStudioCodeCredential, AsyncSupportsTokenInfo)
    assert isinstance(WorkloadIdentityCredential, AsyncSupportsTokenInfo)
    assert isinstance(DefaultAzureCredential, AsyncSupportsTokenInfo)
    assert isinstance(ChainedTokenCredential, AsyncSupportsTokenInfo)
    assert isinstance(AzureCliCredential, AsyncSupportsTokenInfo)
    assert isinstance(AzurePowerShellCredential, AsyncSupportsTokenInfo)
    assert isinstance(AzureDeveloperCliCredential, AsyncSupportsTokenInfo)
    assert isinstance(AzurePipelinesCredential, AsyncSupportsTokenInfo)

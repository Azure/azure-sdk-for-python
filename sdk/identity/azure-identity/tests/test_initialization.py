# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys

from azure.core.credentials import SupportsTokenInfo, TokenCredential
from azure.identity import (
    AuthorizationCodeCredential,
    CertificateCredential,
    ClientSecretCredential,
    DeviceCodeCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
    ManagedIdentityCredential,
    OnBehalfOfCredential,
    SharedTokenCacheCredential,
    UsernamePasswordCredential,
    VisualStudioCodeCredential,
    WorkloadIdentityCredential,
    DefaultAzureCredential,
    ChainedTokenCredential,
    AzureCliCredential,
    AzurePowerShellCredential,
    AzureDeveloperCliCredential,
    AzurePipelinesCredential,
)
import pytest


def test_credential_is_token_credential():
    assert isinstance(AuthorizationCodeCredential, TokenCredential)
    assert isinstance(CertificateCredential, TokenCredential)
    assert isinstance(ClientSecretCredential, TokenCredential)
    assert isinstance(DeviceCodeCredential, TokenCredential)
    assert isinstance(EnvironmentCredential, TokenCredential)
    assert isinstance(InteractiveBrowserCredential, TokenCredential)
    assert isinstance(ManagedIdentityCredential, TokenCredential)
    assert isinstance(OnBehalfOfCredential, TokenCredential)
    assert isinstance(SharedTokenCacheCredential, TokenCredential)
    assert isinstance(UsernamePasswordCredential, TokenCredential)
    assert isinstance(VisualStudioCodeCredential, TokenCredential)
    assert isinstance(WorkloadIdentityCredential, TokenCredential)
    assert isinstance(DefaultAzureCredential, TokenCredential)
    assert isinstance(ChainedTokenCredential, TokenCredential)
    assert isinstance(AzureCliCredential, TokenCredential)
    assert isinstance(AzurePowerShellCredential, TokenCredential)
    assert isinstance(AzureDeveloperCliCredential, TokenCredential)
    assert isinstance(AzurePipelinesCredential, TokenCredential)


@pytest.mark.skipif(
    sys.version_info < (3, 9),
    reason="isinstance check doesn't seem to work when the Protocol subclasses ContextManager in Python <=3.8",
)
def test_credential_is_supports_token_info():
    assert isinstance(AuthorizationCodeCredential, SupportsTokenInfo)
    assert isinstance(CertificateCredential, SupportsTokenInfo)
    assert isinstance(ClientSecretCredential, SupportsTokenInfo)
    assert isinstance(DeviceCodeCredential, SupportsTokenInfo)
    assert isinstance(EnvironmentCredential, SupportsTokenInfo)
    assert isinstance(InteractiveBrowserCredential, SupportsTokenInfo)
    assert isinstance(ManagedIdentityCredential, SupportsTokenInfo)
    assert isinstance(OnBehalfOfCredential, SupportsTokenInfo)
    assert isinstance(SharedTokenCacheCredential, SupportsTokenInfo)
    assert isinstance(UsernamePasswordCredential, SupportsTokenInfo)
    assert isinstance(VisualStudioCodeCredential, SupportsTokenInfo)
    assert isinstance(WorkloadIdentityCredential, SupportsTokenInfo)
    assert isinstance(DefaultAzureCredential, SupportsTokenInfo)
    assert isinstance(ChainedTokenCredential, SupportsTokenInfo)
    assert isinstance(AzureCliCredential, SupportsTokenInfo)
    assert isinstance(AzurePowerShellCredential, SupportsTokenInfo)
    assert isinstance(AzureDeveloperCliCredential, SupportsTokenInfo)
    assert isinstance(AzurePipelinesCredential, SupportsTokenInfo)

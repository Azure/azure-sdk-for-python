# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .authorization_code import AuthorizationCodeCredential
from .azure_powershell import AzurePowerShellCredential
from .chained import ChainedTokenCredential
from .default import DefaultAzureCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .on_behalf_of import OnBehalfOfCredential
from .certificate import CertificateCredential
from .client_secret import ClientSecretCredential
from .shared_cache import SharedTokenCacheCredential
from .azure_cli import AzureCliCredential
from .vscode import VisualStudioCodeCredential
from .client_assertion import ClientAssertionCredential


__all__ = [
    "AuthorizationCodeCredential",
    "AzureCliCredential",
    "AzurePowerShellCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "OnBehalfOfCredential",
    "SharedTokenCacheCredential",
    "VisualStudioCodeCredential",
    "ClientAssertionCredential",
]

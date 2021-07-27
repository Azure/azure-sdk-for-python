# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .application import AzureApplicationCredential
from .authorization_code import AuthorizationCodeCredential
from .azure_powershell import AzurePowerShellCredential
from .chained import ChainedTokenCredential
from .default import DefaultAzureCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .certificate import CertificateCredential
from .client_secret import ClientSecretCredential
from .shared_cache import SharedTokenCacheCredential
from .azure_cli import AzureCliCredential
from .vscode import VisualStudioCodeCredential


__all__ = [
    "AuthorizationCodeCredential",
    "AzureApplicationCredential",
    "AzureCliCredential",
    "AzurePowerShellCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
    "VisualStudioCodeCredential",
]

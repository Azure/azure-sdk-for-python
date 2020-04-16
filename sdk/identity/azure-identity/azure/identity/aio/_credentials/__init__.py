# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from .authorization_code import AuthorizationCodeCredential
from .chained import ChainedTokenCredential
from .default import DefaultAzureCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .client_credential import CertificateCredential, ClientSecretCredential
from .shared_cache import SharedTokenCacheCredential
from .azure_cli import AzureCliCredential

__all__ = [
    "AuthorizationCodeCredential",
    "AzureCliCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "EnvironmentCredential",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
]

if sys.platform.startswith('win'):
    from .win_vscode_credential import WinVSCodeCredential as VSCodeCredential
    __all__.extend([
        'VSCodeCredential',
    ])
elif sys.platform.startswith('darwin'):
    from .macos_vscode_credential import MacOSVSCodeCredential as VSCodeCredential
    __all__.extend([
        'VSCodeCredential',
    ])
else:
    try:
        from .linux_vscode_credential import LinuxVSCodeCredential as VSCodeCredential
        __all__.extend([
            'VSCodeCredential',
        ])
    except ImportError: #pygobject is not installed
        pass

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
from .authorization_code import AuthorizationCodeCredential
from .browser import InteractiveBrowserCredential
from .chained import ChainedTokenCredential
from .client_credential import CertificateCredential, ClientSecretCredential
from .default import DefaultAzureCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .shared_cache import SharedTokenCacheCredential
from .azure_cli import AzureCliCredential
from .user import DeviceCodeCredential, UsernamePasswordCredential

__all__ = [
    "AuthorizationCodeCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "DefaultAzureCredential",
    "DeviceCodeCredential",
    "EnvironmentCredential",
    "InteractiveBrowserCredential",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
    "AzureCliCredential",
    "UsernamePasswordCredential",
]

if sys.platform.startswith('win'):
    # pylint:disable=unused-import
    from .win_vscode_credential import WinVSCodeCredential as VSCodeCredential
    __all__.extend([
        'VSCodeCredential',
    ])
elif sys.platform.startswith('darwin'):
    # pylint:disable=unused-import
    from .macos_vscode_credential import MacOSVSCodeCredential as VSCodeCredential
    __all__.extend([
        'VSCodeCredential',
    ])
else:
    try:
        # pylint:disable=unused-import
        from .linux_vscode_credential import LinuxVSCodeCredential as VSCodeCredential
        __all__.extend([
            'VSCodeCredential',
        ])
    except ImportError: #pygobject is not installed
        pass

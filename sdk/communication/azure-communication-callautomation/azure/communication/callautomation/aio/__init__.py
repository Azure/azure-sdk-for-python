# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import warnings

from ._call_automation_client_async import CallAutomationClient
from ._call_connection_client_async import CallConnectionClient

__all__ = [
    "CallAutomationClient",
    "CallConnectionClient"
]

def __getattr__(name):
    if name == 'CommunicationTokenCredential':
        warnings.warn(
            "CommunicationTokenCredential should not be used with CallAutomation.",
            DeprecationWarning
        )
        from .._shared.user_credential_async import CommunicationTokenCredential
        return CommunicationTokenCredential
    raise AttributeError(f"module 'azure.communication.callautomation' has no attribute {name}")

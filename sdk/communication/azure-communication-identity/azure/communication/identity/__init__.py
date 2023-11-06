# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import warnings
from ._communication_identity_client import CommunicationIdentityClient
from ._generated.models import CommunicationTokenScope

from ._shared.models import (
    CommunicationCloudEnvironment,
    CommunicationIdentifier,
    CommunicationIdentifierKind,
    CommunicationUserIdentifier,
    CommunicationUserProperties,
    identifier_from_raw_id,
    MicrosoftTeamsUserIdentifier,
    MicrosoftTeamsUserProperties,
    PhoneNumberIdentifier,
    PhoneNumberProperties,
    UnknownIdentifier,
)

__all__ = [
    "CommunicationIdentityClient",
    # from _identity
    "CommunicationTokenScope",
    # from _shared
    "CommunicationCloudEnvironment",
    "CommunicationIdentifier",
    "CommunicationIdentifierKind",
    "CommunicationUserIdentifier",
    "CommunicationUserProperties",
    "identifier_from_raw_id",
    "MicrosoftTeamsUserIdentifier",
    "MicrosoftTeamsUserProperties",
    "PhoneNumberIdentifier",
    "PhoneNumberProperties",
    "UnknownIdentifier",
]

def __getattr__(name):
    if name == 'MicrosoftBotProperties':
        warnings.warn(f"{name} is deprecated and should not be used.", DeprecationWarning)
        from ._shared.models  import _MicrosoftBotProperties
        return _MicrosoftBotProperties
    if name == 'MicrosoftBotIdentifier':
        warnings.warn(f"{name} is deprecated and should not be used.", DeprecationWarning)
        from ._shared.models  import _MicrosoftBotIdentifier
        return _MicrosoftBotIdentifier
    raise AttributeError(f"module 'azure.communication.identity' has no attribute {name}")

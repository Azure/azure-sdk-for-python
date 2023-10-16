# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import warnings
from ._rooms_client import RoomsClient
from ._models import (
    CommunicationRoom,
    RoomParticipant,
    ParticipantRole
)
from ._shared.models import (
    CommunicationIdentifier,
    CommunicationIdentifierKind,
    CommunicationCloudEnvironment,
    CommunicationUserIdentifier,
    CommunicationUserProperties,
    PhoneNumberIdentifier,
    PhoneNumberProperties,
    UnknownIdentifier,
    MicrosoftTeamsUserIdentifier,
    MicrosoftTeamsUserProperties
)
from ._version import VERSION

__all__ = [
    'CommunicationRoom',
    'ParticipantRole',
    'RoomsClient',
    'RoomParticipant',
    'CommunicationIdentifier',
    'CommunicationIdentifierKind',
    'CommunicationCloudEnvironment',
    'CommunicationUserIdentifier',
    'CommunicationUserProperties',
    'PhoneNumberIdentifier',
    'PhoneNumberProperties',
    'UnknownIdentifier',
    'MicrosoftTeamsUserIdentifier',
    'MicrosoftTeamsUserProperties'
]

__VERSION__ = VERSION

def __getattr__(name):
    if name == 'MicrosoftBotProperties':
        warnings.warn(f"{name} is deprecated and should not be used.", DeprecationWarning)
        from ._shared.models  import _MicrosoftBotProperties
        return _MicrosoftBotProperties
    if name == 'MicrosoftBotIdentifier':
        warnings.warn(f"{name} is deprecated and should not be used.", DeprecationWarning)
        from ._shared.models  import _MicrosoftBotIdentifier
        return _MicrosoftBotIdentifier
    raise AttributeError(f"module 'azure.communication.rooms' has no attribute {name}")

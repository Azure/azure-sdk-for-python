# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
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
    MicrosoftTeamsUserProperties,
    MicrosoftBotIdentifier,
    MicrosoftBotProperties
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
    'MicrosoftTeamsUserProperties',
    'MicrosoftBotIdentifier',
    'MicrosoftBotProperties'
]

__VERSION__ = VERSION

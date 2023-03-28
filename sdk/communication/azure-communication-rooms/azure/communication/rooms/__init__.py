# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._rooms_client import RoomsClient

from ._generated.models import (
    ParticipantRole,
)
from ._models import (
    CommunicationRoom,
    RoomParticipant,
    InvitedRoomParticipant,
    UpsertParticipantsResult,
    RemoveParticipantsResult
)

from ._shared.models import (
    CommunicationIdentifier,
    CommunicationUserIdentifier,
    identifier_from_raw_id
)

from ._version import VERSION

__all__ = [
    'CommunicationRoom',
    'ParticipantRole',
    'ParticipantsCollection',
    'RoomsClient',
    'RoomParticipant',
    'RoomsCollection',
    "identifier_from_raw_id",
    "CommunicationIdentifier",
    "CommunicationUserIdentifier",
    "InvitedRoomParticipant",
    "UpsertParticipantsResult",
    "RemoveParticipantsResult"
]

__VERSION__ = VERSION

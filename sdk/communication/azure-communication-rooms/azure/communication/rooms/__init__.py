# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._rooms_client import RoomsClient
from ._generated.models._enums import (
    RoomJoinPolicy,
    RoleType
)
from ._models import (
    CommunicationRoom,
    RoomParticipant,
    ParticipantsCollection
)
from ._version import VERSION

__all__ = [
    'CommunicationRoom',
    'RoomsClient',
    'RoomParticipant',
    'RoomJoinPolicy',
    'RoleType',
    'ParticipantsCollection'
]

__VERSION__ = VERSION

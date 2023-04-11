# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._rooms_client import RoomsClient

from ._generated.models import (
    ParticipantRole,
    CommunicationRoom
)
from ._models import (
    RoomParticipant,
    UpsertParticipantsResult,
    RemoveParticipantsResult
)

from ._version import VERSION

__all__ = [
    'CommunicationRoom',
    'ParticipantRole',
    'RoomsClient',
    'RoomParticipant',
    "UpsertParticipantsResult",
    "RemoveParticipantsResult"
]

__VERSION__ = VERSION

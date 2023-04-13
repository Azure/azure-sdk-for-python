# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import Any, Union
from .._generated.models import (
    ParticipantRole
)
from .._shared.models import (
    CommunicationIdentifier,
    identifier_from_raw_id
)

class RoomParticipant():
    """A participant of the room.

    All required parameters must be populated in order to send to Azure.

    :ivar communication_identifier: Communication Identifier.
    :vartype communication_identifier:~azure.communication.rooms._shared.models.CommunicationIdentifier
    :ivar role: Role Name.
    :vartype role: Union[str, ParticipantRole]
    """
    def __init__(self,
                *,
                communication_identifier: CommunicationIdentifier,
                role: Union[str, ParticipantRole] = ParticipantRole.ATTENDEE,
                **kwargs: Any
    ) -> None:
        """
        :keyword communication_identifier: Raw ID representation of the communication identifier. Please refer to the
         following document for additional information on Raw ID. :code:`<br>`
         https://learn.microsoft.com/azure/communication-services/concepts/identifiers?pivots=programming-language-rest#raw-id-representation.
        :keyword role: The role of a room participant. The default value is Attendee. Known
         values are: "Presenter", "Attendee", and "Consumer".
        :paramtype role: str or ~azure.communication.rooms.models.ParticipantRole
        """
        super().__init__(**kwargs)
        self.communication_identifier = communication_identifier
        self.role = role or ParticipantRole.ATTENDEE


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    @classmethod
    def _from_generated(cls, room_participant):
        return cls(
            communication_identifier=identifier_from_raw_id(room_participant.raw_id),
            role=room_participant.role
        )

class UpsertParticipantsResult():
    def __init__(self):
        # empty constructor
        pass

class RemoveParticipantsResult():
    def __init__(self):
        # empty constructor
        pass

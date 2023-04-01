# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import Any, Optional, Union
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

    :ivar communication_identifier: Identifies a participant in Azure Communication services. A
    participant is, for example, an Azure communication user. This model must be interpreted as a
    union: Apart from rawId, at most one further property may be set. Required.
    :vartype communication_identifier:
    ~azure.communication.rooms._shared.models.CommunicationIdentifier
    :ivar role: Role Name.
    :vartype role: Union[str, ParticipantRole]
    """
    def __init__(self, *, raw_id: str, role: Union[str, ParticipantRole], **kwargs: Any) -> None:
        """
        :keyword raw_id: Raw ID representation of the communication identifier. Please refer to the
         following document for additional information on Raw ID. :code:`<br>`
         https://learn.microsoft.com/azure/communication-services/concepts/identifiers?pivots=programming-language-rest#raw-id-representation.
         Required.
        :paramtype raw_id: str
        :keyword role: The role of a room participant. The default value is Attendee. Required. Known
         values are: "Presenter", "Attendee", and "Consumer".
        :paramtype role: str or ~azure.communication.rooms.models.ParticipantRole
        """
        super().__init__(**kwargs)
        self.raw_id = raw_id
        self.role = role
        self.communication_identifier = identifier_from_raw_id(self.raw_id)


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    @classmethod
    def _from_generated(cls, room_participant):
        return cls(
            raw_id=room_participant.raw_id,
            role=room_participant.role
        )

class InvitedRoomParticipant():
    """An invited participant of the room.

    All required parameters must be populated in order to send to Azure.

    :ivar communication_identifier: Identifies a participant in Azure Communication services. A
    participant is, for example, an Azure communication user. This model must be interpreted as a
    union: Apart from rawId, at most one further property may be set. Required.
    :vartype communication_identifier:
    ~azure.communication.rooms._shared.models.CommunicationIdentifier
    :ivar role: Participant Role.
    :vartype role: Optional[Union[str, ParticipantRole]
    """

    def __init__(self, *, communication_identifier: CommunicationIdentifier, role: Optional[Union[str, ParticipantRole]], **kwargs: Any) -> None:
        """
        :keyword raw_id: Raw ID representation of the communication identifier. Please refer to the
         following document for additional information on Raw ID. :code:`<br>`
         https://learn.microsoft.com/azure/communication-services/concepts/identifiers?pivots=programming-language-rest#raw-id-representation.
         Required.
        :paramtype raw_id: str
        :keyword role: The role of a room participant. The default value is Attendee. Required. Known
         values are: "Presenter", "Attendee", and "Consumer".
        :paramtype role: Optional. str or ~azure.communication.rooms.models.ParticipantRole
        """
        super().__init__(**kwargs)
        self.communication_identifier = communication_identifier
        self.role = role

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

class UpsertParticipantsResult():
    def __init__(self):
        # empty constructor
        pass

class RemoveParticipantsResult():
    def __init__(self):
        # empty constructor
        pass

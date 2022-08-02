# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import Optional, List, Union

from azure.core.exceptions import DeserializationError
from .._generated.models import (
    RoomParticipant as RoomParticipantInternal,
    CommunicationIdentifierModel,
    CommunicationUserIdentifierModel,
    RoomJoinPolicy,
    RoleType as ParticipantRole
)
from .._generated import _serialization
from .._generated.models import RoomModel
from .._shared.models import (
    CommunicationIdentifier,
    CommunicationIdentifierKind,
    CommunicationUserIdentifier,
    UnknownIdentifier
)


class CommunicationRoom(_serialization.Model):
    """The response object from rooms service.

    :ivar id: Unique identifier of a room. This id is server generated.
    :vartype id: str
    :ivar created_on: The timestamp when the room was created at the server. The timestamp
     is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype created_on: ~datetime
    :ivar valid_from: The timestamp from when the room is open for joining. The timestamp is in
     RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype valid_from: ~datetime
    :ivar valid_until: The timestamp from when the room can no longer be joined. The timestamp is
     in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype valid_until: ~datetime
    :ivar room_join_policy: The join policy of the room.
    :vartype room_join_policy: ~azure.communication.rooms.RoomJoinPolicy
    :ivar participants: Collection of room participants.
    :vartype participants: Optional[list[~azure.communication.rooms.RoomParticipant]]
    """

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'created_on': {'key': 'createdOn', 'type': 'iso-8601'},
        'valid_from': {'key': 'validFrom', 'type': 'iso-8601'},
        'valid_until': {'key': 'validUntil', 'type': 'iso-8601'},
        'participants': {'key': 'participants', 'type': '[RoomParticipant]'},
    }

    def __init__(
        self,
        *,
        id: str, #pylint: disable=redefined-builtin
        created_on: datetime,
        valid_from: datetime,
        valid_until: datetime,
        room_join_policy: RoomJoinPolicy,
        participants: Optional[List['RoomParticipant']] = None,
        **kwargs
    ):
        """
        :keyword id: Unique identifier of a room. This id is server generated.
        :paramtype id: str
        :keyword created_on: The timestamp when the room was created at the server. The
         timestamp is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
        :paramtype created_on: ~datetime
        :keyword valid_from: The timestamp from when the room is open for joining. The timestamp is in
         RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
        :paramtype valid_from: ~datetime
        :keyword valid_until: The timestamp from when the room can no longer be joined. The timestamp
         is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
        :paramtype valid_until: ~datetime
        :keyword room_join_policy: The join policy of the room.
        :paramtype room_join_policy: ~azure.communication.rooms.RoomJoinPolicy
        :keyword participants: Collection of room participants.
        :paramtype participants: Optional[list[~azure.communication.rooms.RoomParticipant]]
        """
        super(CommunicationRoom, self).__init__(**kwargs)
        self.id = id
        self.created_on = created_on
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.room_join_policy = room_join_policy
        self.participants = participants

    @classmethod
    def from_room_response(cls, get_room_response: RoomModel,
            **kwargs
    ) -> 'CommunicationRoom':
        """Create CommunicationRoom from the internal RoomModel.
        :param RoomModel get_room_response:
            Response from get_room API.
        :returns: Instance of CommunicationRoom.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        """

        return cls(
            id=get_room_response.id,
            created_on=get_room_response.created_date_time,
            valid_from=get_room_response.valid_from,
            valid_until=get_room_response.valid_until,
            room_join_policy=get_room_response.room_join_policy,
            participants=[RoomParticipant.from_room_participant_internal(p) for p in get_room_response.participants],
            **kwargs
        )

class RoomParticipant(_serialization.Model):
    """A participant of the room.

    All required parameters must be populated in order to send to Azure.

    :ivar communication_identifier: Identifies a participant in Azure Communication services. A
    participant is, for example, an Azure communication user. This model must be interpreted as a
    union: Apart from rawId, at most one further property may be set. Required.
    :vartype communication_identifier:
    ~azure.communication.rooms._shared.models.CommunicationIdentifier
    :ivar role: Role Name.
    :vartype role: str or ~azure.communication.rooms.ParticipantRole
    """

    _validation = {
        "communication_identifier": {"required": True},
    }

    _attribute_map = {
        "communication_identifier": {"key": "communicationIdentifier", "type": "CommunicationIdentifier"},
        "role": {"key": "role", "type": "Optional[Union[str, ParticipantRole]"},
    }

    def __init__(
        self, communication_identifier: CommunicationIdentifier, role: Optional[Union[str, ParticipantRole]] = None, **kwargs
    ):
        """
        :param communication_identifier: Identifies a participant in Azure Communication services. A
         participant is, for example, an Azure communication user. This model must be interpreted as a
         union: Apart from rawId, at most one further property may be set. Required.
        :type communication_identifier:
         ~azure.communication.rooms._shared.models.CommunicationIdentifier
        :param role: The Role of a room participant. Known values are: "Presenter", "Attendee", and
         "Consumer".
        :type role: str or ~azure.communication.rooms.ParticipantRole
        """
        super().__init__(**kwargs)
        self.communication_identifier = communication_identifier
        self.role = role

    @classmethod
    def from_room_participant_internal(cls, room_participant_internal: RoomParticipantInternal, **kwargs):
        return cls(
            communication_identifier=_CommunicationIdentifierConverter
                .to_communication_identifier(room_participant_internal.communication_identifier),
            role=room_participant_internal.role,
            **kwargs
        )

    def to_room_participant_internal(self):
        return RoomParticipantInternal(
            communication_identifier=_CommunicationIdentifierConverter
                .to_communication_identifier_model(self.communication_identifier),
            role=self.role
        )

class _CommunicationIdentifierConverter():
    @staticmethod
    def to_communication_identifier_model(communication_identifier: CommunicationIdentifier):
        if communication_identifier.kind == CommunicationIdentifierKind.COMMUNICATION_USER:
            return CommunicationIdentifierModel(
                communication_user=CommunicationUserIdentifierModel(
                    id=communication_identifier.properties['id']
                )
            )
        if communication_identifier.kind == CommunicationIdentifierKind.UNKNOWN:
            return CommunicationIdentifierModel(
                raw_id=communication_identifier.raw_id
            )

        raise TypeError('The type of communication identifier "{}" is not supported'
            .format(communication_identifier.kind))

    @staticmethod
    def to_communication_identifier(communication_identifier_model: CommunicationIdentifierModel):

        raw_id = communication_identifier_model.raw_id
        if not raw_id:
            raise DeserializationError('Property "{}" is required for identifier of type {}'
                .format('raw_id', type(communication_identifier_model).__name__))

        if isinstance(communication_identifier_model.communication_user, CommunicationUserIdentifierModel):
            return CommunicationUserIdentifier(
                communication_identifier_model.communication_user.id
            )

        return UnknownIdentifier(raw_id)


class ParticipantsCollection(_serialization.Model):
    """Collection of participants in a room.

    All required parameters must be populated in order to send to Azure.

    :ivar participants: Room Participants. Required.
    :vartype participants: list[~azure.communication.rooms.RoomParticipant]
    """

    _validation = {
        "participants": {"required": True, "readonly": True},
    }

    _attribute_map = {
        "participants": {"key": "participants", "type": "List[RoomParticipant]"},
    }

    def __init__(self, *, participants: List[RoomParticipantInternal], **kwargs):
        super().__init__(**kwargs)
        self.participants = [RoomParticipant.from_room_participant_internal(p) for p in participants]

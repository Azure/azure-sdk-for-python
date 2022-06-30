# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import Optional, List, Union

from .._generated.models import (
    RoomParticipant as RoomParticipantInternal,
    CommunicationIdentifierModel,
    CommunicationUserIdentifierModel,
    Role
)
from .._generated import _serialization
from .._shared.models import CommunicationUserIdentifier, UnknownIdentifier

from azure.core.exceptions import DeserializationError

class RoomModel(_serialization.Model):
    """The response object from rooms service.

    :ivar id: Unique identifier of a room. This id is server generated.
    :vartype id: str
    :ivar created_date_time: The timestamp when the room was created at the server. The timestamp
     is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype created_date_time: ~datetime
    :ivar valid_from: The timestamp from when the room is open for joining. The timestamp is in
     RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype valid_from: ~datetime
    :ivar valid_until: The timestamp from when the room can no longer be joined. The timestamp is
     in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype valid_until: ~datetime
    :ivar participants: Collection of identities invited to the room.
    :vartype participants: dict[str, any]
    """

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'created_date_time': {'key': 'createdDateTime', 'type': 'iso-8601'},
        'valid_from': {'key': 'validFrom', 'type': 'iso-8601'},
        'valid_until': {'key': 'validUntil', 'type': 'iso-8601'},
        'participants': {'key': 'participants', 'type': '[RoomParticipant]'},
    }

    def __init__(
        self,
        *,
        id=None, # type: Optional[str] pylint: disable=redefined-builtin
        created_date_time=None, # type: Optional[datetime]
        valid_from=None, # type: Optional[datetime]
        valid_until=None, # type: Optional[datetime]
        participants=None, # type: Optional[List[RoomParticipant]]
        **kwargs
    ):
        """
        :keyword id: Unique identifier of a room. This id is server generated.
        :paramtype id: str
        :keyword created_date_time: The timestamp when the room was created at the server. The
         timestamp is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
        :paramtype created_date_time: ~datetime
        :keyword valid_from: The timestamp from when the room is open for joining. The timestamp is in
         RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
        :paramtype valid_from: ~datetime
        :keyword valid_until: The timestamp from when the room can no longer be joined. The timestamp
         is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
        :paramtype valid_until: ~datetime
        :keyword participants: Collection of identities invited to the room.
        :paramtype participants: list[~azure.communication.rooms.models.RoomParticipant]
        """
        super(RoomModel, self).__init__(**kwargs)
        self.id = id
        self.created_date_time = created_date_time
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.participants = participants

    @classmethod
    def from_room_response(cls, get_room_response,  # type: RoomModel
            **kwargs  # type: Any
    ):
        # type: (...) -> RoomModel
        """Create CommunicationRoom from a RoomModel.
        :param RoomModel get_room_response:
            Response from get_room API.
        :returns: Instance of CommunicationRoom.
        :rtype: ~azure.communication.CommunicationRoom
        """

        return cls(
            id=get_room_response.id,
            created_date_time=get_room_response.created_date_time,
            valid_from=get_room_response.valid_from,
            valid_until=get_room_response.valid_until,
            participants=[RoomParticipant._from_room_participant_internal(p) for p in get_room_response.participants],
            **kwargs
        )

class RoomParticipant(_serialization.Model):
    """A participant of the room.

    All required parameters must be populated in order to send to Azure.

    :ivar communication_identifier: Identifies a participant in Azure Communication services. A
    participant is, for example, an Azure communication user. This model must be interpreted as a
    union: Apart from rawId, at most one further property may be set. Required.
    :vartype communication_identifier:
    ~azure.communication.rooms.models.CommunicationIdentifierModel
    :ivar role: Role Name.
    :vartype role: str
    """

    _validation = {
        "communication_identifier": {"required": True},
    }

    _attribute_map = {
        "communication_identifier": {"key": "communicationIdentifier", "type": "any"},
        "role": {"key": "role", "type": "str"},
    }

    def __init__(
        self, *, communication_identifier, role: Optional[Union[str, Role]] = None, **kwargs
    ):
        """
        :keyword communication_identifier: Identifies a participant in Azure Communication services. A
        participant is, for example, an Azure communication user. This model must be interpreted as a
        union: Apart from rawId, at most one further property may be set. Required.
        :paramtype communication_identifier:
        ~azure.communication.rooms.models.CommunicationIdentifierModel
        :keyword role: Role Name.
        :paramtype role: str
        """
        super().__init__(**kwargs)
        self.communication_identifier = communication_identifier
        self.role = role

    @classmethod
    def _from_room_participant_internal(cls, room_participant_internal: RoomParticipantInternal, **kwargs):
        return cls(
            communication_identifier=_CommunicationIdentifierConverter.to_communication_identifier(room_participant_internal.communication_identifier),
            role=room_participant_internal.role,
            **kwargs
        )

    def to_room_participant_internal(self):
        return RoomParticipantInternal(
            communication_identifier=_CommunicationIdentifierConverter.to_communication_identifier_model(self.communication_identifier),
            role=self.role
        )

class _CommunicationIdentifierConverter():
    def to_communication_identifier_model(communication_identifier):
        if isinstance(communication_identifier, CommunicationUserIdentifier):
            return CommunicationIdentifierModel(
                communication_user=CommunicationUserIdentifierModel(
                    id=communication_identifier.properties['id']
                )
            )
        elif isinstance(communication_identifier, UnknownIdentifier):
            return CommunicationIdentifierModel(
                raw_id=communication_identifier.raw_id
            )
        else:
            raise TypeError()

    def to_communication_identifier(communication_identifier_model: CommunicationIdentifierModel):
        def _assert_not_empty(val, field, type):
            if not val:
                raise DeserializationError('Property "{}" is required for identifier of type {}'.format(field, type))
            return val

        raw_id = _assert_not_empty(communication_identifier_model.raw_id, 'raw_id', type(communication_identifier_model).__name__)

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
        "participants": {"key": "participants", "type": "[RoomParticipant]"},
    }

    def __init__(self, *, participants: List[RoomParticipant], **kwargs):
        """
        :keyword participants: Room Participants. Required.
        :paramtype participants: list[~azure.communication.rooms.RoomParticipant]
        """
        super().__init__(**kwargs)
        self.participants = participants

    def __init__(self, *, participants: List[RoomParticipantInternal], **kwargs):
        super().__init__(**kwargs)
        self.participants = [RoomParticipant._from_room_participant_internal(p) for p in participants]




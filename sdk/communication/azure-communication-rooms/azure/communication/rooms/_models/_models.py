# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import List, Optional, Union

from azure.core.exceptions import DeserializationError
from .._generated.models import (
    RoomParticipant as RoomParticipantInternal,
    CommunicationIdentifierModel,
    CommunicationUserIdentifierModel,
    RoomJoinPolicy,
    RoleType
)
from .._generated.models import RoomModel
from .._shared.models import (
    CommunicationIdentifier,
    CommunicationIdentifierKind,
    CommunicationUserIdentifier,
    UnknownIdentifier
)


class CommunicationRoom():
    """The response object from rooms service.

    :ivar id: Unique identifier of a room. This id is server generated.
    :vartype id: str
    :ivar created_on: The timestamp when the room was created at the server.
    :vartype created_on: ~datetime.datetime
    :ivar valid_from: The timestamp from when the room is open for joining.
    :vartype valid_from: ~datetime.datetime
    :ivar valid_until: The timestamp from when the room can no longer be joined.
    :vartype valid_until: ~datetime.datetime
    :ivar room_join_policy: The join policy of the room.
    :vartype room_join_policy: ~azure.communication.rooms.RoomJoinPolicy
    :ivar participants: Collection of room participants.
    :vartype participants: Optional[List[~azure.communication.rooms.RoomParticipant]]
    """

    def __init__(
        self,
        *,
        id: str, #pylint: disable=redefined-builtin
        created_on: datetime,
        valid_from: datetime,
        valid_until: datetime,
        room_join_policy: RoomJoinPolicy,
        participants: Optional[List['RoomParticipant']]=None,
        **kwargs
    ):
        """
        :param id: Unique identifier of a room. This id is server generated.
        :type id: str
        :param created_on: The timestamp when the room was created at the server.
        :type created_on: ~datetime.datetime
        :param valid_from: The timestamp from when the room is open for joining.
        :type valid_from: ~datetime.datetime
        :param valid_until: The timestamp from when the room can no longer be joined.
        :type valid_until: ~datetime.datetime
        :param room_join_policy: The join policy of the room. Allows only participants or any communication
        service users to join
        :type room_join_policy: ~azure.communication.rooms.RoomJoinPolicy
        :param participants: Collection of room participants.
        :type participants: Optional[List[~azure.communication.rooms.RoomParticipant]]
        """
        super(CommunicationRoom, self).__init__(**kwargs)
        self.id = id
        self.created_on = created_on
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.room_join_policy = room_join_policy
        self.participants = participants

    @classmethod
    def _from_room_response(cls, get_room_response: RoomModel,
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
            # pylint: disable=protected-access
            participants=[RoomParticipant._from_room_participant_internal(p) for p in get_room_response.participants],
            **kwargs
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

class RoomParticipant():
    """A participant of the room.

    All required parameters must be populated in order to send to Azure.

    :ivar communication_identifier: Identifies a participant in Azure Communication services. A
    participant is, for example, an Azure communication user. This model must be interpreted as a
    union: Apart from rawId, at most one further property may be set. Required.
    :vartype communication_identifier:
    ~azure.communication.rooms._shared.models.CommunicationIdentifier
    :ivar role: Role Name.
    :vartype role: Optional[Union[str, RoleType]
    """

    def __init__(
        self,
        *,
        communication_identifier: CommunicationIdentifier,
        role: Optional[Union[str, RoleType]]=None,
        **kwargs
    ):
        """
        :param communication_identifier: Identifies a participant in Azure Communication services. A
         participant is, for example, an Azure communication user. This model must be interpreted as a
         union: Apart from rawId, at most one further property may be set. Required.
        :type communication_identifier:
         ~azure.communication.rooms._shared.models.CommunicationIdentifier
        :param role: The Role of a room participant. Known values are: "Presenter", "Attendee", and
         "Consumer".
        :type role: Optional[Union[str, RoleType]]
        """
        super().__init__(**kwargs)
        self.communication_identifier = communication_identifier
        self.role = role

    @classmethod
    def _from_room_participant_internal(cls, room_participant_internal: RoomParticipantInternal, **kwargs):
        return cls(
            communication_identifier=_CommunicationIdentifierConverter
                .to_communication_identifier(room_participant_internal.communication_identifier),
            role=room_participant_internal.role,
            **kwargs
        )

    def _to_room_participant_internal(self):
        return RoomParticipantInternal(
            communication_identifier=_CommunicationIdentifierConverter
                .to_communication_identifier_model(self.communication_identifier),
            role=self.role
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

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


class ParticipantsCollection():
    """Collection of participants in a room.

    All required parameters must be populated in order to send to Azure.

    :ivar participants: Room Participants. Required.
    :vartype participants: List[~azure.communication.rooms.RoomParticipant]
    """

    def __init__(self, *, participants: List[RoomParticipantInternal], **kwargs):
        super().__init__(**kwargs)
        # pylint: disable=protected-access
        self.participants = [RoomParticipant._from_room_participant_internal(p) for p in participants]

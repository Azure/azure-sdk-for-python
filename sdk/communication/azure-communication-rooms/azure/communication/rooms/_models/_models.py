# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import Any, List, Optional, Union

from azure.core.exceptions import DeserializationError
from .._generated.models import (
    RoomModel,
    ParticipantRole
)
from .._shared.models import (
    CommunicationIdentifier,
    identifier_from_raw_id
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
    """

    def __init__(
        self,
        *,
        id: str, #pylint: disable=redefined-builtin
        created_on: datetime,
        valid_from: datetime,
        valid_until: datetime,
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
        """
        super(CommunicationRoom, self).__init__(**kwargs)
        self.id = id
        self.created_on = created_on
        self.valid_from = valid_from
        self.valid_until = valid_until

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
    :vartype role: Union[str, RoleType]
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

class InvitedRoomParticipant():
    """An invited participant of the room.

    All required parameters must be populated in order to send to Azure.

    :ivar communication_identifier: Identifies a participant in Azure Communication services. A
    participant is, for example, an Azure communication user. This model must be interpreted as a
    union: Apart from rawId, at most one further property may be set. Required.
    :vartype communication_identifier:
    ~azure.communication.rooms._shared.models.CommunicationIdentifier
    :ivar role: Role Name.
    :vartype role: Optional[Union[str, RoleType]
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

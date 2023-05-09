# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import Any, Union, overload, Mapping, Optional
from enum import Enum
from datetime import datetime

from azure.core import CaseInsensitiveEnumMeta


from .._shared.models import (
    CommunicationIdentifier,
    identifier_from_raw_id
)


class ParticipantRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The role of a room participant. The default value is Attendee."""

    PRESENTER = "Presenter"
    ATTENDEE = "Attendee"
    CONSUMER = "Consumer"


class RoomParticipant:
    """A participant of the room.

    All required parameters must be populated in order to send to Azure.

    :ivar communication_identifier: Communication Identifier.
    :vartype communication_identifier: ~azure.communication.rooms.CommunicationIdentifier
    :ivar role: Role Name.
    :vartype role: Union[str, ParticipantRole]
    """
    @overload
    def __init__(
        self,
        *,
        communication_identifier: CommunicationIdentifier,
        role: Union[str, ParticipantRole] = ParticipantRole.ATTENDEE,
    ) -> None:
        """
        :keyword communication_identifier: Raw ID representation of the communication identifier. Please refer to the
         following document for additional information on Raw ID. :code:`<br>`
         https://learn.microsoft.com/azure/communication-services/concepts/identifiers?pivots=programming-language-rest#raw-id-representation.
        :paramtype communication_identifier: ~azure.communication.rooms.CommunicationIdentifier
        :keyword role: The role of a room participant. The default value is Attendee. Known
         values are: "Presenter", "Attendee", and "Consumer".
        :paramtype role: str or ~azure.communication.rooms.models.ParticipantRole
        """
    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model. Positional only.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1:
            self.communication_identifier = identifier_from_raw_id(args[0]['rawId'])
            self.role = args[0]['role']
        elif args:
            raise TypeError(f"RoomParticipant.__init__() takes 2 positional arguments but {len(args) + 1} were given.")
        else:
            self.communication_identifier = kwargs['communication_identifier']
            self.role = kwargs.get('role', ParticipantRole.ATTENDEE)
        self.role=self.role or ParticipantRole.ATTENDEE

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False


class CommunicationRoom:
    """The meeting room.

    All required parameters must be populated in order to send to Azure.

    :ivar id: Unique identifier of a room. This id is server generated. Required.
    :vartype id: str
    :ivar created_at: The timestamp when the room was created at the server. The timestamp is in
     RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``. Read-only.
    :vartype created_at: ~datetime.datetime
    :ivar valid_from: The timestamp from when the room is open for joining. The timestamp is in
     RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype valid_from: ~datetime.datetime
    :ivar valid_until: The timestamp from when the room can no longer be joined. The timestamp is
     in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype valid_until: ~datetime.datetime
    """

    @overload
    def __init__(
        self,
        *,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None
    ):
        ...
    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model. Positional only.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1:
            self.id = args[0]['id']
            self.created_at = args[0]['createdAt']
            self.valid_from = args[0]['validFrom']
            self.valid_until = args[0]['validUntil']
        elif args:
            raise TypeError(
                f"CommunicationRoom.__init__() takes 2 positional arguments but {len(args) + 1} were given."
            )
        else:
            self.id = None
            self.created_at = None
            self.valid_from = kwargs.get('valid_from')
            self.valid_until = kwargs.get('valid_until')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

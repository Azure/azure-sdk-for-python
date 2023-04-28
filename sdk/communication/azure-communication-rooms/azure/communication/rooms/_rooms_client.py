# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import List, Optional, Union, Any
import uuid
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace

from azure.communication.rooms._models import (
    RoomParticipant,
    CommunicationRoom
)
from azure.communication.rooms._shared.models import CommunicationIdentifier
from ._generated._client import AzureCommunicationRoomsService
from ._shared.utils import parse_connection_str, get_authentication_policy
from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION

class RoomsClient(object):
    """A client to interact with the AzureCommunicationService Rooms gateway.

    This client provides operations to manage rooms.

    This client provides operations to manage rooms.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    param Union[TokenCredential, AzureKeyCredential] credential:
        The access key we use to authenticate against the service.
    :keyword api_version: Azure Communication Rooms API version.
        Default value is "2023-03-31-preview".
        Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(
            self,
            endpoint: str,
            credential: Union[TokenCredential, AzureKeyCredential],
            **kwargs
    ) -> None:
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "invalid credential from connection string.")

        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._authentication_policy = get_authentication_policy(endpoint, credential, decode_url=True)
        self._rooms_service_client = AzureCommunicationRoomsService(
            self._endpoint,
            api_version=self._api_version,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str: str,
            **kwargs
    ) -> 'RoomsClient':
        """Create RoomsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of RoomsClient.
        :rtype: ~azure.communication.room.RoomsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/Rooms_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the RoomsClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    @distributed_trace
    def create_room(
        self,
        *,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        participants: Optional[List[RoomParticipant]]=None,
        **kwargs
    ) -> CommunicationRoom:
        """Create a new room.

        :param valid_from: The timestamp from when the room is open for joining. Optional.
        :type valid_from: ~datetime.datetime
        :param valid_until: The timestamp from when the room can no longer be joined. Optional.
        :type valid_until: ~datetime.datetime
        :param participants: Collection of identities invited to the room. Optional.
        :type participants: List[~azure.communication.rooms.RoomParticipant]
        :returns: Created room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        create_room_request = {
            "validFrom": valid_from,
            "validUntil": valid_until
        }
        if participants:
            create_room_request["participants"] ={
                p.communication_identifier.raw_id: {"role": p.role} for p in participants
            }

        repeatability_request_id = uuid.uuid1()
        repeatability_first_sent = datetime.utcnow()
        create_room_response = self._rooms_service_client.rooms.create(
            create_room_request=create_room_request,
            repeatability_request_id=repeatability_request_id,
            repeatability_first_sent=repeatability_first_sent,
            **kwargs)
        return CommunicationRoom(create_room_response)

    @distributed_trace
    def delete_room(
        self,
        room_id: str,
        **kwargs
    ) -> None:

        """Delete room.

        :param room_id: Required. Id of room to be deleted
        :type room_id: str
        :returns: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._rooms_service_client.rooms.delete(room_id=room_id, **kwargs)

    @distributed_trace
    def update_room(
        self,
        *,
        room_id: str,
        valid_from: datetime,
        valid_until: datetime,
        **kwargs: Any
    ) -> CommunicationRoom:
        """Update a valid room's attributes. For any argument that is passed
        in, the corresponding room property will be replaced with the new value.

        :keyword room_id: Required. Id of room to be updated
        :type room_id: str
        :keyword valid_from: Required. The timestamp from when the room is open for joining.
        :type valid_from: ~datetime.datetime
        :keyword valid_until: Required. The timestamp from when the room can no longer be joined.
        :type valid_until: ~datetime.datetime
        :returns: Updated room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        update_room_request = {
            "validFrom": valid_from,
            "validUntil": valid_until
        }
        update_room_response = self._rooms_service_client.rooms.update(
            room_id=room_id, update_room_request=update_room_request, **kwargs)
        return CommunicationRoom(update_room_response)

    @distributed_trace
    def get_room(
        self,
        room_id: str,
        **kwargs
    ) -> CommunicationRoom:
        """Get a valid room

        :param room_id: Required. Id of room to be fetched
        :type room_id: str
        :returns: Room with current attributes.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        get_room_response = self._rooms_service_client.rooms.get(room_id=room_id, **kwargs)
        return CommunicationRoom(get_room_response)

    @distributed_trace
    def list_rooms(
        self,
        **kwargs
    ) -> ItemPaged[CommunicationRoom]:
        """List all rooms

        :returns: An iterator like instance of CommunicationRoom.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.rooms.CommunicationRoom]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._rooms_service_client.rooms.list(
            cls=lambda rooms: [CommunicationRoom(r) for r in rooms]
            **kwargs
        )

    @distributed_trace
    def add_or_update_participants(
        self,
        *,
        room_id: str,
        participants: List[RoomParticipant],
        **kwargs
    ) -> None:
        """Update participants to a room. It looks for the room participants based on their
        communication identifier and replace the existing participants with the value passed in
        this API.
        :param room_id: Required. Id of room to be updated
        :type room_id: str
        :param participants: Required. Collection of identities invited to be updated
        :type participants: List[~azure.communication.rooms.RoomParticipant]
        :returns: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        update_participants_request = {
            "participants": {p.communication_identifier.raw_id: {"role": p.role} for p in participants}
        }
        self._rooms_service_client.participants.update(
            room_id=room_id, update_participants_request=update_participants_request, **kwargs)

    @distributed_trace
    def remove_participants(
        self,
        *,
        room_id: str,
        participants: List[Union[RoomParticipant, CommunicationIdentifier]],
        **kwargs
    ) -> None:
        """Remove participants from a room
        :param room_id: Required. Id of room to be updated
        :type room_id: str
        :param participants: Required. Collection of identities to be removed from the room.
        :type participants:
         List[Union[~azure.communication.rooms.RoomParticipant, ~azure.communication.rooms.CommunicationIdentifier]]
        :returns: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        remove_participants_request = {
            "participants": {}
        }
        for participant in participants:
            try:
                remove_participants_request["participants"][participant.communication_identifier.raw_id] = None
            except AttributeError:
                remove_participants_request["participants"][participant.raw_id] = None
        self._rooms_service_client.participants.update(
            room_id=room_id, update_participants_request=remove_participants_request, **kwargs)

    @distributed_trace
    def list_participants(
        self,
        room_id: str,
        **kwargs
    )-> ItemPaged[RoomParticipant]:
        """Get participants of a room
        :param room_id: Required. Id of room whose participants to be fetched.
        :type room_id: str
        :returns: An iterator like instance of RoomParticipant.
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.rooms.RoomParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._rooms_service_client.participants.list(
            room_id=room_id,
            cls=lambda objs: [RoomParticipant(x) for x in objs],
            **kwargs)

    def __enter__(self) -> "RoomsClient":
        self._rooms_service_client.__enter__()
        return self

    def __exit__(self, *args: "Any") -> None:
        self.close()

    def close(self) -> None:
        """Close the :class:
        `~azure.communication.rooms.RoomsClient` session.
        """
        self._rooms_service_client.__exit__()

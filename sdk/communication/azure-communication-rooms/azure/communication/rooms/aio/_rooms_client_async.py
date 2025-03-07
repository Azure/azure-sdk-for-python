# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import List, Optional, Union, Any
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.async_paging import AsyncItemPaged
from azure.communication.rooms._models import RoomParticipant, CommunicationRoom
from azure.communication.rooms._shared.models import CommunicationIdentifier
from .._generated.aio._client import AzureCommunicationRoomsService
from .._generated._serialization import Serializer
from .._shared.auth_policy_utils import get_authentication_policy
from .._shared.utils import parse_connection_str
from .._version import SDK_MONIKER
from .._api_versions import DEFAULT_VERSION


class RoomsClient(object):
    """A client to interact with the AzureCommunicationService Rooms gateway.

    This client provides operations to manage rooms.

    :param str endpoint:
     The endpoint url for Azure Communication Service resource.
    :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
     The access key we use to authenticate against the service.
    :keyword api_version: Azure Communication Rooms API version.
     Default value is "2023-06-14".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: Union[AsyncTokenCredential, AzureKeyCredential], **kwargs) -> None:
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError as exc:
            raise ValueError("Account URL must be a string.") from exc

        if not credential:
            raise ValueError("invalid credential from connection string.")

        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._authentication_policy = get_authentication_policy(endpoint, credential, decode_url=True, is_async=True)
        self._rooms_service_client = AzureCommunicationRoomsService(
            self._endpoint,
            api_version=self._api_version,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs) -> "RoomsClient":
        """Create RoomsClient from a Connection String.

        :param str conn_str:
         A connection string to an Azure Communication Service resource.
        :returns: Instance of RoomsClient.
        :rtype: ~azure.communication.room.RoomsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/rooms_client_sample_async.py
                :start-after: [START auth_from_connection_string_async]
                :end-before: [END auth_from_connection_string_async]
                :language: python
                :dedent: 8
                :caption: Creating the RoomsClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    @distributed_trace_async
    async def create_room(
        self,
        *,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        pstn_dial_out_enabled: bool = False,
        participants: Optional[List[RoomParticipant]] = None,
        **kwargs
    ) -> CommunicationRoom:
        """Create a new room.

        :keyword datetime valid_from: The timestamp from when the room is open for joining. Optional.
        :keyword datetime valid_until: The timestamp from when the room can no longer be joined. Optional.
        :keyword bool pstn_dial_out_enabled: Set this flag to true if, at the time of the call,
         dial out to a PSTN number is enabled in a particular room. Optional.
        :keyword List[RoomParticipant] participants: Collection of identities invited to the room. Optional.
        :returns: Created room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        create_room_request = {
            "validFrom": valid_from,
            "validUntil": valid_until,
            "pstnDialOutEnabled": pstn_dial_out_enabled,
        }
        if participants:
            create_room_request["participants"] = {
                p.communication_identifier.raw_id: {"role": p.role} for p in participants
            }
        _SERIALIZER = Serializer()

        repeatability_request_id = str(uuid.uuid1())
        repeatability_first_sent = Serializer().serialize_data(datetime.utcnow(), "rfc-1123")

        request_headers = kwargs.pop("headers", {})
        request_headers.update(
            {"Repeatability-Request-Id": repeatability_request_id, "Repeatability-First-Sent": repeatability_first_sent}
        )

        create_room_response = await self._rooms_service_client.rooms.create(
            create_room_request=create_room_request, headers=request_headers, **kwargs
        )

        return CommunicationRoom(create_room_response)

    @distributed_trace_async
    async def delete_room(self, room_id: str, **kwargs) -> None:
        """Delete room.

        :param room_id: Required. Id of room to be deleted
        :type room_id: str
        :returns: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return await self._rooms_service_client.rooms.delete(room_id=room_id, **kwargs)

    @distributed_trace_async
    async def update_room(
        self,
        *,
        room_id: str,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        pstn_dial_out_enabled: Optional[bool] = None,
        **kwargs: Any
    ) -> CommunicationRoom:
        """Update a valid room's attributes. For any argument that is passed
        in, the corresponding room property will be replaced with the new value.

        :keyword str room_id: Required. Id of room to be updated
        :keyword datetime valid_from: The timestamp from when the room is open for joining. Optional.
        :keyword datetime valid_until: The timestamp from when the room can no longer be joined. Optional.
        :keyword bool pstn_dial_out_enabled: Optional. Set this flag to true if, at the time of the call,
         dial out to a PSTN number is enabled in a particular room. By default, this flag is set to false.
        :returns: Updated room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        update_room_request = {
            "validFrom": valid_from,
            "validUntil": valid_until,
            "pstnDialOutEnabled": pstn_dial_out_enabled,
        }
        update_room_response = await self._rooms_service_client.rooms.update(
            room_id=room_id, update_room_request=update_room_request, **kwargs
        )
        return CommunicationRoom(update_room_response)

    @distributed_trace_async
    async def get_room(self, room_id: str, **kwargs) -> CommunicationRoom:
        """Get a valid room

        :param room_id: Required. Id of room to be fetched
        :type room_id: str
        :returns: Room with current attributes.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        get_room_response = await self._rooms_service_client.rooms.get(room_id=room_id, **kwargs)
        return CommunicationRoom(get_room_response)

    @distributed_trace
    def list_rooms(self, **kwargs) -> AsyncItemPaged[CommunicationRoom]:
        """List all rooms

        :returns: An iterator like instance of CommunicationRoom.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.rooms.CommunicationRoom]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._rooms_service_client.rooms.list(cls=lambda rooms: [CommunicationRoom(r) for r in rooms], **kwargs)

    @distributed_trace_async
    async def add_or_update_participants(self, *, room_id: str, participants: List[RoomParticipant], **kwargs) -> None:
        """Update participants to a room. It looks for the room participants based on their
        communication identifier and replace those participants with the value passed in
        this API.

        :keyword str room_id: Required. Id of room to be updated
        :keyword List[RoomParticipant] participants:
         Required. Collection of identities invited to be updated
        :returns: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        update_participants_request = {
            "participants": {p.communication_identifier.raw_id: {"role": p.role} for p in participants}
        }
        await self._rooms_service_client.participants.update(
            room_id=room_id, update_participants_request=update_participants_request, **kwargs
        )

    @distributed_trace_async
    async def remove_participants(
        self, *, room_id: str, participants: List[Union[RoomParticipant, CommunicationIdentifier]], **kwargs
    ) -> None:
        """Remove participants from a room

        :keyword str room_id: Required. Id of room to be updated
        :keyword List[Union[RoomParticipant, CommunicationIdentifier]] participants:
         Required. Collection of identities to be removed from the room.
        :returns: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        remove_participants_request = {"participants": {}}
        for participant in participants:
            try:
                remove_participants_request["participants"][participant.communication_identifier.raw_id] = None
            except AttributeError:
                remove_participants_request["participants"][participant.raw_id] = None
        await self._rooms_service_client.participants.update(
            room_id=room_id, update_participants_request=remove_participants_request, **kwargs
        )

    @distributed_trace
    def list_participants(self, room_id: str, **kwargs) -> AsyncItemPaged[RoomParticipant]:
        """Get participants of a room

        :param room_id: Required. Id of room whose participants to be fetched.
        :type room_id: str
        :returns: An iterator like instance of RoomParticipant.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.rooms.RoomParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._rooms_service_client.participants.list(
            room_id=room_id, cls=lambda objs: [RoomParticipant(x) for x in objs], **kwargs
        )

    async def __aenter__(self) -> "RoomsClient":
        await self._rooms_service_client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self.close()

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.rooms.aio.RoomsClient` session.
        """
        await self._rooms_service_client.__aexit__()

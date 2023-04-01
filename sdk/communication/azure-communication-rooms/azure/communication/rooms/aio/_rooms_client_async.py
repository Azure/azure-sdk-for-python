# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ast import Dict
from datetime import datetime
from typing import Any, List, Optional
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.async_paging import AsyncItemPaged
from azure.communication.rooms._models import (
    RoomParticipant,
    InvitedRoomParticipant,
    UpsertParticipantsResult,
    RemoveParticipantsResult)
from azure.communication.rooms._shared.models import CommunicationIdentifier
from azure.communication.rooms._shared.policy import HMACCredentialsPolicy
from .._generated.aio._client import AzureCommunicationRoomsService
from .._shared.utils import parse_connection_str
from .._version import SDK_MONIKER
from .._api_versions import DEFAULT_VERSION
from .._generated.models import (
    CommunicationRoom,
    CreateRoomRequest,
    UpdateRoomRequest,
    UpdateParticipantsRequest,
    ParticipantProperties
)

class RoomsClient(object):
    """A client to interact with the AzureCommunicationService Rooms gateway.

    This client provides operations to manage rooms.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param ~azure.core.credentials.AzureKeyCredential credential:
        The access key we use to authenticate against the service.
    :keyword api_version: Azure Communication Rooms API version.
        Default value is "2023-03-31-preview". Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(
            self, endpoint: str,
            credential: AzureKeyCredential,
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

        # TokenCredential not supported at the moment
        if hasattr(credential, "get_token"):
            raise TypeError("Unsupported credential: {}. Use an AzureKeyCredential to use HMACCredentialsPolicy"
                    " for authentication".format(type(credential)))

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._authentication_policy = HMACCredentialsPolicy(endpoint, credential.key, decode_url=True)
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

    @distributed_trace_async
    async def create_room(
        self,
        *,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        participants:Optional[List[InvitedRoomParticipant]] = None,
        **kwargs
    ) -> CommunicationRoom:
        """Create a new room.

        :param valid_from: The timestamp from when the room is open for joining. Optional.
        :type valid_from: ~datetime.datetime
        :param valid_until: The timestamp from when the room can no longer be joined. Optional.
        :type valid_until: ~datetime.datetime
        :param participants: Collection of identities invited to the room. Optional.
        :type participants: List[~azure.communication.rooms.InvitedRoomParticipant]
        :returns: Created room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        create_room_request = CreateRoomRequest(
            valid_from=valid_from,
            valid_until=valid_until,
            # pylint: disable=protected-access
            participants=self._convert_room_participants_to_dictionary_for_upsert(participants)
        )

        repeatability_request_id = uuid.uuid1()
        repeatability_first_sent = datetime.utcnow()

        create_room_response = await self._rooms_service_client.rooms.create(
            create_room_request=create_room_request,
            repeatability_request_id=repeatability_request_id,
            repeatability_first_sent=repeatability_first_sent,
            **kwargs)
        return create_room_response # pylint: disable=protected-access

    @distributed_trace_async
    async def delete_room(
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
        await self._rooms_service_client.rooms.delete(room_id=room_id, **kwargs)

    @distributed_trace_async
    async def update_room(
        self,
        *,
        room_id: str,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        **kwargs
    ) -> CommunicationRoom:
        """Update a valid room's attributes. For any argument that is passed
        in, the corresponding room property will be replaced with the new value.

        :param room_id: Required. Id of room to be updated
        :type room_id: str
        :param valid_from: The timestamp from when the room is open for joining. Optional.
        :type valid_from: ~datetime.datetime
        :param valid_until: The timestamp from when the room can no longer be joined. Optional.
        :type valid_until: ~datetime.datetime
        :returns: Updated room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        """
        update_room_request = UpdateRoomRequest(
            valid_from=valid_from,
            valid_until=valid_until,
        )
        update_room_response = await self._rooms_service_client.rooms.update(
            room_id=room_id, update_room_request=update_room_request, **kwargs)
        return update_room_response # pylint: disable=protected-access

    @distributed_trace_async
    async def get_room(
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
        get_room_response = await self._rooms_service_client.rooms.get(room_id=room_id, **kwargs)
        return get_room_response # pylint: disable=protected-access

    @distributed_trace
    def list_rooms(
        self,
        **kwargs
    ): # type:(...) -> AsyncItemPaged[CommunicationRoom]
        """List all rooms

        :returns: An iterator like instance of CommunicationRoom.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.rooms.CommunicationRoom]
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self._rooms_service_client.rooms.list(**kwargs)


    @distributed_trace_async
    async def upsert_participants(
        self,
        *,
        room_id: str,
        participants: List[InvitedRoomParticipant],
        **kwargs
    ) -> UpsertParticipantsResult:
        """Update participants to a room. It looks for the room participants based on their
        communication identifier and replace those participants with the value passed in
        this API.
        :param room_id: Required. Id of room to be updated
        :type room_id: str
        :param participants: Required. Collection of identities to be updated
        :type participants: List[~azure.communication.rooms.InvitedRoomParticipant]
        :return: Upsert participants result
        :rtype: ~azure.communication.rooms.UpsertParticipantsResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        update_participants_request = UpdateParticipantsRequest(
            # pylint: disable=protected-access
            participants=self._convert_room_participants_to_dictionary_for_upsert(participants)
        )
        await self._rooms_service_client.participants.update(
            room_id=room_id, update_participants_request=update_participants_request, **kwargs)
        return UpsertParticipantsResult()

    @distributed_trace_async
    async def remove_participants(
        self,
        *,
        room_id: str,
        communication_identifiers: List[CommunicationIdentifier],
        **kwargs
    ) -> RemoveParticipantsResult:
        """Remove participants from a room
        :param room_id: Required. Id of room to be updated
        :type room_id: str
        :param participants: Required. Collection of identities to be removed from the room.
        :type participants: List[~azure.communication.rooms._shared.models.CommunicationIdentifier]
        :return: Upsert participants result
        :rtype: ~azure.communication.rooms.RemoveParticipantsResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        remove_participants_request = UpdateParticipantsRequest(
            participants=self._convert_communication_identifiers_to_dictionary_for_remove(communication_identifiers)
        )
        await self._rooms_service_client.participants.update(
            room_id=room_id, update_participants_request=remove_participants_request, **kwargs)
        return RemoveParticipantsResult()

    @distributed_trace
    def list_participants(
        self,
        room_id: str,
        **kwargs
    ):  # type: (...) -> AsyncItemPaged[RoomParticipant]
        """Get participants of a room
        :param room_id: Required. Id of room whose participants to be fetched.
        :type room_id: str
        :returns: An iterator like instance of RoomParticipant.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.rooms.RoomParticipant]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._rooms_service_client.participants.list(
            room_id=room_id,
            cls=lambda objs: [RoomParticipant._from_generated(x) for x in objs],  # pylint:disable=protected-access
            **kwargs)

    def _convert_room_participants_to_dictionary_for_upsert(self, room_participants : List[InvitedRoomParticipant]):
        upsert_dictionary = dict()
        for participant in room_participants or []:
            upsert_dictionary[participant.communication_identifier.raw_id] = ParticipantProperties(role=participant.role)
        return upsert_dictionary

    def _convert_communication_identifiers_to_dictionary_for_remove(self, communication_identifiers : List[CommunicationIdentifier]):
        remove_dictionary = dict()
        for identifier in communication_identifiers or []:
            remove_dictionary[identifier.raw_id] = None
        return remove_dictionary

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

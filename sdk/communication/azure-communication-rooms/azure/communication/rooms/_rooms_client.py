# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from azure.core.tracing.decorator import distributed_trace
from azure.communication.rooms._models import RoomRequest, CommunicationRoom

from ._generated._azure_communication_rooms_service import AzureCommunicationRoomsService
from ._generated.models import (
    CreateRoomRequest,
)

from ._shared.utils import parse_connection_str, get_authentication_policy
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    from typing import Any

class RoomsClient(object):
    """A client to interact with the AzureCommunicationService Rooms gateway.

    This client provides operations to manage rooms.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param TokenCredential credential:
        The TokenCredential we use to authenticate against the service.
    """
    def __init__(
            self, endpoint, # type: str
            credential, # type: TokenCredential
            **kwargs # type: Any
    ):
        # type: (...) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "invalid credential from connection string.")

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        self._rooms_service_client = AzureCommunicationRoomsService(
            self._endpoint,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> RoomsClient
        """Create RoomsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of RoomsClient.
        :rtype: ~azure.communication.RoomsClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/Rooms_sample.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the RoomsClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace
    def create_room(
        self,
        room_request=None, # type: RoomRequest
        **kwargs
    ):
        # type: (...) -> CommunicationRoom
        """Create a new room.

        :param room_request: Room to be created. If it is not specified,
         room will be created with 180 days of validity
        :type room_request: RoomRequest
        :returns: Created room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        create_room_request = None
        if room_request is not None:
            create_room_request = room_request.to_create_room_request()
        else:
            create_room_request = CreateRoomRequest()
        create_room_response = self._rooms_service_client.rooms.create_room(
            create_room_request=create_room_request, **kwargs)
        return CommunicationRoom.from_create_room_response(create_room_response)

    @distributed_trace
    def delete_room(
        self,
        room_id, # type: str
        **kwargs
    ):
        # type: (...) -> CommunicationRoom
        """Delete room.

        :param room_id: Required. Id of room to be deleted
        :type room_id: str
        :returns: None.
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        self._rooms_service_client.rooms.delete_room(room_id=room_id, **kwargs)

    @distributed_trace
    def update_room(
        self,
        room_id,
        room_request, # type: RoomRequest
        **kwargs
    ):
        # type: (...) -> CommunicationRoom
        """Update a valid room's attributes

        :param room_id: Required. Id of room to be updated
        :type room_id: str
        :param room_request: Required. Room with new attributes
        :type room_request: RoomRequest
        :returns: Updated room.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        """
        if not room_request:
            raise ValueError("room_request cannot be None.")
        update_room_request = room_request.to_update_room_request()
        update_room_response = self._rooms_service_client.rooms.update_room(
            room_id=room_id, update_room_request=update_room_request, **kwargs)
        return CommunicationRoom.from_update_room_response(update_room_response)

    @distributed_trace
    def get_room(
        self,
        room_id, # type: str
        **kwargs
    ):
        # type: (...) -> CommunicationRoom
        """Get a valid room

        :param room_id: Required. Id of room to be fetched
        :type room_id: str
        :returns: Room with current attributes.
        :rtype: ~azure.communication.rooms.CommunicationRoom
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        get_room_response = self._rooms_service_client.rooms.get_room(room_id=room_id, **kwargs)
        return CommunicationRoom.from_get_room_response(get_room_response)
    
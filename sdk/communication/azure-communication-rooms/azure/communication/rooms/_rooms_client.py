# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from uuid import uuid4
from azure.core.tracing.decorator import distributed_trace
from azure.communication.rooms._models import RoomRequest, CommunicationRoom

from ._generated._azure_communication_rooms_service import AzureCommunicationRoomsService
from ._shared.utils import parse_connection_str, get_authentication_policy, get_current_utc_time
from ._version import SDK_MONIKER

class RoomsClient(object):
    """A client to interact with the AzureCommunicationService Rooms gateway.

    This client provides operations to send an SMS via a phone number.

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

    def create_room(
        self,
        roomRequest=None, # type: RoomRequest
        **kwargs
    ):
        # type: (...) -> CommunicationRoom
        create_room_request = roomRequest.to_create_room_request()
        create_room_response = self._rooms_service_client.rooms.create_room(
            create_room_request=create_room_request, **kwargs)
        return CommunicationRoom.from_create_room_response(create_room_response)
    
    def delete_room(
        self,
        room_id, # type: str
        **kwargs
    ):
        self._rooms_service_client.rooms.delete_room(room_id=room_id, **kwargs)
    
    def update_room(
        self,
        room_id,
        roomRequest=None, # type: RoomRequest
        **kwargs
    ):
        # type: (...) -> CommunicationRoom
        update_room_request = roomRequest.to_update_room_request()
        update_room_response = self._rooms_service_client.rooms.update_room(
            room_id=room_id, update_room_request=update_room_request, **kwargs)
        return CommunicationRoom.from_update_room_response(update_room_response)
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List
from azure.communication.callingserver.aio import CallingServerClient, CallConnection
from azure.communication.callingserver import (
    CommunicationUserIdentifier,
    CreateCallOptions,
    CallMediaType,
    CallingEventSubscriptionType,
    ServerCallLocator,
    GroupCallLocator
    )
from utils._live_test_utils import CallingServerLiveTestUtils

class CallingServerLiveTestUtilsAsync:

    @staticmethod
    def validate_callconnection_Async(call_connection_async: CallConnection):
        assert call_connection_async is not None
        assert call_connection_async.call_connection_id is not None
        assert len(call_connection_async.call_connection_id) != 0

    @staticmethod
    async def create_group_calls_async(
        callingserver_client: CallingServerClient,
        group_id: str,
        from_user: str,
        to_user: str,
        call_back_uri: str
        ) -> List[CallConnection]:
        from_participant = CommunicationUserIdentifier(from_user)
        to_participant = CommunicationUserIdentifier(to_user)
        group_calls = []

        from_call_connection = None
        to_call_connection = None
        try:
            # join from_participant to Server Call
            from_options = CreateCallOptions(
                callback_uri=call_back_uri,
                requested_media_types=[CallMediaType.AUDIO],
                requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED]
            )
            from_call_connection = await callingserver_client.join_call(GroupCallLocator(group_id), from_participant, from_options)
            CallingServerLiveTestUtilsAsync.validate_callconnection_Async(from_call_connection)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()

            # join to_participant to Server Call
            to_options = CreateCallOptions(
                callback_uri=call_back_uri,
                requested_media_types=[CallMediaType.AUDIO],
                requested_call_events=[CallingEventSubscriptionType.PARTICIPANTS_UPDATED]
            )
            to_call_connection = await callingserver_client.join_call(GroupCallLocator(group_id), to_participant, to_options)
            CallingServerLiveTestUtilsAsync.validate_callconnection_Async(from_call_connection)
            CallingServerLiveTestUtils.sleep_if_in_live_mode()

            group_calls.append(from_call_connection)
            group_calls.append(to_call_connection)

            return group_calls

        except Exception as err:
            print("An exception occurred: ", err)

            if from_call_connection is not None:
                await from_call_connection.hang_up()
            if to_call_connection is not None:
                await to_call_connection.hang_up()

            raise err

    @staticmethod
    async def cancel_all_media_operations_for_group_call_async(call_connections: List[CallConnection]) -> None:
        if call_connections is None:
            return
        for connection in call_connections:
            if connection is not None:
                await connection.cancel_all_media_operations()

    @staticmethod
    async def clean_up_connections_async(call_connections: List[CallConnection]) -> None:
        if call_connections is None:
            return
        for connection in call_connections:
            if connection is not None:
                await connection.hang_up()

    @staticmethod
    def get_delete_url():
        # For recording tests, a new delete url should be generated.
        return "https://storage.asm.skype.com/v1/objects/0-wus-d3-ae157c63a416e12d1415e9ea9da8e779"

    @staticmethod
    def get_invalid_delete_url():
        return "https://storage.asm.skype.com/v1/objects/0-eus-d3-00000000000000000000000000000000"

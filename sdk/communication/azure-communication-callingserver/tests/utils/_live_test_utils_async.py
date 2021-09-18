# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
from typing import List
from devtools_testutils import is_live
from azure.communication.callingserver.aio import CallingServerClient, CallConnection
from azure.communication.callingserver import (
    CommunicationUserIdentifier,
    CreateCallOptions,
    MediaType,
    EventSubscriptionType
    )

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
        ):
        group_calls = []

        try:
            from_participant = CommunicationUserIdentifier(from_user)
            to_participant = CommunicationUserIdentifier(to_user)

            # create from_participant option
            from_options = CreateCallOptions(
                callback_uri=call_back_uri,
                requested_media_types=[MediaType.AUDIO],
                requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED]
            )

            async with callingserver_client:
                from_call_connection = await callingserver_client.join_call(group_id, from_participant, from_options)

                if is_live():
                    time.sleep(10)

                CallingServerLiveTestUtilsAsync.validate_callconnection_Async(from_call_connection)

                # create to_participant option
                to_options = CreateCallOptions(
                    callback_uri=call_back_uri,
                    requested_media_types=[MediaType.AUDIO],
                    requested_call_events=[EventSubscriptionType.PARTICIPANTS_UPDATED]
                )

                to_call_connection = await callingserver_client.join_call(group_id, to_participant, to_options)

                if is_live():
                    time.sleep(10)

                CallingServerLiveTestUtilsAsync.validate_callconnection_Async(from_call_connection)

                group_calls.append(from_call_connection)
                group_calls.append(to_call_connection)
                return group_calls

        except Exception as err:
                print("An exception occurred")

        finally:
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
                try:
                    await connection.cancel_all_media_operations()
                except Exception as err:
                    print("Error cancel group call media operations: " + str(err))


    @staticmethod
    async def clean_up_connections_async(call_connections: List[CallConnection]) -> None:
        if call_connections is None:
            return

        for connection in call_connections:
            if connection is not None:
                try:
                    await connection.hang_up()
                except Exception as err:
                    print("Error hanging up: " + str(err))

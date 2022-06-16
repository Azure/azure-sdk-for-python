# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
import asyncio
import logging

from azure.eventhub._pyamqp.aio import _authentication_async
from azure.eventhub._pyamqp.aio import ReceiveClientAsync, SendClientAsync
from azure.eventhub._pyamqp.constants import TransportType
from azure.eventhub._pyamqp.message import Message


async def send_message(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    sas_auth = _authentication_async.SASTokenAuthAsync(
        uri=uri,
        audience=uri,
        username=live_eventhub['key_name'],
        password=live_eventhub['access_key']
    )

    target = "amqps://{}/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['partition']
        )

    message = Message(value="Single Message")

    async with SendClientAsync(live_eventhub['hostname'], target, auth=sas_auth, debug=True, transport_type=TransportType.Amqp) as send_client:
        await send_client.send_message_async(message)

@pytest.mark.skip()
@pytest.mark.asyncio
async def test_event_hubs_client_web_socket_async(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    sas_auth = _authentication_async.SASTokenAuthAsync(
        uri=uri,
        audience=uri,
        username=live_eventhub['key_name'],
        password=live_eventhub['access_key']
    )

    source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['consumer_group'],
        live_eventhub['partition'])
    

    await send_message(live_eventhub=live_eventhub)

    async with ReceiveClientAsync(live_eventhub['hostname'] + '/$servicebus/websocket/', source, auth=sas_auth, debug=True, timeout=10, prefetch=1, transport_type=TransportType.AmqpOverWebsocket) as receive_client:
        begin = receive_client._received_messages.qsize()
        await receive_client.receive_message_batch_async(max_batch_size=1)
        assert receive_client._received_messages.qsize() - begin > 0

# Need to fix this test 
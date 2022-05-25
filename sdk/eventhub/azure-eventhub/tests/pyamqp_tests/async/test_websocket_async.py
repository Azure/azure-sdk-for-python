# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
import asyncio
import logging
import pytest

from azure.eventhub._pyamqp import authentication
from azure.eventhub._pyamqp.aio import ReceiveClientAsync
from azure.eventhub._pyamqp.constants import TransportType

@pytest.mark.asyncio
async def test_event_hubs_client_web_socket(eventhub_config):
    uri = "sb://{}/{}".format(eventhub_config['hostname'], eventhub_config['event_hub'])
    sas_auth = SASTokenAuthAsync(
        uri=uri,
        audience=uri,
        username=eventhub_config['key_name'],
        password=eventhub_config['access_key']
    )

    source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
        eventhub_config['hostname'],
        eventhub_config['event_hub'],
        eventhub_config['consumer_group'],
        eventhub_config['partition'])

    receive_client = ReceiveClientAsync(eventhub_config['hostname'] + '/$servicebus/websocket/', source, auth=sas_auth, debug=False, timeout=5000, prefetch=50, transport_type=TransportType.AmqpOverWebsocket)
    await receive_client.open_async()
    while not await receive_client.client_ready_async():
        await asyncio.sleep(0.05)
    messages = await receive_client.receive_message_batch_async(max_batch_size=1)
    logging.info(len(messages))
    logging.info(messages[0])
    await receive_client.close_async()

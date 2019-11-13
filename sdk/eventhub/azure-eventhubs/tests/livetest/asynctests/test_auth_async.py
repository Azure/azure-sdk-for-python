#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import asyncio

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_secret_credential_async(aad_credential, live_eventhub):
    try:
        from azure.identity.aio import EnvironmentCredential
    except ImportError:
        pytest.skip("No azure identity library")

    credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(host=live_eventhub['hostname'],
                                             event_hub_path=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    consumer_client = EventHubConsumerClient(host=live_eventhub['hostname'],
                                             event_hub_path=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')

    async with producer_client:
        await producer_client.send(EventData(body='A single message'))

    async def event_handler(partition_context, events):
        assert partition_context.partition_id == '0'
        assert len(events) == 1
        assert list(events[0].body)[0] == 'A single message'.encode('utf-8')

    async with consumer_client:
        task = asyncio.ensure_future(
            consumer_client.receive(event_handler=event_handler, consumer_group='$default', partition_id='0'))
        await asyncio.sleep(2)
        task.cancel()

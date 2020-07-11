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
async def test_client_secret_credential_async(aad_credential, aad_credential_test_eh):
    try:
        from azure.identity.aio import EnvironmentCredential
    except ImportError:
        pytest.skip("No azure identity library")
        return

    credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(fully_qualified_namespace=aad_credential_test_eh['hostname'],
                                             eventhub_name=aad_credential_test_eh['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    consumer_client = EventHubConsumerClient(fully_qualified_namespace=aad_credential_test_eh['hostname'],
                                             eventhub_name=aad_credential_test_eh['event_hub'],
                                             consumer_group='$default',
                                             credential=credential,
                                             user_agent='customized information')

    async with producer_client:
        batch = await producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        await producer_client.send_batch(batch)

    def on_event(partition_context, event):
        on_event.called = True
        on_event.partition_id = partition_context.partition_id
        on_event.event = event
    on_event.called = False
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event, partition_id='0', starting_position='-1'))
        await asyncio.sleep(13)
    await task
    assert on_event.called is True


#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import asyncio
import datetime
import time

from azure.identity.aio import EnvironmentCredential
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient, EventHubSharedKeyCredential
from azure.eventhub.aio._client_base_async import EventHubSASTokenCredential

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from tests.eventhub_preparer import (
    CachedEventHubNamespacePreparer, 
    CachedEventHubPreparer
)

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_secret_credential_async(live_eventhub):
    credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
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
    assert on_event.partition_id == "0"
    assert list(on_event.event.body)[0] == 'A single message'.encode('utf-8')


class AsyncEventHubAuthTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='eventhubtest')
    @CachedEventHubNamespacePreparer(name_prefix='eventhubtest')
    @CachedEventHubPreparer(name_prefix='eventhubtest')
    async def test_client_sas_credential_async(self,
                                   eventhub,
                                   eventhub_namespace,
                                   eventhub_namespace_key_name,
                                   eventhub_namespace_primary_key,
                                   eventhub_namespace_connection_string,
                                   **kwargs):
        # This should "just work" to validate known-good.
        hostname = "{}.servicebus.windows.net".format(eventhub_namespace.name)
        producer_client = EventHubProducerClient.from_connection_string(eventhub_namespace_connection_string, eventhub_name = eventhub.name)

        async with producer_client:
            batch = await producer_client.create_batch(partition_id='0')
            batch.add(EventData(body='A single message'))
            await producer_client.send_batch(batch)

        # This should also work, but now using SAS tokens.
        credential = EventHubSharedKeyCredential(eventhub_namespace_key_name, eventhub_namespace_primary_key)
        hostname = "{}.servicebus.windows.net".format(eventhub_namespace.name)
        auth_uri = "sb://{}/{}".format(hostname, eventhub.name)
        token = (await credential.get_token(auth_uri)).token
        producer_client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                                 eventhub_name=eventhub.name,
                                                 credential=EventHubSASTokenCredential(token, time.time() + 3000))

        async with producer_client:
            batch = await producer_client.create_batch(partition_id='0')
            batch.add(EventData(body='A single message'))
            await producer_client.send_batch(batch)

        # Finally let's do it with SAS token + conn str
        token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token.decode())
        conn_str_producer_client = EventHubProducerClient.from_connection_string(token_conn_str,
                                                                                 eventhub_name=eventhub.name)

        async with conn_str_producer_client:
            batch = await conn_str_producer_client.create_batch(partition_id='0')
            batch.add(EventData(body='A single message'))
            await conn_str_producer_client.send_batch(batch)

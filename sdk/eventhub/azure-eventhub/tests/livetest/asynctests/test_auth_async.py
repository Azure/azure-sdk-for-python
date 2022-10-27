#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import asyncio
import time

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.identity.aio import EnvironmentCredential
from azure.eventhub import EventData
from azure.eventhub.exceptions import ConnectError, AuthenticationError, EventHubError
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient, EventHubSharedKeyCredential
from azure.eventhub.aio._client_base_async import EventHubSASTokenCredential


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_secret_credential_async(live_eventhub, uamqp_transport):
    credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information',
                                             uamqp_transport=uamqp_transport
                                             )
    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$default',
                                             credential=credential,
                                             user_agent='customized information',
                                             uamqp_transport=uamqp_transport
                                             )

    async with producer_client:
        batch = await producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        await producer_client.send_batch(batch)

    async def on_event(partition_context, event):
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


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_sas_credential_async(live_eventhub, uamqp_transport):
    # This should "just work" to validate known-good.
    hostname = live_eventhub['hostname']
    producer_client = EventHubProducerClient.from_connection_string(live_eventhub['connection_str'],
                                                                    eventhub_name=live_eventhub['event_hub'], uamqp_transport=uamqp_transport)

    async with producer_client:
        batch = await producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        await producer_client.send_batch(batch)

    # This should also work, but now using SAS tokens.
    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub['event_hub'])
    token = (await credential.get_token(auth_uri)).token
    producer_client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=EventHubSASTokenCredential(token, time.time() + 3000),
                                             uamqp_transport=uamqp_transport)

    async with producer_client:
        batch = await producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        await producer_client.send_batch(batch)

    # Finally let's do it with SAS token + conn str
    token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token.decode())
    conn_str_producer_client = EventHubProducerClient.from_connection_string(token_conn_str,
                                                                             eventhub_name=live_eventhub['event_hub'], uamqp_transport=uamqp_transport)

    async with conn_str_producer_client:
        batch = await conn_str_producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        await conn_str_producer_client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_azure_sas_credential_async(live_eventhub, uamqp_transport):
    # This should "just work" to validate known-good.
    hostname = live_eventhub['hostname']
    producer_client = EventHubProducerClient.from_connection_string(live_eventhub['connection_str'], eventhub_name = live_eventhub['event_hub'], uamqp_transport=uamqp_transport)

    async with producer_client:
        batch = await producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        await producer_client.send_batch(batch)

    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub['event_hub'])
    token = (await credential.get_token(auth_uri)).token.decode()
    producer_client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=AzureSasCredential(token), uamqp_transport=uamqp_transport)

    async with producer_client:
        batch = await producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        await producer_client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_azure_named_key_credential_async(live_eventhub, uamqp_transport):

    credential = AzureNamedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                            eventhub_name=live_eventhub['event_hub'],
                                            consumer_group='$default',
                                            credential=credential,
                                            user_agent='customized information', uamqp_transport=uamqp_transport)

    assert (await consumer_client.get_eventhub_properties()) is not None

    credential.update("foo", "bar")

    with pytest.raises(Exception):
        await consumer_client.get_eventhub_properties()

    credential.update(live_eventhub['key_name'], live_eventhub['access_key'])
    assert (await consumer_client.get_eventhub_properties()) is not None

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_invalid_credential_async(live_eventhub, uamqp_transport):

    async def on_event(partition_context, event):
        pass

    async def on_error(partition_context, error):
        on_error.err = error

    env_credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(fully_qualified_namespace="fakeeventhub.servicebus.windows.net",
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             user_agent='customized information',
                                             retry_total=1,
                                             retry_mode='exponential',
                                             retry_backoff=0.02,
                                             uamqp_transport=uamqp_transport)
    consumer_client = EventHubConsumerClient(fully_qualified_namespace="fakeeventhub.servicebus.windows.net",
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             user_agent='customized information',
                                             consumer_group='$Default',
                                             retry_total=1,
                                             retry_mode='exponential',
                                             retry_backoff=0.02,
                                             uamqp_transport=uamqp_transport)
    async with producer_client:
        with pytest.raises(ConnectError):
            await producer_client.create_batch(partition_id='0')

    on_error.err = None
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event,
                                                                starting_position= "-1", on_error=on_error))
        await asyncio.sleep(15)
    await task
    assert isinstance(on_error.err, ConnectError)

    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name='fakehub',
                                             credential=env_credential,
                                             uamqp_transport=uamqp_transport)

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name='fakehub',
                                             credential=env_credential,
                                             consumer_group='$Default',
                                             retry_total=0,
                                             uamqp_transport=uamqp_transport)

    async with producer_client:
        with pytest.raises(ConnectError):
            await producer_client.create_batch(partition_id='0')

    on_error.err = None
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event,
                                                                starting_position= "-1", on_error=on_error))
        await asyncio.sleep(15)
    await task
    assert isinstance(on_error.err, AuthenticationError)
    
    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    token = (await credential.get_token(auth_uri)).token
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=EventHubSASTokenCredential(token, time.time() + 5),
                                             uamqp_transport=uamqp_transport)
    await asyncio.sleep(6)
    # expired credential
    async with producer_client:
        with pytest.raises(AuthenticationError):
            await producer_client.create_batch(partition_id='0')

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=EventHubSASTokenCredential(token, time.time() + 7),
                                             consumer_group='$Default',
                                             retry_total=0,
                                             uamqp_transport=uamqp_transport)
    on_error.err = None
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event,
                                                                starting_position= "-1", on_error=on_error))
        await asyncio.sleep(15)
    await task

    # expired credential
    assert isinstance(on_error.err, AuthenticationError)

    credential = EventHubSharedKeyCredential('fakekey', live_eventhub['access_key'])
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             uamqp_transport=uamqp_transport)

    async with producer_client:
        with pytest.raises(AuthenticationError):
            await producer_client.create_batch(partition_id='0')

    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             connection_verify="cacert.pem",
                                             uamqp_transport=uamqp_transport)
    
    # TODO: this seems like a bug from uamqp, should be ConnectError?
    async with producer_client:
        with pytest.raises(EventHubError):
            await producer_client.create_batch(partition_id='0')

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$Default',
                                             credential=env_credential,
                                             retry_total=0,
                                             connection_verify="cacert.pem",
                                             uamqp_transport=uamqp_transport)
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event,
                                                                starting_position= "-1", on_error=on_error))
        await asyncio.sleep(5)
    await task

    # TODO: this seems like a bug from uamqp, should be ConnectError?
    assert isinstance(on_error.err, FileNotFoundError)

    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             custom_endpoint_address="fakeaddr",
                                             uamqp_transport=uamqp_transport)

    async with producer_client:
        with pytest.raises(AuthenticationError):
            await producer_client.create_batch(partition_id='0')

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$Default',
                                             credential=env_credential,
                                             retry_total=0,
                                             custom_endpoint_address="fakeaddr",
                                             uamqp_transport=uamqp_transport)
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event,
                                                                starting_position= "-1", on_error=on_error))
        await asyncio.sleep(15)
    await task

    assert isinstance(on_error.err, AuthenticationError)
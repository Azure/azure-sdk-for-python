#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import pytest
import sys
import time

from azure.eventhub import (
    EventData,
    EventDataBatch,
)
from azure.identity.aio import EnvironmentCredential
from azure.eventhub.exceptions import (
    EventHubError,
    ConnectError,
    AuthenticationError,
    OperationTimeoutError
)
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient, EventHubSharedKeyCredential
from azure.eventhub.aio._client_base_async import EventHubSASTokenCredential


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_hostname_async(invalid_hostname, connstr_receivers, uamqp_transport):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - it keeps reporting 'Unable to set external certificates' "
                    "and blocking other tests")
    _, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)

    # test setting callback
    async def on_error(events, pid, err):
        assert len(events) == 1
        assert not pid
        on_error.err = err

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(invalid_hostname, on_error=on_error, uamqp_transport=uamqp_transport)
    async with client:
        batch = EventDataBatch()
        batch.add(EventData("test data"))
        await client.send_batch(batch)
    assert isinstance(on_error.err, ConnectError)

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(invalid_hostname, on_error=on_error, uamqp_transport=uamqp_transport)
    async with client:
        await client.send_event(EventData("test data"))
    assert isinstance(on_error.err, ConnectError)


@pytest.mark.parametrize("invalid_place",
                         ["hostname", "key_name", "access_key", "event_hub", "partition"])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_invalid_param_async(live_eventhub, invalid_place, uamqp_transport):
    eventhub_config = live_eventhub.copy()
    if invalid_place != "partition":
        eventhub_config[invalid_place] = "invalid " + invalid_place
    conn_str = live_eventhub["connection_str"].format(
        eventhub_config['hostname'],
        eventhub_config['key_name'],
        eventhub_config['access_key'],
        eventhub_config['event_hub'])

    client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group='$default', retry_total=0, uamqp_transport=uamqp_transport)

    async def on_event(partition_context, event):
        pass

    async with client:
        if invalid_place == "partition":
            task = asyncio.ensure_future(client.receive(on_event, partition_id=invalid_place,
                                         starting_position="-1"))
        else:
            task = asyncio.ensure_future(client.receive(on_event, partition_id="0",
                                                        starting_position="-1"))
        await asyncio.sleep(10)
        assert len(client._event_processors) == 1
    await task


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_key_async(invalid_key, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(invalid_key, uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_policy_async(invalid_policy, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(invalid_policy, uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_non_existing_entity_sender_async(connection_str, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(connection_str, eventhub_name="nemo", uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_to_invalid_partitions_async(connection_str, uamqp_transport):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
        try:
            with pytest.raises(ConnectError):
                batch = await client.create_batch(partition_id=p)
                batch.add(EventData("test data"))
                await client.send_batch(batch)
        finally:
            await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_too_large_message_async(connection_str, uamqp_transport):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    try:
        data = EventData(b"A" * 1100000)
        with pytest.raises(ValueError):
            batch = await client.create_batch()
            batch.add(data)
    finally:
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_null_body_async(connection_str, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    try:
        with pytest.raises(ValueError):
            data = EventData(None)
            batch = await client.create_batch()
            batch.add(data)
            await client.send_batch(batch)
    finally:
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_create_batch_with_invalid_hostname_async(invalid_hostname, uamqp_transport):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - it keeps reporting 'Unable to set external certificates' "
                    "and blocking other tests")
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(ConnectError):
            await client.create_batch(max_size_in_bytes=300)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_create_batch_with_too_large_size_async(connection_str, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(ValueError):
            await client.create_batch(max_size_in_bytes=5 * 1024 * 1024)

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_invalid_proxy_server(connection_str, uamqp_transport):
    if sys.platform.startswith('darwin') and uamqp_transport:
        pytest.skip("Skipping on OSX - running forever and blocking other tests")
    HTTP_PROXY = {
    'proxy_hostname': 'fakeproxy',  # proxy hostname.
    'proxy_port': 3128,  # proxy port.
    }

    client = EventHubProducerClient.from_connection_string(connection_str, http_proxy=HTTP_PROXY, uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(EventHubError):
            batch = await client.create_batch()

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_send_timeout(connstr_receivers, uamqp_transport):
    connection_str, receivers = connstr_receivers

    async def on_success(events, pid):
        pass

    async def on_error(events, pid, err):
        pass

    producer = EventHubProducerClient.from_connection_string(
        connection_str, uamqp_transport=uamqp_transport
    )

    async with producer:
        with pytest.raises(OperationTimeoutError):
            await producer.send_batch([EventData(b"Data")], timeout=-1)

        with pytest.raises(OperationTimeoutError):
            await producer.send_event(EventData(b"Data"), timeout=-1)

    producer = EventHubProducerClient.from_connection_string(
        connection_str,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport
    )

    async with producer:
        with pytest.raises(OperationTimeoutError):
            await producer.send_batch([EventData(b"Data")], timeout=-1)

        with pytest.raises(OperationTimeoutError):
            await producer.send_event(EventData(b"Data"), timeout=-1)

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_invalid_credential_async(live_eventhub, uamqp_transport, location):

    async def on_event(partition_context, event):
        pass

    async def on_error(partition_context, error):
        on_error.err = error

    env_credential = EnvironmentCredential()
    # Skipping on OSX - it's raising a ConnectionLostError and blocking other tests
    if not sys.platform.startswith('darwin'):
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
    await asyncio.sleep(15)
    # expired credential
    async with producer_client:
        with pytest.raises(AuthenticationError):
            await producer_client.create_batch(partition_id='0')

    # TODO: expired credential AuthenticationError not raised for east-asia/China regions
    if 'servicebus.windows.net' in live_eventhub['hostname']:
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

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             consumer_group='$Default',
                                             retry_total=0,
                                             uamqp_transport=uamqp_transport)
    on_error.err = None
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event,
                                                                starting_position= "-1", on_error=on_error))
        await asyncio.sleep(15)
    await task

    assert isinstance(on_error.err, AuthenticationError)

    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], 'fakekey')
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             uamqp_transport=uamqp_transport)

    async with producer_client:
        with pytest.raises(AuthenticationError):
            await producer_client.create_batch(partition_id='0')

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             consumer_group='$Default',
                                             retry_total=0,
                                             uamqp_transport=uamqp_transport)
    on_error.err = None
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event,
                                                                starting_position= "-1", on_error=on_error))
        await asyncio.sleep(15)
    await task

    assert isinstance(on_error.err, AuthenticationError)

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
        await asyncio.sleep(15)
    await task

    # TODO: this seems like a bug from uamqp, should be ConnectError?
    assert isinstance(on_error.err, FileNotFoundError)

    # Skipping on OSX - it's raising a ConnectionLostError
    if not sys.platform.startswith('darwin'):
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

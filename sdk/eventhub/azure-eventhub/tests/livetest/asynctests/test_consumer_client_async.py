import pytest
import asyncio

from azure.core.settings import settings
from azure.core.tracing import SpanKind
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.aio._eventprocessor.in_memory_checkpoint_store import InMemoryCheckpointStore
from azure.eventhub._constants import ALL_PARTITIONS


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_storage_checkpoint_async(connstr_senders, uamqp_transport, checkpoint_store_aio, live_eventhub, resource_mgmt_client):
    connection_str, senders = connstr_senders

    for i in range(10):
        senders[0].send(EventData("Test EventData"))
        senders[1].send(EventData("Test EventData"))

    try:
        await checkpoint_store_aio._container_client.create_container()
    except:
        pass

    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', checkpoint_store=checkpoint_store_aio, uamqp_transport=uamqp_transport)

    sequence_numbers_0 = []
    sequence_numbers_1 = []
    async def on_event(partition_context, event):
        await partition_context.update_checkpoint(event)
        sequence_num = event.sequence_number
        if partition_context.partition_id == "0":
            if sequence_num in sequence_numbers_0:
                assert False
            sequence_numbers_0.append(sequence_num)
        else:
            if sequence_num in sequence_numbers_1:
                assert False
            sequence_numbers_1.append(sequence_num)

    async with client:
        task = asyncio.ensure_future(
            client.receive(on_event, starting_position="-1"))
        # Update the eventhub
        eventhub = resource_mgmt_client.event_hubs.get(
            live_eventhub["resource_group"],
            live_eventhub["namespace"],
            live_eventhub["event_hub"]
        )
        properties = eventhub.as_dict()
        if properties["message_retention_in_days"] == 1:
            properties["message_retention_in_days"] = 2
        else:
            properties["message_retention_in_days"] = 1
        resource_mgmt_client.event_hubs.create_or_update(
            live_eventhub["resource_group"],
            live_eventhub["namespace"],
            live_eventhub["event_hub"],
            properties
        )
        await asyncio.sleep(10)

 
    await task
    assert len(sequence_numbers_0) == 10
    assert len(sequence_numbers_1) == 10

    try:
        await checkpoint_store_aio._container_client.delete_container()
    except:
        pass

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_no_partition_async(connstr_senders, uamqp_transport):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)

    async def on_event(partition_context, event):
        on_event.received += 1
        await partition_context.update_checkpoint(event)
        on_event.namespace = partition_context.fully_qualified_namespace
        on_event.eventhub_name = partition_context.eventhub_name
        on_event.consumer_group = partition_context.consumer_group
        on_event.offset = event.offset
        on_event.sequence_number = event.sequence_number

    on_event.received = 0

    on_event.namespace = None
    on_event.eventhub_name = None
    on_event.consumer_group = None
    on_event.offset = None
    on_event.sequence_number = None

    async with client:
        task = asyncio.ensure_future(
            client.receive(on_event, starting_position="-1"))
        await asyncio.sleep(10)
        assert on_event.received == 2

        checkpoints = await list(client._event_processors.values())[0]._checkpoint_store.list_checkpoints(
            on_event.namespace, on_event.eventhub_name, on_event.consumer_group
        )
        assert len([checkpoint for checkpoint in checkpoints if checkpoint["offset"] == on_event.offset]) > 0
        assert len(
            [checkpoint for checkpoint in checkpoints if checkpoint["sequence_number"] == on_event.sequence_number]) > 0

    await task


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_partition_async(connstr_senders, uamqp_transport):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)

    async def on_event(partition_context, event):
        assert partition_context.partition_id == "0"
        assert partition_context.consumer_group == "$default"
        assert partition_context.fully_qualified_namespace in connection_str
        assert partition_context.eventhub_name == senders[0]._client.eventhub_name
        on_event.received += 1

    on_event.received = 0
    async with client:
        task = asyncio.ensure_future(
            client.receive(on_event, partition_id="0", starting_position="-1"))
        await asyncio.sleep(10)
        assert on_event.received == 1
    await task


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_load_balancing_async(connstr_senders, uamqp_transport):
    connection_str, senders = connstr_senders
    cs = InMemoryCheckpointStore()
    client1 = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', checkpoint_store=cs, load_balancing_interval=1, uamqp_transport=uamqp_transport)
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', checkpoint_store=cs, load_balancing_interval=1, uamqp_transport=uamqp_transport)

    async def on_event(partition_context, event):
        pass

    async with client1, client2:
        task1 = asyncio.ensure_future(
            client1.receive(on_event, starting_position="-1"))
        await asyncio.sleep(3.3)
        task2 = asyncio.ensure_future(
            client2.receive(on_event, starting_position="-1"))
        await asyncio.sleep(20)
        assert len(client1._event_processors[("$default", ALL_PARTITIONS)]._tasks) == 1
        assert len(client2._event_processors[("$default", ALL_PARTITIONS)]._tasks) == 1
    await task1
    await task2


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_no_max_wait_time_async(connstr_senders, uamqp_transport):
    '''Test whether callback is called when max_wait_time is None and max_batch_size has reached
    '''
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)

    async def on_event_batch(partition_context, event_batch):
        on_event_batch.received += len(event_batch)
        await partition_context.update_checkpoint()
        on_event_batch.namespace = partition_context.fully_qualified_namespace
        on_event_batch.eventhub_name = partition_context.eventhub_name
        on_event_batch.consumer_group = partition_context.consumer_group
        on_event_batch.offset = event_batch[-1].offset
        on_event_batch.sequence_number = event_batch[-1].sequence_number

    on_event_batch.received = 0
    on_event_batch.namespace = None
    on_event_batch.eventhub_name = None
    on_event_batch.consumer_group = None
    on_event_batch.offset = None
    on_event_batch.sequence_number = None

    async with client:
        task = asyncio.ensure_future(
            client.receive_batch(on_event_batch, starting_position="-1"))
        await asyncio.sleep(10)
        assert on_event_batch.received == 2

        checkpoints = await list(client._event_processors.values())[0]._checkpoint_store.list_checkpoints(
            on_event_batch.namespace, on_event_batch.eventhub_name, on_event_batch.consumer_group
        )
        assert len([checkpoint for checkpoint in checkpoints if checkpoint["offset"] == on_event_batch.offset]) > 0
        assert len(
            [checkpoint for checkpoint in checkpoints if checkpoint["sequence_number"] == on_event_batch.sequence_number]) > 0

    await task


@pytest.mark.parametrize("max_wait_time, sleep_time, expected_result",
                         [(3, 15, []),
                          (3, 2, None),
                          ])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_empty_with_max_wait_time_async(connection_str, max_wait_time, sleep_time, expected_result, uamqp_transport):
    '''Test whether event handler is called when max_wait_time > 0 and no event is received
    '''
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)
    async def on_event_batch(partition_context, event_batch):
        on_event_batch.event_batch = event_batch

    on_event_batch.event_batch = None
    async with client:
        task = asyncio.ensure_future(
            client.receive_batch(on_event_batch, max_wait_time=max_wait_time, starting_position="-1"))
        await asyncio.sleep(sleep_time)
        assert on_event_batch.event_batch == expected_result

    await task


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_early_callback_async(connstr_senders, uamqp_transport):
    ''' Test whether the callback is called once max_batch_size reaches and before max_wait_time reaches.
    '''
    connection_str, senders = connstr_senders
    for _ in range(10):
        senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)

    async def on_event_batch(partition_context, event_batch):
        on_event_batch.received += len(event_batch)

    on_event_batch.received = 0

    async with client:
        task = asyncio.ensure_future(
            client.receive_batch(
                on_event_batch, max_batch_size=10, max_wait_time=100, starting_position="-1", partition_id="0"))
        await asyncio.sleep(10)
        assert on_event_batch.received == 10
    await task


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_tracing_async(connstr_senders, uamqp_transport, fake_span):
    """Test that that receive and process spans are properly created and linked."""
    settings.tracing_implementation.set_value(fake_span)
    connection_str, senders = connstr_senders

    with fake_span(name="SendSpan") as root_send:
        senders[0].send([EventData(b"Data"), EventData(b"Data")])

    assert len(root_send.children) == 3
    assert root_send.children[0].name == "EventHubs.message"
    assert root_send.children[1].name == "EventHubs.message"
    assert root_send.children[2].name == "EventHubs.send"
    assert len(root_send.children[2].links) == 2

    traceparent1 = root_send.children[2].links[0].headers['traceparent']
    traceparent2 = root_send.children[2].links[1].headers['traceparent']

    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)

    async def on_event_batch(partition_context, event_batch):
        on_event_batch.received += len(event_batch)

    on_event_batch.received = 0

    with fake_span(name="ReceiveSpan") as root_receive:
        async with client:
            task = asyncio.ensure_future(
                client.receive_batch(on_event_batch, max_batch_size=2, starting_position="-1"))
            await asyncio.sleep(10)
            assert on_event_batch.received == 2

        await task

    assert root_receive.name == "ReceiveSpan"
    # One receive span and one process span.
    assert len(root_receive.children) == 2

    assert root_receive.children[0].name == "EventHubs.receive"
    assert root_receive.children[0].kind == SpanKind.CLIENT

    # One link for each message in the batch.
    assert len(root_receive.children[0].links) == 2
    assert root_receive.children[0].links[0].headers['traceparent'] == traceparent1
    assert root_receive.children[0].links[1].headers['traceparent'] == traceparent2

    assert root_receive.children[1].name == "EventHubs.process"
    assert root_receive.children[1].kind == SpanKind.CONSUMER

    assert len(root_receive.children[1].links) == 2
    assert root_receive.children[1].links[0].headers['traceparent'] == traceparent1
    assert root_receive.children[1].links[1].headers['traceparent'] == traceparent2

    settings.tracing_implementation.set_value(None)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_large_event_async(connstr_senders, uamqp_transport):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("A" * 15700))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)

    async def on_event(partition_context, event):
        assert partition_context.partition_id == "0"
        assert partition_context.consumer_group == "$default"
        assert partition_context.fully_qualified_namespace in connection_str
        assert partition_context.eventhub_name == senders[0]._client.eventhub_name
        on_event.received += 1
        assert client._event_processors[0]._consumers[0]._handler._link.current_link_credit == 1

    on_event.received = 0
    async with client:
        task = asyncio.ensure_future(
            client.receive(on_event, partition_id="0", starting_position="-1", prefetch=2))
        await asyncio.sleep(10)
        assert on_event.received == 1
    await task
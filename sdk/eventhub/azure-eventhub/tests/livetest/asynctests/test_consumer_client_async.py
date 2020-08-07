import pytest
import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.aio._eventprocessor.in_memory_checkpoint_store import InMemoryCheckpointStore
from azure.eventhub._constants import ALL_PARTITIONS


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_no_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')

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
async def test_receive_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')

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
async def test_receive_load_balancing_async(connstr_senders):
    connection_str, senders = connstr_senders
    cs = InMemoryCheckpointStore()
    client1 = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', checkpoint_store=cs, load_balancing_interval=1)
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', checkpoint_store=cs, load_balancing_interval=1)

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
async def test_receive_batch_no_max_wait_time_async(connstr_senders):
    '''Test whether callback is called when max_wait_time is None and max_batch_size has reached
    '''
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')

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
                         [(3, 10, []),
                          (3, 2, None),
                          ])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_empty_with_max_wait_time_async(connection_str, max_wait_time, sleep_time, expected_result):
    '''Test whether event handler is called when max_wait_time > 0 and no event is received
    '''
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
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
async def test_receive_batch_early_callback_async(connstr_senders):
    ''' Test whether the callback is called once max_batch_size reaches and before max_wait_time reaches.
    '''
    connection_str, senders = connstr_senders
    for _ in range(10):
        senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')

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

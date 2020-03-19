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
        await asyncio.sleep(10)
        assert len(client1._event_processors[("$default", ALL_PARTITIONS)]._tasks) == 1
        assert len(client2._event_processors[("$default", ALL_PARTITIONS)]._tasks) == 1
    task1.cancel()
    task2.cancel()

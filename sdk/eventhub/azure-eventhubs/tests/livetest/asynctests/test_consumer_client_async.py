import pytest
import asyncio
from azure.eventhub import EventData, EventPosition
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.aio._eventprocessor.local_checkpoint_store import InMemoryCheckpointStore
from azure.eventhub._constants import ALL_PARTITIONS


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_no_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str)

    async def on_event(partition_context, event):
        on_event.received += 1

    on_event.received = 0
    async with client:
        task = asyncio.ensure_future(
            client.receive(on_event, consumer_group="$default", initial_event_position="-1"))
        await asyncio.sleep(10)
        assert on_event.received == 2
    task.cancel()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str)

    async def on_event(partition_context, event):
        assert partition_context.partition_id == "0"
        assert partition_context.consumer_group_name == "$default"
        assert partition_context.fully_qualified_namespace in connection_str
        assert partition_context.eventhub_name == senders[0]._client.eh_name
        on_event.received += 1

    on_event.received = 0
    async with client:
        task = asyncio.ensure_future(
            client.receive(on_event, consumer_group="$default", partition_id="0", initial_event_position="-1"))
        await asyncio.sleep(10)
        assert on_event.received == 1
    task.cancel()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_load_balancing_async(connstr_senders):
    connection_str, senders = connstr_senders
    cs = InMemoryCheckpointStore()
    client1 = EventHubConsumerClient.from_connection_string(
        connection_str, checkpoint_store=cs, load_balancing_interval=1)
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, checkpoint_store=cs, load_balancing_interval=1)

    async def on_event(partition_context, event):
        pass

    async with client1, client2:
        task1 = asyncio.ensure_future(
            client1.receive(on_event, consumer_group="$default", initial_event_position="-1"))
        task2 = asyncio.ensure_future(
            client2.receive(on_event, consumer_group="$default", initial_event_position="-1"))
        await asyncio.sleep(10)
        assert len(client1._event_processors[("$default", ALL_PARTITIONS)]._tasks) == 1
        assert len(client2._event_processors[("$default", ALL_PARTITIONS)]._tasks) == 1
    task1.cancel()
    task2.cancel()

import pytest
import asyncio
from azure.eventhub import EventData, EventPosition
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.aio.eventprocessor.local_partition_manager import InMemoryPartitionManager


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_no_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str)
    received = 0

    async def on_events(partition_context, events):
        nonlocal received
        received += len(events)

    async with client:
        task = asyncio.ensure_future(
            client.receive(on_events, consumer_group="$default", initial_event_position="-1"))
        await asyncio.sleep(10)
        assert received == 2
        # task.cancel()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str)
    received = 0

    async def on_events(partition_context, events):
        nonlocal received
        received += len(events)
        assert partition_context.partition_id == "0"
        assert partition_context.consumer_group_name == "$default"
        assert partition_context.fully_qualified_namespace in connection_str
        assert partition_context.eventhub_name == senders[0]._client.eh_name

    async with client:
        task = asyncio.ensure_future(
            client.receive(on_events, consumer_group="$default", partition_id="0", initial_event_position="-1"))
        await asyncio.sleep(10)
        assert received == 1
        # task.cancel()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_load_balancing_async(connstr_senders):
    connection_str, senders = connstr_senders
    pm = InMemoryPartitionManager()
    client1 = EventHubConsumerClient.from_connection_string(
        connection_str, partition_manager=pm, load_balancing_interval=1)
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, partition_manager=pm, load_balancing_interval=1)

    async def on_events(partition_context, events):
        pass

    async with client1, client2:
        task1 = asyncio.ensure_future(
            client1.receive(on_events, consumer_group="$default", initial_event_position="-1"))
        task2 = asyncio.ensure_future(
            client2.receive(on_events, consumer_group="$default", initial_event_position="-1"))
        await asyncio.sleep(10)
        assert len(client1._event_processors[("$default", "-1")]._tasks) == 1
        assert len(client2._event_processors[("$default", "-1")]._tasks) == 1
        # task1.cancel()
        # task2.cancel()

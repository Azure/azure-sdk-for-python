import time
import pytest
from azure.eventhub import EventData
from azure.eventhub import EventHubConsumerClient
from azure.eventhub._eventprocessor.local_partition_manager import InMemoryPartitionManager


@pytest.mark.liveTest
def test_receive_no_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str, network_tracing=False)
    received = 0

    def process_events(partition_context, events):
        nonlocal received
        received += len(events)

    with client:
        client.receive(process_events, consumer_group="$default", initial_event_position="-1")
        senders[0].send(EventData("Test EventData"))
        senders[1].send(EventData("Test EventData"))
        time.sleep(3)
        assert received == 2


@pytest.mark.liveTest
def test_receive_partition_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str, network_tracing=False)
    received = 0

    def process_events(partition_context, events):
        nonlocal received
        received += len(events)
        assert partition_context.partition_id == "0"
        assert partition_context.consumer_group_name == "$default"
        assert partition_context.fully_qualified_namespace in connection_str
        assert partition_context.eventhub_name == senders[0]._client.eh_name

    with client:
        client.receive(process_events, consumer_group="$default", partition_id="0", initial_event_position="-1")
        senders[0].send(EventData("Test EventData"))
        time.sleep(2)
        assert received == 1


@pytest.mark.liveTest
def test_receive_load_balancing_async(connstr_senders):
    connection_str, senders = connstr_senders
    pm = InMemoryPartitionManager()
    client1 = EventHubConsumerClient.from_connection_string(
        connection_str, partition_manager=pm, network_tracing=False, load_balancing_interval=1)
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, partition_manager=pm, network_tracing=False, load_balancing_interval=1)

    def process_events(partition_context, events):
        pass

    with client1 and client2:
        client1.receive(process_events, consumer_group="$default", initial_event_position="-1")
        client2.receive(process_events, consumer_group="$default", initial_event_position="-1")
        time.sleep(10)
        assert len(client1._event_processors[("$default", "-1")]._working_threads) == 1
        assert len(client2._event_processors[("$default", "-1")]._working_threads) == 1

import time
import pytest
import threading
from azure.eventhub import EventData
from azure.eventhub import EventHubConsumerClient
from azure.eventhub._eventprocessor.local_partition_manager import InMemoryPartitionManager


@pytest.mark.liveTest
def test_receive_no_partition(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, receive_timeout=1, network_tracing=False)

    recv_cnt = {"received": 0}  # substitution for nonlocal variable, 2.7 compatible

    def process_events(partition_context, events):
        recv_cnt["received"] += len(events)

    with client:
        worker = threading.Thread(target=client.receive,
                                  args=(process_events,),
                                  kwargs={"consumer_group": "$default", "initial_event_position": "-1"})
        worker.start()
        time.sleep(10)
        assert recv_cnt["received"] == 2


@pytest.mark.liveTest
def test_receive_partition(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(connection_str, network_tracing=False)

    recv_cnt = {"received": 0}  # substitution for nonlocal variable, 2.7 compatible

    def process_events(partition_context, events):
        recv_cnt["received"] += len(events)
        assert partition_context.partition_id == "0"
        assert partition_context.consumer_group_name == "$default"
        assert partition_context.fully_qualified_namespace in connection_str
        assert partition_context.eventhub_name == senders[0]._client.eh_name

    with client:
        worker = threading.Thread(target=client.receive,
                                  args=(process_events,),
                                  kwargs={"consumer_group": "$default", "initial_event_position": "-1",
                                          "partition_id": "0"})
        worker.start()
        time.sleep(10)
        assert recv_cnt["received"] == 1


@pytest.mark.liveTest
def test_receive_load_balancing(connstr_senders):
    connection_str, senders = connstr_senders
    pm = InMemoryPartitionManager()
    client1 = EventHubConsumerClient.from_connection_string(
        connection_str, partition_manager=pm, network_tracing=False, load_balancing_interval=1)
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, partition_manager=pm, network_tracing=False, load_balancing_interval=1)

    def process_events(partition_context, events):
        pass

    with client1, client2:
        worker1 = threading.Thread(target=client1.receive,
                                   args=(process_events,),
                                   kwargs={"consumer_group": "$default", "initial_event_position": "-1"})

        worker2 = threading.Thread(target=client2.receive,
                                   args=(process_events,),
                                   kwargs={"consumer_group": "$default", "initial_event_position": "-1"})

        worker1.start()
        worker2.start()
        time.sleep(20)
        assert len(client1._event_processors[("$default", "-1")]._working_threads) == 1
        assert len(client2._event_processors[("$default", "-1")]._working_threads) == 1

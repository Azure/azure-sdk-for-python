import time
import pytest
import threading
import sys
from azure.eventhub import EventData
from azure.eventhub import EventHubConsumerClient
from azure.eventhub._eventprocessor.in_memory_checkpoint_store import InMemoryCheckpointStore
from azure.eventhub._constants import ALL_PARTITIONS


@pytest.mark.parametrize("uamqp_transport",
                         [True, False])
@pytest.mark.liveTest
def test_receive_no_partition(connstr_senders, uamqp_transport):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(
        connection_str,
        consumer_group='$default',
        receive_timeout=1,
        uamqp_transport=uamqp_transport
    )

    def on_event(partition_context, event):
        on_event.received += 1
        partition_context.update_checkpoint(event)
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

    with client:
        worker = threading.Thread(target=client.receive,
                                  args=(on_event,),
                                  kwargs={"starting_position": "-1"})
        worker.start()
        time.sleep(20)
        assert on_event.received == 2
        checkpoints = list(client._event_processors.values())[0]._checkpoint_store.list_checkpoints(
            on_event.namespace, on_event.eventhub_name, on_event.consumer_group
        )
        assert len([checkpoint for checkpoint in checkpoints if checkpoint["offset"] == on_event.offset]) > 0
        assert len([checkpoint for checkpoint in checkpoints if checkpoint["sequence_number"] == on_event.sequence_number]) > 0


@pytest.mark.parametrize("uamqp_transport",
                         [True, False])
@pytest.mark.liveTest
def test_receive_partition(connstr_senders, uamqp_transport):
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', uamqp_transport=uamqp_transport
    )

    def on_event(partition_context, event):
        on_event.received += 1
        on_event.partition_id = partition_context.partition_id
        on_event.consumer_group = partition_context.consumer_group
        on_event.fully_qualified_namespace = partition_context.fully_qualified_namespace
        on_event.eventhub_name = partition_context.eventhub_name

    on_event.received = 0
    with client:
        worker = threading.Thread(target=client.receive,
                                  args=(on_event,),
                                  kwargs={"starting_position": "-1",
                                          "partition_id": "0"})
        worker.start()
        time.sleep(10)
        assert on_event.received == 1
        assert on_event.partition_id == "0"
        assert on_event.consumer_group == "$default"
        assert on_event.fully_qualified_namespace in connection_str
        assert on_event.eventhub_name == senders[0]._client.eventhub_name


@pytest.mark.parametrize("uamqp_transport",
                         [True, False])
@pytest.mark.liveTest
def test_receive_load_balancing(connstr_senders, uamqp_transport):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - test code using multiple threads. Sometimes OSX aborts python process")

    connection_str, senders = connstr_senders
    cs = InMemoryCheckpointStore()
    client1 = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', checkpoint_store=cs, load_balancing_interval=1, uamqp_transport=uamqp_transport
    )
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', checkpoint_store=cs, load_balancing_interval=1, uamqp_transport=uamqp_transport
    )

    def on_event(partition_context, event):
        pass

    with client1, client2:
        worker1 = threading.Thread(target=client1.receive,
                                   args=(on_event,),
                                   kwargs={"starting_position": "-1"})

        worker2 = threading.Thread(target=client2.receive,
                                   args=(on_event,),
                                   kwargs={"starting_position": "-1"})

        worker1.start()
        time.sleep(3.3)
        worker2.start()
        time.sleep(20)
        assert len(client1._event_processors[("$default", ALL_PARTITIONS)]._consumers) == 1
        assert len(client2._event_processors[("$default", ALL_PARTITIONS)]._consumers) == 1


@pytest.mark.parametrize("uamqp_transport",
                         [True, False])
def test_receive_batch_no_max_wait_time(connstr_senders, uamqp_transport):
    '''Test whether callback is called when max_wait_time is None and max_batch_size has reached
    '''
    connection_str, senders = connstr_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', uamqp_transport=uamqp_transport
    )

    def on_event_batch(partition_context, event_batch):
        on_event_batch.received += len(event_batch)
        partition_context.update_checkpoint()
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

    with client:
        worker = threading.Thread(target=client.receive_batch, args=(on_event_batch,),
                                  kwargs={"starting_position": "-1"})
        worker.start()
        time.sleep(20)
        assert on_event_batch.received == 2

        checkpoints = list(client._event_processors.values())[0]._checkpoint_store.list_checkpoints(
            on_event_batch.namespace, on_event_batch.eventhub_name, on_event_batch.consumer_group
        )
        assert len([checkpoint for checkpoint in checkpoints if checkpoint["offset"] == on_event_batch.offset]) > 0
        assert len(
            [checkpoint for checkpoint in checkpoints if checkpoint["sequence_number"] == on_event_batch.sequence_number]) > 0

    worker.join()


@pytest.mark.parametrize("max_wait_time, sleep_time, expected_result, uamqp_transport",
                         [(3, 10, [], True),
                          (3, 2, None, True),
                          (3, 10, [], False),
                          (3, 2, None, False),
                          ])
def test_receive_batch_empty_with_max_wait_time(connection_str, max_wait_time, sleep_time, expected_result, uamqp_transport):
    '''Test whether event handler is called when max_wait_time > 0 and no event is received
    '''
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)
    def on_event_batch(partition_context, event_batch):
        on_event_batch.event_batch = event_batch

    on_event_batch.event_batch = None
    with client:
        worker = threading.Thread(target=client.receive_batch, args=(on_event_batch,), kwargs={
            "max_wait_time": max_wait_time, "starting_position": "-1"
        })
        worker.start()
        time.sleep(sleep_time)
        assert on_event_batch.event_batch == expected_result
    worker.join()


@pytest.mark.parametrize("uamqp_transport",
                         [True, False])
def test_receive_batch_early_callback(connstr_senders, uamqp_transport):
    ''' Test whether the callback is called once max_batch_size reaches and before max_wait_time reaches.
    '''
    connection_str, senders = connstr_senders
    for _ in range(10):
        senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', uamqp_transport=uamqp_transport
    )

    def on_event_batch(partition_context, event_batch):
        on_event_batch.received += len(event_batch)

    on_event_batch.received = 0

    with client:
        worker = threading.Thread(target=client.receive_batch, args=(on_event_batch,), kwargs={
            "max_batch_size": 10, "max_wait_time": 100, "starting_position": "-1", "partition_id": "0"
        })
        worker.start()
        time.sleep(10)
        assert on_event_batch.received == 10
    worker.join()

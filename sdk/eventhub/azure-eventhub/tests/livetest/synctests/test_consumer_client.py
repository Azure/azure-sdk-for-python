import time
import pytest
import threading
import sys

from azure.eventhub import EventData
from azure.eventhub import EventHubConsumerClient
from azure.eventhub._eventprocessor.in_memory_checkpoint_store import (
    InMemoryCheckpointStore,
)
from azure.eventhub._constants import ALL_PARTITIONS


@pytest.mark.liveTest
def test_receive_storage_checkpoint(
    auth_credential_senders,
    uamqp_transport,
    checkpoint_store,
    live_eventhub,
    resource_mgmt_client,
):
    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders

    for i in range(10):
        senders[0].send(EventData("Test EventData"))
        senders[1].send(EventData("Test EventData"))

    try:
        checkpoint_store._container_client.create_container()
    except:
        pass

    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        checkpoint_store=checkpoint_store,
        uamqp_transport=uamqp_transport,
    )

    sequence_numbers_0 = []
    sequence_numbers_1 = []

    def on_event(partition_context, event):
        partition_context.update_checkpoint(event)
        sequence_num = event.sequence_number
        if partition_context.partition_id == "0":
            if sequence_num in sequence_numbers_0:
                assert False
            sequence_numbers_0.append(sequence_num)
        else:
            if sequence_num in sequence_numbers_1:
                assert False
            sequence_numbers_1.append(sequence_num)

    with client:
        worker = threading.Thread(target=client.receive, args=(on_event,), kwargs={"starting_position": "-1"})
        worker.start()

        # Update the eventhub
        eventhub = resource_mgmt_client.event_hubs.get(
            live_eventhub["resource_group"],
            live_eventhub["namespace"],
            live_eventhub["event_hub"],
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
            properties,
        )

        time.sleep(20)

    assert len(sequence_numbers_0) == 10
    assert len(sequence_numbers_1) == 10

    try:
        checkpoint_store._container_client.delete_container()
    except:
        pass


@pytest.mark.liveTest
def test_receive_no_partition(auth_credential_senders, uamqp_transport):
    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        receive_timeout=1,
        uamqp_transport=uamqp_transport,
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
        worker = threading.Thread(target=client.receive, args=(on_event,), kwargs={"starting_position": "-1"})
        worker.start()
        time.sleep(20)
        assert on_event.received == 2
        checkpoints = list(client._event_processors.values())[0]._checkpoint_store.list_checkpoints(
            on_event.namespace, on_event.eventhub_name, on_event.consumer_group
        )
        assert len([checkpoint for checkpoint in checkpoints if checkpoint["offset"] == on_event.offset]) > 0
        assert (
            len([checkpoint for checkpoint in checkpoints if checkpoint["sequence_number"] == on_event.sequence_number])
            > 0
        )


@pytest.mark.liveTest
def test_receive_partition(auth_credential_senders, uamqp_transport):
    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders
    senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        uamqp_transport=uamqp_transport,
    )

    def on_event(partition_context, event):
        on_event.received += 1
        on_event.partition_id = partition_context.partition_id
        on_event.consumer_group = partition_context.consumer_group
        on_event.fully_qualified_namespace = partition_context.fully_qualified_namespace
        on_event.eventhub_name = partition_context.eventhub_name

    on_event.received = 0
    with client:
        worker = threading.Thread(
            target=client.receive,
            args=(on_event,),
            kwargs={"starting_position": "-1", "partition_id": "0"},
        )
        worker.start()
        time.sleep(10)
        assert on_event.received == 1
        assert on_event.partition_id == "0"
        assert on_event.consumer_group == "$default"
        assert on_event.fully_qualified_namespace == fully_qualified_namespace
        assert on_event.eventhub_name == senders[0]._client.eventhub_name


@pytest.mark.liveTest
def test_receive_load_balancing(auth_credential_senders, uamqp_transport):
    if sys.platform.startswith("darwin"):
        pytest.skip("Skipping on OSX - test code using multiple threads. Sometimes OSX aborts python process")

    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders
    cs = InMemoryCheckpointStore()
    client1 = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        checkpoint_store=cs,
        load_balancing_interval=1,
        uamqp_transport=uamqp_transport,
    )
    client2 = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        checkpoint_store=cs,
        load_balancing_interval=1,
        uamqp_transport=uamqp_transport,
    )

    def on_event(partition_context, event):
        pass

    with client1, client2:
        worker1 = threading.Thread(target=client1.receive, args=(on_event,), kwargs={"starting_position": "-1"})

        worker2 = threading.Thread(target=client2.receive, args=(on_event,), kwargs={"starting_position": "-1"})

        worker1.start()
        time.sleep(3.3)
        worker2.start()
        time.sleep(20)
        assert len(client1._event_processors[("$default", ALL_PARTITIONS)]._consumers) == 1
        assert len(client2._event_processors[("$default", ALL_PARTITIONS)]._consumers) == 1


def test_receive_batch_no_max_wait_time(auth_credential_senders, uamqp_transport):
    """Test whether callback is called when max_wait_time is None and max_batch_size has reached"""
    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders
    senders[0].send(EventData("Test EventData"))
    senders[1].send(EventData("Test EventData"))
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        uamqp_transport=uamqp_transport,
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
        worker = threading.Thread(
            target=client.receive_batch,
            args=(on_event_batch,),
            kwargs={"starting_position": "-1"},
        )
        worker.start()
        time.sleep(20)
        assert on_event_batch.received == 2

        checkpoints = list(client._event_processors.values())[0]._checkpoint_store.list_checkpoints(
            on_event_batch.namespace,
            on_event_batch.eventhub_name,
            on_event_batch.consumer_group,
        )
        assert len([checkpoint for checkpoint in checkpoints if checkpoint["offset"] == on_event_batch.offset]) > 0
        assert (
            len(
                [
                    checkpoint
                    for checkpoint in checkpoints
                    if checkpoint["sequence_number"] == on_event_batch.sequence_number
                ]
            )
            > 0
        )

    worker.join()


@pytest.mark.parametrize("max_wait_time, sleep_time, expected_result", [(3, 15, []), (3, 2, None)])
def test_receive_batch_empty_with_max_wait_time(
    auth_credentials, uamqp_transport, max_wait_time, sleep_time, expected_result
):
    """Test whether event handler is called when max_wait_time > 0 and no event is received"""
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        uamqp_transport=uamqp_transport,
    )

    def on_event_batch(partition_context, event_batch):
        on_event_batch.event_batch = event_batch

    on_event_batch.event_batch = None
    with client:
        worker = threading.Thread(
            target=client.receive_batch,
            args=(on_event_batch,),
            kwargs={"max_wait_time": max_wait_time, "starting_position": "-1"},
        )
        worker.start()
        time.sleep(sleep_time)
        assert on_event_batch.event_batch == expected_result
    worker.join()


def test_receive_batch_early_callback(auth_credential_senders, uamqp_transport):
    """Test whether the callback is called once max_batch_size reaches and before max_wait_time reaches."""
    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders
    for _ in range(10):
        senders[0].send(EventData("Test EventData"))
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        uamqp_transport=uamqp_transport,
    )

    def on_event_batch(partition_context, event_batch):
        on_event_batch.received += len(event_batch)

    on_event_batch.received = 0

    with client:
        worker = threading.Thread(
            target=client.receive_batch,
            args=(on_event_batch,),
            kwargs={
                "max_batch_size": 10,
                "max_wait_time": 100,
                "starting_position": "-1",
                "partition_id": "0",
            },
        )
        worker.start()
        time.sleep(10)
        assert on_event_batch.received == 10
    worker.join()


@pytest.mark.liveTest
def test_receive_batch_tracing(auth_credential_senders, uamqp_transport):
    """Test that that receive and process spans are properly created and linked."""

    # TODO: Commenting out tracing for now. Need to fix this issue first: #36571
    # fake_span = enable_tracing
    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders

    # with fake_span(name="SendSpan") as root_send:
    senders[0].send([EventData(b"Data"), EventData(b"Data")])

    # assert len(root_send.children) == 3
    # assert root_send.children[0].name == "EventHubs.message"
    # assert root_send.children[1].name == "EventHubs.message"
    # assert root_send.children[2].name == "EventHubs.send"
    # assert len(root_send.children[2].links) == 2

    # traceparent1 = root_send.children[2].links[0].headers["traceparent"]
    # traceparent2 = root_send.children[2].links[1].headers["traceparent"]

    def on_event_batch(partition_context, event_batch):
        on_event_batch.received += len(event_batch)

    on_event_batch.received = 0

    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        uamqp_transport=uamqp_transport,
    )

    # with fake_span(name="ReceiveSpan") as root_receive:
    with client:
        worker = threading.Thread(
            target=client.receive_batch,
            args=(on_event_batch,),
            kwargs={"starting_position": "-1"},
        )
        worker.start()
        time.sleep(20)
        assert on_event_batch.received == 2

    worker.join()

    # assert root_receive.name == "ReceiveSpan"
    ## One receive span and one process span.
    # assert len(root_receive.children) == 2

    # assert root_receive.children[0].name == "EventHubs.receive"
    # assert root_receive.children[0].kind == SpanKind.CLIENT

    ## One link for each message in the batch.
    # assert len(root_receive.children[0].links) == 2
    # assert root_receive.children[0].links[0].headers["traceparent"] == traceparent1
    # assert root_receive.children[0].links[1].headers["traceparent"] == traceparent2

    # assert root_receive.children[1].name == "EventHubs.process"
    # assert root_receive.children[1].kind == SpanKind.CONSUMER

    # assert len(root_receive.children[1].links) == 2
    # assert root_receive.children[1].links[0].headers["traceparent"] == traceparent1
    # assert root_receive.children[1].links[1].headers["traceparent"] == traceparent2


@pytest.mark.liveTest
def test_receive_batch_large_event(auth_credential_senders, uamqp_transport):
    fully_qualified_namespace, eventhub_name, credential, senders = auth_credential_senders
    senders[0].send(EventData("A" * 15700))
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        uamqp_transport=uamqp_transport,
    )

    def on_event(partition_context, event):
        on_event.received += 1
        on_event.partition_id = partition_context.partition_id
        on_event.consumer_group = partition_context.consumer_group
        on_event.fully_qualified_namespace = partition_context.fully_qualified_namespace
        on_event.eventhub_name = partition_context.eventhub_name
        assert client._event_processors[0]._consumers[0]._handler._link.current_link_credit == 1

    on_event.received = 0
    with client:
        worker = threading.Thread(
            target=client.receive_batch,
            args=(on_event,),
            kwargs={"starting_position": "-1", "partition_id": "0", "prefetch": 2},
        )
        worker.start()
        time.sleep(10)
        assert on_event.received == 1
        assert on_event.partition_id == "0"
        assert on_event.consumer_group == "$default"
        assert on_event.fully_qualified_namespace == fully_qualified_namespace
        assert on_event.eventhub_name == senders[0]._client.eventhub_name

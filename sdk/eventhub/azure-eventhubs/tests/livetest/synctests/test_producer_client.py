import pytest
from azure.eventhub import EventData
from azure.eventhub import EventHubProducerClient


@pytest.mark.liveTest
def test_send_with_partition_key(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)

    with client:
        data_val = 0
        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(50):
                data = EventData(str(data_val))
                data_val += 1
                client.send(data, partition_key=partition_key)

    found_partition_keys = {}
    for index, partition in enumerate(receivers):
        received = partition.receive(timeout=5)
        for message in received:
            try:
                existing = found_partition_keys[message.partition_key]
                assert existing == index
            except KeyError:
                found_partition_keys[message.partition_key] = index


@pytest.mark.liveTest
def test_send_partition(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    with client:
        client.send(EventData(b"Data"), partition_id="1")

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1
    client.close()


@pytest.mark.liveTest
def test_send_no_partition_batch(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    with client:
        event_batch = client.create_batch()
        try:
            while True:
                event_batch.try_add(EventData(b"Data"))
        except ValueError:
            client.send(event_batch)

    partition_0 = receivers[0].receive(timeout=2)
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_0) + len(partition_1) > 10

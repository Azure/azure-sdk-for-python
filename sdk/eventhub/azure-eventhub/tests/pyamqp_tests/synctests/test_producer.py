import pytest

from azure.eventhub import EventHubProducerClient, EventData


@pytest.mark.liveTest
def test_send_batch_event(live_eventhub):
    client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    batch = client.create_batch()

    # large message that should be split into multiple transfer frames
    while True:
        try:
            batch.add(EventData(b'test'))
        except ValueError:
            break
    client.send_batch(batch)

    # small message that fits in one transfer frame
    batch = client.create_batch()
    for _ in range(100):
        batch.add(EventData(b'test' * 60))
    client.send_batch(batch)


@pytest.mark.liveTest
def test_send_batch_event_single_partition(live_eventhub):
    client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    batch = client.create_batch(partition_id="0")

    while True:
        try:
            batch.add(EventData(b'test'))
        except ValueError:
            break
    client.send_batch(batch)

    batch = client.create_batch()
    for _ in range(100):
        batch.add(EventData(b'test' * 60))
    client.send_batch(batch)
import pytest

from azure.eventhub import EventHubProducerClient, EventData


@pytest.mark.liveTest
def test_send_batch_event(live_eventhub):
    client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    batch = client.create_batch()

    # TODO: there is a bug that currently a batch message of size > 64*1024 could not be sent via a single transfer frame
    #  we probably need to support spliting a single message into multiple frames when the message is large (what uamqp library is doing)
    #  or check if tweaking link/session/connection frame settings allows us to send a large message
    # while True:
    #     try:
    #         batch.add(EventData(b'test'))
    #     except ValueError:
    #         break
    # client.send_batch(batch)

    for _ in range(100):
        batch.add(EventData(b'test' * 60))
    client.send_batch(batch)


@pytest.mark.liveTest
def test_send_batch_event(live_eventhub):
    client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    batch = client.create_batch(partition_id="0")

    # TODO: there is a bug that currently a batch message of size > 64*1024 could not be sent via a single transfer frame
    #  we probably need to support spliting a single message into multiple frames when the message is large (what uamqp library is doing)
    #  or check if tweaking link/session/connection frame settings allows us to send a large message
    # while True:
    #     try:
    #         batch.add(EventData(b'test'))
    #     except ValueError:
    #         break
    # client.send_batch(batch)

    for _ in range(100):
        batch.add(EventData(b'test' * 60))
    client.send_batch(batch)
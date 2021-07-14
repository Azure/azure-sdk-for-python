# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import threading
import time
import pytest

from azure.eventhub import EventHubConsumerClient, EventHubProducerClient, EventData


@pytest.mark.liveTest
def test_receive_from_single_partition(live_eventhub):
    producer_client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    consumer_client = EventHubConsumerClient.from_connection_string(live_eventhub["connection_str"], consumer_group=live_eventhub["consumer_group"])

    to_send_count = 10
    received_count = [0]

    def on_event(partition_context, event):
        received_count[0] += 1

    batch = producer_client.create_batch(partition_id="0")
    for _ in range(to_send_count):
        batch.add(EventData(b'data'))

    producer_client.send_batch(batch)

    thread = threading.Thread(
        target=consumer_client.receive,
        kwargs={
            "on_event": on_event,
            "partition_id": "0",
            "starting_position": "-1",  # "-1" is from the beginning of the partition.
        }
    )
    thread.daemon = True
    thread.start()
    time.sleep(15)
    consumer_client.close()
    thread.join()
    assert to_send_count == received_count[0]

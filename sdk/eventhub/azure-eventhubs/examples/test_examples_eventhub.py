#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import logging


def create_eventhub_client(live_eventhub_config):
    # [START create_eventhub_client]
    import os
    from azure.eventhub import EventHubClient, EventHubSharedKeyCredential

    host = os.environ['EVENT_HUB_HOSTNAME']
    event_hub_path = os.environ['EVENT_HUB_NAME']
    shared_access_policy = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key = os.environ['EVENT_HUB_SAS_KEY']

    client = EventHubClient(
        host=host,
        event_hub_path=event_hub_path,
        credential=EventHubSharedKeyCredential(shared_access_policy, shared_access_key)
    )
    # [END create_eventhub_client]
    return client


def test_example_eventhub_sync_send_and_receive(live_eventhub_config):
    # [START create_eventhub_client_connstr]
    import os
    from azure.eventhub import EventHubClient

    connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        os.environ['EVENT_HUB_HOSTNAME'],
        os.environ['EVENT_HUB_SAS_POLICY'],
        os.environ['EVENT_HUB_SAS_KEY'],
        os.environ['EVENT_HUB_NAME'])
    client = EventHubClient.from_connection_string(connection_str)
    # [END create_eventhub_client_connstr]

    from azure.eventhub import EventData, EventPosition

    # [START create_eventhub_client_sender]
    client = EventHubClient.from_connection_string(connection_str)
    # Create a producer.
    producer = client.create_producer(partition_id="0")
    # [END create_eventhub_client_sender]

    # [START create_eventhub_client_receiver]
    client = EventHubClient.from_connection_string(connection_str)
    # Create a consumer.
    consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    # Create an exclusive consumer object.
    exclusive_consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), owner_level=1)
    # [END create_eventhub_client_receiver]

    client = EventHubClient.from_connection_string(connection_str)
    producer = client.create_producer(partition_id="0")
    consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    try:
        consumer.receive(timeout=1)

        # [START create_event_data]
        event_data = EventData("String data")
        event_data = EventData(b"Bytes data")
        event_data = EventData([b"A", b"B", b"C"])

        list_data = ['Message {}'.format(i) for i in range(10)]
        event_data = EventData(body=list_data)
        # [END create_event_data]

        # [START eventhub_client_sync_create_batch]
        event_data_batch = producer.create_batch(max_size=10000)
        while True:
            try:
                event_data_batch.try_add(EventData('Message inside EventBatchData'))
            except ValueError:
                # The EventDataBatch object reaches its max_size.
                # You can send the full EventDataBatch object and create a new one here.
                break
        # [END eventhub_client_sync_create_batch]

        # [START eventhub_client_sync_send]
        with producer:
            event_data = EventData(b"A single event")
            producer.send(event_data)
        # [END eventhub_client_sync_send]
        time.sleep(1)

        # [START eventhub_client_sync_receive]
        with consumer:
            logger = logging.getLogger("azure.eventhub")
            received = consumer.receive(timeout=5, max_batch_size=1)
            for event_data in received:
                logger.info("Message received:{}".format(event_data.body_as_str()))
        # [END eventhub_client_sync_receive]
            assert len(received) > 0
            assert received[0].body_as_str() == "A single event"
            assert list(received[-1].body)[0] == b"A single event"
    finally:
        pass


def test_example_eventhub_producer_ops(live_eventhub_config, connection_str):
    from azure.eventhub import EventHubClient, EventData

    # [START eventhub_client_sender_close]
    client = EventHubClient.from_connection_string(connection_str)
    producer = client.create_producer(partition_id="0")
    try:
        producer.send(EventData(b"A single event"))
    finally:
        # Close down the send handler.
        producer.close()
    # [END eventhub_client_sender_close]


def test_example_eventhub_consumer_ops(live_eventhub_config, connection_str):
    from azure.eventhub import EventHubClient
    from azure.eventhub import EventPosition

    # [START eventhub_client_receiver_close]
    client = EventHubClient.from_connection_string(connection_str)
    consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    try:
        consumer.receive(timeout=1)
    finally:
        # Close down the receive handler.
        consumer.close()
    # [END eventhub_client_receiver_close]

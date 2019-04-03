#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import datetime
import os
import time
import logging
import asyncio

from azure.eventhub import EventHubError


def create_eventhub_client(live_eventhub_config):
    # [START create_eventhub_client]
    import os
    from azure.eventhub import EventHubClient

    address = os.environ['EVENT_HUB_ADDRESS']
    shared_access_policy = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key = os.environ['EVENT_HUB_SAS_KEY']

    client = EventHubClient(
        address=address,
        username=shared_access_policy,
        password=shared_access_key)
    # [END create_eventhub_client]
    return client


def create_eventhub_client_from_sas_token(live_eventhub_config):
    # [START create_eventhub_client_sas_token]
    import os
    from azure.eventhub import EventHubClient

    address = os.environ['EVENT_HUB_ADDRESS']
    sas_token = os.environ['EVENT_HUB_SAS_TOKEN']

    client = EventHubClient.from_sas_token(
        address=address,
        sas_token=sas_token)
    # [END create_eventhub_client_sas_token]


def create_eventhub_client_from_iothub_connection_string(live_eventhub_config):
    # [START create_eventhub_client_iot_connstr]
    import os
    from azure.eventhub import EventHubClient

    iot_connection_str = os.environ['IOTHUB_CONNECTION_STR']
    client = EventHubClient.from_iothub_connection_string(iot_connection_str)
    # [END create_eventhub_client_iot_connstr]


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

    from azure.eventhub import EventData, Offset

    # [START create_eventhub_client_sender]
    client = EventHubClient.from_connection_string(connection_str)    
    # Add a sender to the client object.
    sender = client.add_sender(partition="0")
    # [END create_eventhub_client_sender]

    # [START create_eventhub_client_receiver]
    client = EventHubClient.from_connection_string(connection_str)    
    # Add a receiver to the client object.
    receiver = client.add_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    # [END create_eventhub_client_receiver]

    # [START create_eventhub_client_epoch_receiver]
    client = EventHubClient.from_connection_string(connection_str)    
    # Add a receiver to the client object with an epoch value.
    epoch_receiver = client.add_epoch_receiver(consumer_group="$default", partition="0", epoch=42)
    # [END create_eventhub_client_epoch_receiver]

    # [START eventhub_client_run]
    client = EventHubClient.from_connection_string(connection_str)
    # Add Senders/Receivers
    try:
        client.run()
        # Start sending and receiving
    except:
        raise
    finally:
        client.stop()
    # [END eventhub_client_run]

    client = EventHubClient.from_connection_string(connection_str)
    sender = client.add_sender(partition="0")
    receiver = client.add_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    try:
        # Opens the connection and starts running all Sender/Receiver clients.
        client.run()
        # Start sending and receiving

        # [START create_event_data]
        event_data = EventData("String data")
        event_data = EventData(b"Bytes data")
        event_data = EventData([b"A", b"B", b"C"])

        def batched():
            for i in range(10):
                yield "Batch data, Event number {}".format(i)
        
        event_data = EventData(batch=batched())
        # [END create_event_data]

        # [START eventhub_client_sync_send]
        event_data = EventData(b"A single event")
        sender.send(event_data)
        # [END eventhub_client_sync_send]
        time.sleep(1)

        # [START eventhub_client_sync_receive]
        logger = logging.getLogger("azure.eventhub")
        received = receiver.receive(timeout=5, max_batch_size=1)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
        # [END eventhub_client_sync_receive]
        assert len(received) == 1
        assert received[0].body_as_str() == "A single event"
        assert list(received[-1].body)[0] == b"A single event"
    except:
        raise
    
    finally:
        client.stop()

    # [START eventhub_client_stop]
    client = EventHubClient.from_connection_string(connection_str)
    # Add Senders/Receivers
    try:
        client.run()
        # Start sending and receiving
    except:
        raise
    finally:
        client.stop()
    # [END eventhub_client_stop]


def test_example_eventhub_transfer(connection_str):
    import os
    from azure.eventhub import EventHubClient, EventData

    client = EventHubClient.from_connection_string(connection_str)
    sender = client.add_sender()

    try:
        client.run()
        # [START eventhub_client_transfer]
        logger = logging.getLogger("azure.eventhub")
        def callback(outcome, condition):
            logger.info("Message sent. Outcome: {}, Condition: {}".format(
                outcome, condition))

        event_data = EventData(b"A single event")
        sender.transfer(event_data, callback=callback)
        sender.wait()
        # [END eventhub_client_transfer]
    except:
        raise
    finally:
        client.stop()


def test_example_eventhub_sync_sender_ops(live_eventhub_config, connection_str):
    import os
    # [START create_eventhub_client_sender_instance]
    from azure.eventhub import EventHubClient

    client = EventHubClient.from_connection_string(connection_str)
    sender = client.add_sender(partition="0")
    # [END create_eventhub_client_sender_instance]

    # [START eventhub_client_sender_open]
    client = EventHubClient.from_connection_string(connection_str)
    sender = client.add_sender(partition="0")
    try:
        # Open the Sender using the supplied conneciton.
        sender.open()
        # Start sending
    except:
        raise
    finally:
        # Close down the send handler.
        sender.close()
    # [END eventhub_client_sender_open]

    # [START eventhub_client_sender_close]
    client = EventHubClient.from_connection_string(connection_str)
    sender = client.add_sender(partition="0")
    try:
        # Open the Sender using the supplied conneciton.
        sender.open()
        # Start sending
    except:
        raise
    finally:
        # Close down the send handler.
        sender.close()
    # [END eventhub_client_sender_close]    


def test_example_eventhub_sync_receiver_ops(live_eventhub_config, connection_str):
    import os
    # [START create_eventhub_client_receiver_instance]
    from azure.eventhub import EventHubClient, Offset

    client = EventHubClient.from_connection_string(connection_str)
    receiver = client.add_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    # [END create_eventhub_client_receiver_instance]

    # [START eventhub_client_receiver_open]
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client.add_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    try:
        # Open the Receiver using the supplied conneciton.
        receiver.open()
        # Start receiving
    except:
        raise
    finally:
        # Close down the receive handler.
        receiver.close()
    # [END eventhub_client_receiver_open]        

    # [START eventhub_client_receiver_close]
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client.add_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    try:
        # Open the Receiver using the supplied conneciton.
        receiver.open()
        # Start receiving
    except:
        raise
    finally:
        # Close down the receive handler.
        receiver.close()
    # [END eventhub_client_receiver_close]
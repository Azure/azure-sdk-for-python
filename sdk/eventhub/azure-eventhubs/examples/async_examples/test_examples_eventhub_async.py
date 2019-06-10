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

from azure.eventhub import EventHubError, EventData


@pytest.mark.asyncio
async def test_example_eventhub_async_send_and_receive(live_eventhub_config):
    # [START create_eventhub_client_async]
    from azure.eventhub.aio import EventHubClient
    import os
    connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        os.environ['EVENT_HUB_HOSTNAME'],
        os.environ['EVENT_HUB_SAS_POLICY'],
        os.environ['EVENT_HUB_SAS_KEY'],
        os.environ['EVENT_HUB_NAME'])    
    client = EventHubClient.from_connection_string(connection_str)
    # [END create_eventhub_client_async]

    from azure.eventhub import EventData, EventPosition

    # [START create_eventhub_client_async_sender]
    client = EventHubClient.from_connection_string(connection_str)
    # Add a async sender to the async client object.
    sender = client.create_sender(partition_id="0")
    # [END create_eventhub_client_async_sender]

    # [START create_eventhub_client_async_receiver]
    client = EventHubClient.from_connection_string(connection_str)
    # Add a async receiver to the async client object.
    receiver = client.create_receiver(partition_id="0", consumer_group="$default", event_position=EventPosition('@latest'))
    # [END create_eventhub_client_async_receiver]

    # [START create_eventhub_client_async_epoch_receiver]
    client = EventHubClient.from_connection_string(connection_str)
    # Add a async receiver to the async client object.
    epoch_receiver = client.create_receiver(consumer_group="$default", partition_id="0", exclusive_receiver_priority=42)
    # [END create_eventhub_client_async_epoch_receiver]

    client = EventHubClient.from_connection_string(connection_str)
    sender = client.create_sender(partition_id="0")
    receiver = client.create_receiver(partition_id="0", consumer_group="$default", event_position=EventPosition('@latest'))
    async with sender:
        # [START eventhub_client_async_send]
        event_data = EventData(b"A single event")
        await sender.send(event_data)
        # [END eventhub_client_async_send]
        time.sleep(1)
        # [START eventhub_client_async_receive]
        logger = logging.getLogger("azure.eventhub")
        async with receiver:
            received = await receiver.receive(timeout=5)
            for event_data in received:
                logger.info("Message received:{}".format(event_data.body_as_str()))
        # [END eventhub_client_async_receive]
            assert len(received) == 1
            assert received[0].body_as_str() == "A single event"
            assert list(received[-1].body)[0] == b"A single event"


@pytest.mark.asyncio
async def test_example_eventhub_async_sender_ops(live_eventhub_config, connection_str):
    import os
    # [START create_eventhub_client_async_sender_instance]
    from azure.eventhub.aio import EventHubClient
    from azure.eventhub import EventData

    client = EventHubClient.from_connection_string(connection_str)
    sender = client.create_sender(partition_id="0")
    # [END create_eventhub_client_async_sender_instance]

    # [START eventhub_client_async_sender_close]
    client = EventHubClient.from_connection_string(connection_str)
    sender = client.create_sender(partition_id="0")
    try:
        # Open the Async EventSender using the supplied conneciton and receive.
        await sender.send(EventData(b"A single event"))
    except:
        raise
    finally:
        # Close down the send handler.
        await sender.close()
    # [END eventhub_client_async_sender_close]


@pytest.mark.asyncio
async def test_example_eventhub_async_receiver_ops(live_eventhub_config, connection_str):
    import os
    # [START create_eventhub_client_async_receiver_instance]
    from azure.eventhub.aio import EventHubClient
    from azure.eventhub import EventPosition

    client = EventHubClient.from_connection_string(connection_str)
    receiver = client.create_receiver(partition_id="0", consumer_group="$default", event_position=EventPosition('@latest'))
    # [END create_eventhub_client_async_receiver_instance]

    # [START eventhub_client_async_receiver_open]
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client.create_receiver(partition_id="0", consumer_group="$default", event_position=EventPosition('@latest'))
    try:
        # Open and receive
        await receiver.receive(timeout=1)
    except:
        raise
    finally:
        # Close down the receive handler.
        await receiver.close()
    # [END eventhub_client_async_receiver_open]        

    # [START eventhub_client_async_receiver_close]
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client.create_receiver(partition_id="0", consumer_group="$default", event_position=EventPosition('@latest'))
    try:
        # Open and receive
        await receiver.receive(timeout=1)
    except:
        raise
    finally:
        # Close down the receive handler.
        await receiver.close()
    # [END eventhub_client_async_receiver_close]
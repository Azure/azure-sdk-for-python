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


@pytest.mark.asyncio
async def test_example_eventhub_async_send_and_receive(live_eventhub_config):
    # [START create_eventhub_client_async]
    from azure.eventhub import EventHubClientAsync
    import os
    connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        os.environ['EVENT_HUB_HOSTNAME'],
        os.environ['EVENT_HUB_SAS_POLICY'],
        os.environ['EVENT_HUB_SAS_KEY'],
        os.environ['EVENT_HUB_NAME'])    
    client = EventHubClientAsync.from_connection_string(connection_str)
    # [END create_eventhub_client_async]

    from azure.eventhub import EventData, Offset

    # [START create_eventhub_client_async_sender]
    client = EventHubClientAsync.from_connection_string(connection_str)
    # Add a async sender to the async client object.
    sender = client.add_async_sender(partition="0")
    # [END create_eventhub_client_async_sender]

    # [START create_eventhub_client_async_receiver]
    client = EventHubClientAsync.from_connection_string(connection_str)
    # Add a async receiver to the async client object.
    receiver = client.add_async_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    # [END create_eventhub_client_async_receiver]

    # [START create_eventhub_client_async_epoch_receiver]
    client = EventHubClientAsync.from_connection_string(connection_str)
    # Add a async receiver to the async client object.
    epoch_receiver = client.add_async_epoch_receiver(consumer_group="$default", partition="0", epoch=42)
    # [END create_eventhub_client_async_epoch_receiver]

    # [START eventhub_client_run_async]
    client = EventHubClientAsync.from_connection_string(connection_str)
    # Add AsyncSenders/AsyncReceivers
    try:
        # Opens the connection and starts running all AsyncSender/AsyncReceiver clients.
        await client.run_async()
        # Start sending and receiving
    except:
        raise
    finally:
        await client.stop_async()
    # [END eventhub_client_run_async]

    
    client = EventHubClientAsync.from_connection_string(connection_str)
    sender = client.add_async_sender(partition="0")
    receiver = client.add_async_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    try:
        # Opens the connection and starts running all AsyncSender/AsyncReceiver clients.
        await client.run_async()   

        # [START eventhub_client_async_send]
        event_data = EventData(b"A single event")
        await sender.send(event_data)
        # [END eventhub_client_async_send]
        time.sleep(1)
        # [START eventhub_client_async_receive]
        logger = logging.getLogger("azure.eventhub")
        received = await receiver.receive(timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
        # [END eventhub_client_async_receive]
        assert len(received) == 1
        assert received[0].body_as_str() == "A single event"
        assert list(received[-1].body)[0] == b"A single event"
    except:
        raise
    finally:
        await client.stop_async()

    # [START eventhub_client_async_stop]
    client = EventHubClientAsync.from_connection_string(connection_str)
    # Add AsyncSenders/AsyncReceivers
    try:
        # Opens the connection and starts running all AsyncSender/AsyncReceiver clients.
        await client.run_async()
        # Start sending and receiving
    except:
        raise
    finally:
        await client.stop_async()
    # [END eventhub_client_async_stop]


@pytest.mark.asyncio
async def test_example_eventhub_async_sender_ops(live_eventhub_config, connection_str):
    import os
    # [START create_eventhub_client_async_sender_instance]
    from azure.eventhub import EventHubClientAsync

    client = EventHubClientAsync.from_connection_string(connection_str)
    sender = client.add_async_sender(partition="0")
    # [END create_eventhub_client_async_sender_instance]

    # [START eventhub_client_async_sender_open]
    client = EventHubClientAsync.from_connection_string(connection_str)
    sender = client.add_async_sender(partition="0")
    try:
        # Open the Async Sender using the supplied conneciton.
        await sender.open_async()
        # Start sending
    except:
        raise
    finally:
        # Close down the send handler.
        await sender.close_async()
    # [END eventhub_client_async_sender_open]        

    # [START eventhub_client_async_sender_close]
    client = EventHubClientAsync.from_connection_string(connection_str)
    sender = client.add_async_sender(partition="0")
    try:
        # Open the Async Sender using the supplied conneciton.
        await sender.open_async()
        # Start sending
    except:
        raise
    finally:
        # Close down the send handler.
        await sender.close_async()
    # [END eventhub_client_async_sender_close]


@pytest.mark.asyncio
async def test_example_eventhub_async_receiver_ops(live_eventhub_config, connection_str):
    import os
    # [START create_eventhub_client_async_receiver_instance]
    from azure.eventhub import EventHubClientAsync, Offset

    client = EventHubClientAsync.from_connection_string(connection_str)
    receiver = client.add_async_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    # [END create_eventhub_client_async_receiver_instance]

    # [START eventhub_client_async_receiver_open]
    client = EventHubClientAsync.from_connection_string(connection_str)
    receiver = client.add_async_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    try:
        # Open the Async Receiver using the supplied conneciton.
        await receiver.open_async()
        # Start receiving
    except:
        raise
    finally:
        # Close down the receive handler.
        await receiver.close_async()
    # [END eventhub_client_async_receiver_open]        

    # [START eventhub_client_async_receiver_close]
    client = EventHubClientAsync.from_connection_string(connection_str)
    receiver = client.add_async_receiver(consumer_group="$default", partition="0", offset=Offset('@latest'))
    try:
        # Open the Async Receiver using the supplied conneciton.
        await receiver.open_async()
        # Start receiving
    except:
        raise
    finally:
        # Close down the receive handler.
        await receiver.close_async()
    # [END eventhub_client_async_receiver_close]
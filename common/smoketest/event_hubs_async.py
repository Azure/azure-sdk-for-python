# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from datetime import datetime
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient
from azure.eventhub import EventData

RECEIVE_TIMEOUT = 30
CONSUMER_GROUP = "$Default"
STARTING_POSITION = "-1"
TEST_EVENTS = [
    EventData(b"Test Event 1 in Python"),
    EventData(b"Test Event 2 in Python"),
    EventData(b"Test Event 3 in Python"),
]

class EventHubAsync:
    def __init__(self):
        # This test requires a previusly created Event Hub.
        # In this example the name is "myeventhub", but it could be change below
        connection_string = os.environ["EVENT_HUBS_CONNECTION_STRING"]
        event_hub_name = "myeventhub"
        self.consumer_client = EventHubConsumerClient.from_connection_string(
            connection_string, CONSUMER_GROUP, idle_timeout=RECEIVE_TIMEOUT
        )
        self.producer_client = EventHubProducerClient.from_connection_string(
            connection_string
        )

        self.received_event_count = 0

    async def get_partition_ids(self):
        print("Getting partitions id...")
        partition_ids = await self.consumer_client.get_partition_ids()
        print("\tdone")
        return partition_ids

    async def send_and_receive_events(self, partition_id):
        print("Sending events...")

        batch = await self.producer_client.create_batch(partition_id=partition_id)

        for event in TEST_EVENTS:
            batch.add(event)

        await self.producer_client.send_batch(batch)
        await self.producer_client.close()
        print("\tdone")

        print("Receiving events...")
        await self.consumer_client.receive(
            # on_event will close the consumer_client which resumes execution
            on_event=self.on_event,
            on_error=self.on_error,
            timeout=RECEIVE_TIMEOUT,
            starting_position=STARTING_POSITION
        )

        print("\tdone")

        if self.received_event_count < len(TEST_EVENTS):
            raise Exception(
                "Error, expecting {0} events, but {1} were received.".format(
                    str(len(TEST_EVENTS)), str(self.received_event_count)
                )
            )

    async def on_event(self, context, event):
        if self.received_event_count < len(TEST_EVENTS):
            self.received_event_count += 1
            print(event.body_as_str())
        else:
            # Close the client which allows execution to continue
            await self.close_client()

    async def on_error(self, context, error):
        await self.close_client()
        raise Exception("Received Error: {0}".format(error))

    async def close_client(self):
        await self.consumer_client.close()

    async def run(self):
        print("")
        print("------------------------")
        print("Event Hubs")
        print("------------------------")
        print("1) Get partition ID")
        print("2) Send Events")
        print("3) Consume Events")
        print("")

        partitionIDs = await self.get_partition_ids()
        # In this sample the same partition id is going to be used for the producer and consumer,
        # It is the first one, but it could be any (is not relevant as long as it is the same in both producer and consumer)
        await self.send_and_receive_events(partitionIDs[0])

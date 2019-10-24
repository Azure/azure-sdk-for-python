# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from datetime import datetime
from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData, EventPosition


class EventHub:
    def __init__(self):
        # This test requires a previusly created Event Hub.
        # In this example the name is "myeventhub", but it could be change below
        connection_string = os.environ["EVENT_HUBS_CONNECTION_STRING"]
        event_hub_name = "myeventhub"
        self.client = EventHubClient.from_connection_string(
            connection_string, event_hub_path=event_hub_name
        )

    async def get_partition_ids(self):
        print("Getting partitions id...")
        partition_ids = await self.client.get_partition_ids()
        print("\tdone")
        return partition_ids

    async def send_and_receive_events(self, partition_id):
        async with self.client.create_consumer(
            consumer_group="$default",
            partition_id=partition_id,
            event_position=EventPosition(datetime.utcnow()),
        ) as consumer:

            print("Sending events...")
            async with self.client.create_producer(
                partition_id=partition_id
            ) as producer:
                event_list = [
                    EventData(b"Test Event 1 in Python"),
                    EventData(b"Test Event 2 in Python"),
                    EventData(b"Test Event 3 in Python"),
                ]
                await producer.send(event_list)
            print("\tdone")

            print("Receiving events...")
            received = await consumer.receive(max_batch_size=len(event_list), timeout=2)
            for event_data in received:
                print("\tEvent Received: " + event_data.body_as_str())

            print("\tdone")

            if len(received) != len(event_list):
                raise Exception(
                    "Error, expecting {0} events, but {1} were received.".format(
                        str(len(event_list)), str(len(received))
                    )
                )

    async def run(self):
        print("")
        print("------------------------")
        print("Event Hubs")
        print("------------------------")
        print("1) Get partition ID")
        print("2) Send Events")
        print("3) Consume Events")
        print("")

        partition_id = await self.get_partition_ids()
        # In this sample the same partition id is going to be used for the producer and consumer,
        # It is the first one, but it could be any (is not relevant as long as it is the same in both producer and consumer)
        await self.send_and_receive_events(partition_id[0])

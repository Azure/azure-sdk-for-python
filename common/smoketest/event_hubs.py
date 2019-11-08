# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from datetime import datetime
from azure.eventhub import EventHubClient, EventData, EventPosition


class EventHub:
    def __init__(self):
        # This test requires a previusly created Event Hub.
        # In this example the name is "myeventhub", but it could be change below
        connection_string = os.environ["EVENT_HUBS_CONNECTION_STRING"]
        event_hub_name = "myeventhub"
        self.client = EventHubClient.from_connection_string(
            connection_string, event_hub_path=event_hub_name
        )

    def get_partition_ids(self):
        print("Getting partitions id...")
        partition_ids = self.client.get_partition_ids()
        print("\tdone")
        return partition_ids

    def send_and_receive_events(self, partitionID):
        with self.client.create_consumer(
            consumer_group="$default",
            partition_id=partitionID,
            event_position=EventPosition(datetime.utcnow()),
        ) as consumer:

            print("Sending events...")
            with self.client.create_producer(partition_id=partitionID) as producer:
                event_list = [
                    EventData(b"Test Event 1 in Python"),
                    EventData(b"Test Event 2 in Python"),
                    EventData(b"Test Event 3 in Python"),
                ]
                producer.send(event_list)
            print("\tdone")

            print("Receiving events...")
            received = consumer.receive(max_batch_size=len(event_list), timeout=3)
            for event_data in received:
                print("\tEvent Received: " + event_data.body_as_str())

            print("\tdone")

            if len(received) != len(event_list):
                raise Exception(
                    "Error, expecting {0} events, but {1} were received.".format(
                        str(len(event_list)), str(len(received))
                    )
                )

    def run(self):
        print("")
        print("------------------------")
        print("Event Hubs")
        print("------------------------")
        print("1) Get partition ID")
        print("2) Send Events")
        print("3) Consume Events")
        print("")

        partitionID = self.get_partition_ids()
        # In this sample the same partition id is going to be used for the producer and consumer,
        # It is the first one, but it could be any (is not relevant as long as it is the same in both producer and consumer)
        self.send_and_receive_events(partitionID[0])

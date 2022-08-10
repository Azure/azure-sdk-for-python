# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
from uuid import uuid4

from azure_devtools.perfstress_tests import BatchPerfTest, EventPerfTest, get_random_bytes
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient, EventData
from azure.eventhub.aio import (
    EventHubProducerClient as AsyncEventHubProducerClient,
    EventHubConsumerClient as AsyncEventHubConsumerClient
)


class _EventHubProcessorTest(EventPerfTest):
    consumer_group = '$Default'

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_EVENTHUB_CONNECTION_STRING")
        eventhub_name = self.get_from_env("AZURE_EVENTHUB_NAME")

        self.checkpoint_store = None
        self.async_checkpoint_store = None
        if arguments.use_storage_checkpoint:
            storage_connection_str = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")
            from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
            from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore as AsyncBlobCheckpointStore
            from azure.eventhub.extensions.checkpointstoreblobaio._vendor.storage.blob import BlobServiceClient
            self.container_name = "checkpointstore-" + str(uuid4())
            self.blob_service_client = BlobServiceClient.from_connection_string(storage_connection_str)
            self.checkpoint_store = BlobCheckpointStore.from_connection_string(storage_connection_str, self.container_name)
            self.async_checkpoint_store = AsyncBlobCheckpointStore.from_connection_string(storage_connection_str, self.container_name)

        self.consumer = EventHubConsumerClient.from_connection_string(
            connection_string,
            _EventHubProcessorTest.consumer_group,
            eventhub_name=eventhub_name,
            checkpoint_store=self.checkpoint_store,
            load_balancing_strategy=arguments.load_balancing_strategy
        )
        self.async_consumer = AsyncEventHubConsumerClient.from_connection_string(
            connection_string,
            _EventHubProcessorTest.consumer_group,
            eventhub_name=eventhub_name,
            checkpoint_store=self.async_checkpoint_store,
            load_balancing_strategy=arguments.load_balancing_strategy
        )
        if arguments.preload:
            self.async_producer = AsyncEventHubProducerClient.from_connection_string(connection_string, eventhub_name=eventhub_name)

    async def _preload_eventhub(self):
        data = get_random_bytes(self.args.event_size)
        async with self.async_producer as producer:
            partitions = await producer.get_partition_ids()
            for partition in partitions:
                properties = await producer.get_partition_properties(partition_id=partition)
                event_count = properties["last_enqueued_sequence_number"] - properties["beginning_sequence_number"]
                print(f"Detected {event_count} events in partition {partition}.")
                if event_count < self.args.preload:
                    events_to_add = self.args.preload - event_count
                    batch = await producer.create_batch(partition_id=partition)
                    for i in range(events_to_add):
                        try:
                            batch.add(EventData(data))
                        except ValueError:
                            # Batch full
                            await producer.send_batch(batch)
                            print(f"Loaded {i} of {events_to_add} events to partition {partition}.")
                            batch = await producer.create_batch()
                            batch.add(EventData(data))
                    await producer.send_batch(batch)
                    print(f"Finished loading {events_to_add} events to partition {partition}.")

    async def global_setup(self):
        await super().global_setup()
        if self.args.preload:
            await self._preload_eventhub()

    async def setup(self):
        """
        Create the checkpoint store Blob container before starting the Event processors.
        """
        if self.args.use_storage_checkpoint:
            await self.blob_service_client.create_container(self.container_name)
        await super().setup()

    async def cleanup(self):
        """
        Delete the checkpoint store Blob container after closing the Event processors.
        """
        await super().cleanup()
        if self.args.use_storage_checkpoint:
            await self.blob_service_client.delete_container(self.container_name)

    def stop_events_sync(self) -> None:
        """
        Stop the process for receiving events.
        """
        self.consumer.close()

    async def stop_events_async(self) -> None:
        """
        Stop the process for receiving events.
        """
        await self.async_consumer.close()

    @staticmethod
    def add_arguments(parser):
        super(_EventHubProcessorTest, _EventHubProcessorTest).add_arguments(parser)
        parser.add_argument('--event-size', nargs='?', type=int, help='Size of a single event. Defaults to 100 bytes', default=100)
        parser.add_argument('--prefetch-count', nargs='?', type=int, help='Number of events to receive locally per request. Defaults to 300', default=300)
        parser.add_argument('--load-balancing-strategy', nargs='?', type=str, help="Event Processor load balancing strategy, 'greedy' or 'balanced'. Default is 'greedy'.", default='greedy')
        parser.add_argument('--checkpoint-interval', nargs='?', type=int, help='Interval between checkpoints (in number of events).  Default is no checkpoints.', default=None)
        parser.add_argument('--max-wait-time', nargs='?', type=float, help='Maximum time to wait for an event to be received.', default=None)
        parser.add_argument('--processing-delay', nargs='?', type=int, help='Delay when processing each event (in ms).', default=None)
        parser.add_argument('--processing-delay-strategy', nargs='?', type=str, help="Whether to 'sleep' or 'spin' during processing delay. Default is 'sleep'.", default='sleep')
        parser.add_argument('--preload', nargs='?', type=int, help='Ensure the specified number of events are available in each partition. Default is 0.', default=0)
        parser.add_argument('--use-storage-checkpoint', action="store_true", help="Use Blob storage for checkpointing. Default is False (in-memory checkpointing).", default=False)


class _SendTest(BatchPerfTest):
    consumer_group = '$Default'

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_EVENTHUB_CONNECTION_STRING")
        eventhub_name = self.get_from_env("AZURE_EVENTHUB_NAME")
        self.producer = EventHubProducerClient.from_connection_string(
            connection_string,
            eventhub_name=eventhub_name
        )
        self.async_producer = AsyncEventHubProducerClient.from_connection_string(
            connection_string,
            eventhub_name=eventhub_name
        )

    async def setup(self):
        await super().setup()
        # First time calling create_batch would communicate with the service to
        # get the max allowed frame size on the link and the value will be cached.
        # Explicitly calling the method in setup to eliminate overhead in test run methods.
        self.producer.create_batch()
        await self.async_producer.create_batch()

    async def close(self):
        self.producer.close()
        await self.async_producer.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_SendTest, _SendTest).add_arguments(parser)
        parser.add_argument('--event-size', nargs='?', type=int, help='Size of event body (in bytes). Defaults to 100 bytes', default=100)
        parser.add_argument('--batch-size', nargs='?', type=int, help='The number of events that should be included in each batch. Defaults to 100', default=100)

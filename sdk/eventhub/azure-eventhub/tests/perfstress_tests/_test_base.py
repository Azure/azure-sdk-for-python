# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from uuid import uuid4

from azure_devtools.perfstress_tests import PerfStressTest, EventPerfTest, get_random_bytes
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
        if arguments.blob_storage:
            from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
            from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore as AsyncBlobCheckpointStore
            from azure.eventhub.extensions.checkpointstoreblobaio._vendor.storage.blob import BlobServiceClient
            self.container_name = "checkpointstore-" + str(uuid4())
            self.blob_service_client = BlobServiceClient.from_connection_string(arguments.blob_storage)
            self.checkpoint_store = BlobCheckpointStore.from_connection_string(arguments.blob_storage, self.container_name)
            self.async_checkpoint_store = AsyncBlobCheckpointStore.from_connection_string(arguments.blob_storage, self.container_name)

        self.consumer = EventHubConsumerClient.from_connection_string(
            connection_string,
            _EventHubProcessorTest.consumer_group,
            eventhub_name=eventhub_name
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
            batch = await producer.create_batch()
            for i in range(self.args.preload):
                try:
                    batch.add(EventData(data))
                except ValueError:
                    # Batch full
                    await producer.send_batch(batch)
                    print("Loaded {} events".format(i))
                    batch = await producer.create_batch()
                    batch.add(EventData(data))
            await producer.send_batch(batch)

    async def global_setup(self):
        await super().global_setup()
        if self.args.preload:
            await self._preload_eventhub()

    async def setup(self):
        """
        Create the checkpoint store Blob container before starting the Event processors.
        """
        if self.args.blob_storage:
            await self.blob_service_client.create_container(self.container_name)
        await super().setup()

    async def cleanup(self):
        """
        Delete the checkpoint store Blob container after closing the Event processors.
        """
        await super().cleanup()
        if self.args.blob_storage:
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
        parser.add_argument('--maximum-wait-time', nargs='?', type=float, help='Maximum time to wait for an event to be received.', default=None)
        parser.add_argument('--processing-delay', nargs='?', type=int, help='Delay when processing each event (in ms).', default=None)
        parser.add_argument('--processing-delay-strategy', nargs='?', type=str, help="Whether to 'sleep' or 'spin' during processing delay. Default is 'sleep'.", default='sleep')
        parser.add_argument('--preload', nargs='?', type=int, help='Number of events to preload. Default is 0.', default=0)
        parser.add_argument('--blob-storage', nargs='?', type=str, help='Connection string to a Blob Storage account to use Storage checkpoint store. Default is in-memory checkpoint store.', default=None)


class _EventHubTest(PerfStressTest):
    consumer_group = '$Default'

    @staticmethod
    def add_arguments(parser):
        super(_EventHubTest, _EventHubTest).add_arguments(parser)
        parser.add_argument('--event-size', nargs='?', type=int, help='Size of a single event. Defaults to 100 bytes', default=100)
        parser.add_argument('--num-events', nargs='?', type=int, help='Number of events to send or receive. Defaults to 100', default=100)


class _SendTest(_EventHubTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_EVENTHUB_CONNECTION_STRING")
        eventhub_name = self.get_from_env("AZURE_EVENTHUB_NAME")
        self.producer = EventHubProducerClient.from_connection_string(connection_string, eventhub_name=eventhub_name)
        self.async_producer = AsyncEventHubProducerClient.from_connection_string(connection_string, eventhub_name=eventhub_name)

    async def global_setup(self):
        await super().global_setup()
        # First time calling create_batch would communicate with the service to
        # get the max allowed frame size on the link and the value will be cached.
        # Explicitly calling the method in global_setup to eliminate overhead in test run methods.
        self.producer.create_batch()
        await self.async_producer.create_batch()

    async def close(self):
        self.producer.close()
        await self.async_producer.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_SendTest, _SendTest).add_arguments(parser)
        parser.add_argument('--num-events', nargs='?', type=int, help='Number of events to send or receive. Defaults to 100', default=100)



class _ReceiveTest(_EventHubTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_EVENTHUB_CONNECTION_STRING")
        eventhub_name = self.get_from_env("AZURE_EVENTHUB_NAME")
        self.async_producer = AsyncEventHubProducerClient.from_connection_string(connection_string, eventhub_name=eventhub_name)
        self.consumer = EventHubConsumerClient.from_connection_string(connection_string, _EventHubTest.consumer_group, eventhub_name=eventhub_name)
        self.async_consumer = AsyncEventHubConsumerClient.from_connection_string(connection_string, _EventHubTest.consumer_group, eventhub_name=eventhub_name)

    async def _preload_eventhub(self):
        data = get_random_bytes(self.args.event_size)
        async with self.async_producer as producer:
            batch = await producer.create_batch()
            for i in range(self.args.preload):
                try:
                    batch.add(EventData(data))
                except ValueError:
                    # Batch full
                    await producer.send_batch(batch)
                    print("Loaded {} events".format(i))
                    batch = await producer.create_batch()
                    batch.add(EventData(data))
            await producer.send_batch(batch)

    async def global_setup(self):
        await super().global_setup()
        await self._preload_eventhub()

    async def close(self):
        self.consumer.close()
        await self.async_consumer.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ReceiveTest, _ReceiveTest).add_arguments(parser)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for events before closing. Defaults to 60.', default=60)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of events to preload. Default is 10000.', default=10000)

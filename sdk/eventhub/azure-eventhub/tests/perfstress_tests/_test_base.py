# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import PerfStressTest, get_random_bytes
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient, EventData
from azure.eventhub.aio import (
    EventHubProducerClient as AsyncEventHubProducerClient,
    EventHubConsumerClient as AsyncEventHubConsumerClient
)


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
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='Max time to wait for events before closing. Defaults to 0.', default=60)
        parser.add_argument('--preload', nargs='?', type=int, help='Number of events to preload. Default is 10000.', default=10000)

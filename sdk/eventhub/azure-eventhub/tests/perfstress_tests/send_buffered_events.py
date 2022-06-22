# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import asyncio
from collections import defaultdict

from azure_devtools.perfstress_tests import EventPerfTest, get_random_bytes
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient, EventData
from azure.eventhub.aio import (
    EventHubProducerClient as AsyncEventHubProducerClient,
    EventHubConsumerClient as AsyncEventHubConsumerClient
)


class SendBufferedEventsTest(EventPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.event_size)
        connection_string = self.get_from_env("AZURE_EVENTHUB_CONNECTION_STRING")
        eventhub_name = self.get_from_env("AZURE_EVENTHUB_NAME")
        self.producer = EventHubProducerClient.from_connection_string(
            connection_string,
            eventhub_name=eventhub_name,
            buffered_mode=True,
            buffer_concurrency=self.args.max_concurrency,
            max_buffer_length=self.args.max_buffer_length,
            max_wait_time=self.args.max_wait_time,
            on_success=self.on_batch_success_sync,
            on_error=self.process_error_sync
        )
        self.async_producer = AsyncEventHubProducerClient.from_connection_string(
            connection_string,
            eventhub_name=eventhub_name,
            buffered_mode=True,
            buffer_concurrency=self.args.max_concurrency,
            max_buffer_length=self.args.max_buffer_length,
            max_wait_time=self.args.max_wait_time,
            on_success=self.on_batch_success_async,
            on_error=self.process_error_async
        )

    async def setup(self):
        # First time calling create_batch would communicate with the service to
        # get the max allowed frame size on the link and the value will be cached.
        # Explicitly calling the method in setup to eliminate overhead in test run methods.
        self.producer.create_batch()
        await self.async_producer.create_batch()
        await super().setup()

    def on_batch_success_sync(self, events, _):
        try:
            for _ in events:
                self.event_raised_sync()
        except Exception as e:
            self.error_raised_sync(e)

    async def on_batch_success_async(self, events, _):
        try:
            for _ in events:
                await self.event_raised_async()
        except Exception as e:
            await self.error_raised_async(e)

    def process_error_sync(self, *args):
        self.error_raised_sync(args[2])

    async def process_error_async(self, *args):
        await self.error_raised_async(args[2])

    def start_events_sync(self) -> None:
        """
        Start the process for receiving events.
        """
        if self.args.batch_size > 1:
            batch = self.producer.create_batch()
            for _ in range(self.args.batch_size):
                batch.add(EventData(self.data))
            self.producer.send_batch(batch)
        else:
            self.producer.send_event(EventData(self.data))

    async def start_events_async(self) -> None:
        """
        Start the process for receiving events.
        """
        if self.args.batch_size > 1:
            batch = await self.async_producer.create_batch()
            for _ in range(self.args.batch_size):
                batch.add(EventData(self.data))
            await self.async_producer.send_batch(batch)
        else:
            await self.async_producer.send_event(EventData(self.data))

    def stop_events_sync(self) -> None:
        """
        Stop the process for receiving events.
        """
        self.producer.close()

    async def stop_events_async(self) -> None:
        """
        Stop the process for receiving events.
        """
        await self.async_producer.close()

    async def close(self):
        self.producer.close()
        await self.async_producer.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(SendBufferedEventsTest, SendBufferedEventsTest).add_arguments(parser)
        parser.add_argument('--max-wait-time', nargs='?', type=int, help='The amount of time (in ms) to wait for a batch to be built with events in the buffer before publishing a partially full batch.', default=25)
        parser.add_argument('--max-buffer-length', nargs='?', type=int, help='The total number of events that can be buffered for publishing at a given time for a given partition.', default=1500)
        parser.add_argument('--max-concurrency', nargs='?', type=int, help='The total number of batches that may be sent concurrently, across all partitions.')
        parser.add_argument('--event-size', nargs='?', type=int, help='Size of event body (in bytes). Defaults to 100 bytes', default=100)
        parser.add_argument('--batch-size', nargs='?', type=int, help='The number of events that should be included in each batch. Defaults to 100', default=100)

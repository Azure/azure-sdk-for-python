# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import asyncio
from collections import defaultdict

from ._test_base import _EventHubProcessorTest


class ProcessEventsTest(_EventHubProcessorTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self._partition_event_count = defaultdict(int)

    def process_event_sync(self, partition_context, event):
        if event:
            if self.args.processing_delay:
                delay_in_seconds = self.args.processing_delay / 1000
                if self.args.processing_delay_strategy == 'sleep':
                    time.sleep(delay_in_seconds)
                elif self.args.processing_delay_strategy == 'spin':
                    starttime = time.time()
                    while (time.time() - starttime) < delay_in_seconds:
                        pass
            
            # Consume properties: this will load all the AMQP message application properties into
            # a decoded dictionary.
            _ = event.properties

            # Consume body: this will load the full message body content.
            _ = event.body

            if self.args.checkpoint_interval:
                self._partition_event_count[partition_context.partition_id] += 1
                if self._partition_event_count[partition_context.partition_id] >= self.args.checkpoint_interval:
                    partition_context.update_checkpoint(event)
                    self._partition_event_count[partition_context.partition_id] = 0
            try:
                self.event_raised_sync()
            except Exception as e:
                self.error_raised_sync(e)

    async def process_event_async(self, partition_context, event):
        if event:
            if self.args.processing_delay:
                delay_in_seconds = self.args.processing_delay / 1000
                if self.args.processing_delay_strategy == 'sleep':
                    await asyncio.sleep(delay_in_seconds)
                elif self.args.processing_delay_strategy == 'spin':
                    starttime = time.time()
                    while (time.time() - starttime) < delay_in_seconds:
                        pass
            
            # Consume properties: this will load all the AMQP message application properties into
            # a decoded dictionary.
            _ = event.properties

            # Consume body: this will load the full message body content.
            _ = event.body

            if self.args.checkpoint_interval:
                self._partition_event_count[partition_context.partition_id] += 1
                if self._partition_event_count[partition_context.partition_id] >= self.args.checkpoint_interval:
                    await partition_context.update_checkpoint(event)
                    self._partition_event_count[partition_context.partition_id] = 0
            try:
                await self.event_raised_async()
            except Exception as e:
                await self.error_raised_async(e)


    def process_error_sync(self, _, error):
        self.error_raised_sync(error)

    async def process_error_async(self, _, error):
        await self.error_raised_async(error)

    def start_events_sync(self) -> None:
        """
        Start the process for receiving events.
        """
        self.consumer.receive(
            on_event=self.process_event_sync,
            on_error=self.process_error_sync,
            max_wait_time=self.args.max_wait_time,
            prefetch=self.args.prefetch_count,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )

    async def start_events_async(self) -> None:
        """
        Start the process for receiving events.
        """
        await self.async_consumer.receive(
            on_event=self.process_event_async,
            on_error=self.process_error_async,
            max_wait_time=self.args.max_wait_time,
            prefetch=self.args.prefetch_count,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )

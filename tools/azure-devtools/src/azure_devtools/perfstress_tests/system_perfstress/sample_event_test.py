# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from azure_devtools.perfstress_tests import EventPerfTest


class MockEventProcessor():

    def __init__(self, partitions, process_event, process_error, error_after=None, max_events_per_second=None):
        self.partitions = partitions
        self.error_after = error_after
        self.max_events_per_second = max_events_per_second
        self.shutdown = False
        self._error_raised = False
        self._error_lock = threading.Lock()
        self._event_args = [{'partition': i, 'data': 'hello'} for i in range(self.partitions)]
        self._events_raised = [0] * self.partitions
        self._starttime = None
        self._process_event = process_event
        self._process_error = process_error
        self._executor = ThreadPoolExecutor(max_workers=self.partitions)
    
    def _process_error_after(self, partition):
        with self._error_lock:
            if not self._error_raised:
                error = Exception("Raising error after {} seconds.".format(self.error_after))
                self._process_error(partition=partition, error=error)
                self._error_raised = True

    def start_processing(self):
        self._starttime = time.time()
        with self._executor as ex:
            futures = [ex.submit(self._process, p) for p in range(self.partitions)]
            for future in as_completed(futures):
                future.result()

    def _process(self, partition):
        event_args = self._event_args[partition]
        if self.max_events_per_second:
            max_events_per_partition = float(self.max_events_per_second) / self.partitions
            while not self.shutdown:
                elapsed = time.time() - self._starttime
                if self.error_after and not self._error_raised and elapsed > self.error_after:
                    self._process_error_after(partition)
                else:
                    target_events = elapsed * max_events_per_partition
                    if self._events_raised[partition] < target_events:
                        self._process_event(**event_args)
                        self._events_raised[partition] += 1
                    else:
                        time.sleep(1 / max_events_per_partition)
        else:
            while not self.shutdown:
                elapsed = time.time() - self._starttime
                if self.error_after and not self._error_raised and elapsed > self.error_after:
                    self._process_error_after(partition)
                else:
                    self._process_event(**event_args)


class AsyncMockEventProcessor():

    def __init__(self, partitions, process_event, process_error, error_after=None, max_events_per_second=None):
        self.partitions = partitions
        self.error_after = error_after
        self.max_events_per_second = max_events_per_second
        self.shutdown = False
        self._error_raised = False
        self._error_lock = asyncio.Lock()
        self._starttime = None
        self._process_event = process_event
        self._process_error = process_error
        self._event_args = [{'partition': i, 'data': 'hello'} for i in range(self.partitions)]
        self._events_raised = [0] * self.partitions

    async def _process_error_after(self, partition):
        async with self._error_lock:
            if not self._error_raised:
                error = Exception("Raising error after {} seconds.".format(self.error_after))
                await self._process_error(partition=partition, error=error)
                self._error_raised = True

    async def start_processing(self):
        self._starttime = time.time()
        await asyncio.gather(*[self._process(i) for i in range(self.partitions)])

    async def _process(self, partition):
        event_args = self._event_args[partition]
        sleep_count = 0
        if self.max_events_per_second:
            max_events_per_partition = float(self.max_events_per_second) / self.partitions
            while not self.shutdown:
                sleep_count += 1
                elapsed = time.time() - self._starttime
                if self.error_after and not self._error_raised and elapsed > self.error_after:
                    await self._process_error_after(partition)
                else:
                    target_events = elapsed * max_events_per_partition
                    if self._events_raised[partition] < target_events:
                        await self._process_event(**event_args)
                        self._events_raised[partition] += 1
                    else:
                        await asyncio.sleep(1 / max_events_per_partition)
                await asyncio.sleep(0)
        else:
            while not self.shutdown:
                sleep_count += 1
                elapsed = time.time() - self._starttime
                if self.error_after and not self._error_raised and elapsed > self.error_after:
                    await self._process_error_after(partition)
                else:
                    await self._process_event(**event_args)
                if sleep_count % 500 == 0:
                    await asyncio.sleep(0)


class SampleEventTest(EventPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # Setup service clients
        self.event_processor = MockEventProcessor(
            self.args.partitions,
            self.process_event_sync,
            self.process_error_sync,
            error_after=self.args.error_after_seconds,
            max_events_per_second=self.args.max_events_per_second
        )
        self.async_event_processor = AsyncMockEventProcessor(
            self.args.partitions,
            self.process_event_async,
            self.process_error_async,
            error_after=self.args.error_after_seconds,
            max_events_per_second=self.args.max_events_per_second
        )

    def process_event_sync(self, **kwargs):
        self.event_raised_sync()

    def process_error_sync(self, error=None, **kwargs):
        self.error_raised_sync(error)

    async def process_event_async(self, **kwargs):
        await self.event_raised_async()

    async def process_error_async(self, error=None, **kwargs):
        await self.error_raised_async(error)

    def start_events_sync(self) -> None:
        """
        Start the process for receiving events.
        """
        self.event_processor.start_processing()

    def stop_events_sync(self) -> None:
        """
        Stop the process for receiving events.
        """
        self.event_processor.shutdown = True

    async def start_events_async(self) -> None:
        """
        Start the process for receiving events.
        """
        await self.async_event_processor.start_processing()

    async def stop_events_async(self) -> None:
        """
        Stop the process for receiving events.
        """
        self.async_event_processor.shutdown = True
    
    @staticmethod
    def add_arguments(parser):
        super(SampleEventTest, SampleEventTest).add_arguments(parser)
        parser.add_argument('--error-after-seconds', nargs='?', type=int, help='Raise error after this number of seconds.')
        parser.add_argument('--max-events-per-second', nargs='?', type=int, help='Maximum events per second across all partitions.')
        parser.add_argument('--partitions', nargs='?', type=int, help="Number of partitions. Default is 8.", default=8)

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import threading
import time

from ._repeated_timer import AtomicCounter
from ._perf_stress_base import _PerfTestBase


class EventPerfTest(_PerfTestBase):

    def __init__(self, arguments):
        super().__init__(arguments)
        if self.args.profile:
            raise NotImplementedError("Profiler support for event tests pending.")

        if self.args.sync:
            self._condition = threading.Condition()
        else:
            self._condition = asyncio.Condition()
        self._start_time = time.time()
        self._error = None
        self._processing = None
        self._completed_operations = AtomicCounter()

    @property
    def completed_operations(self) -> int:
        """
        Total number of operations completed by run_all().
        Reset after warmup.
        """
        return self._completed_operations.value()

    @property
    def last_completion_time(self) -> float:
        """
        Elapsed time between start of warmup/run and last completed operation.
        Reset after warmup.
        """
        return self._last_completion_time - self._start_time

    def event_raised_sync(self):
        self._completed_operations.increment()
        self._last_completion_time = time.time()

    def error_raised_sync(self, error):
        with self._condition:
            self._error = error
            self._condition.notify_all()

    async def event_raised_async(self):
        self._completed_operations.increment()
        self._last_completion_time = time.time()

    async def error_raised_async(self, error):
        async with self._condition:
            self._error = error
            self._condition.notify_all()

    async def setup(self) -> None:
        """
        Setup called once per parallel test instance.
        Used to setup state specific to this test instance.
        """
        if self.args.sync:
            self._processing = threading.Thread(target=self.start_events_sync)
            self._processing.daemon = True
            self._processing.start()
        else:
            self._processing = asyncio.ensure_future(self.start_events_async())

    async def cleanup(self) -> None:
        """
        Cleanup called once per parallel test instance.
        Used to cleanup state specific to this test instance.
        """
        if self.args.sync:
            self.stop_events_sync()
            self._processing.join()
        else:
            await self.stop_events_async()
            await self._processing
        try:
            raise self._error
        except TypeError:
            pass

    def run_all_sync(self, duration: int) -> None:
        """
        Run all sync tests, including both warmup and duration.
        """
        with self._condition:
            self._completed_operations.reset()
            self._last_completion_time = 0.0
            self._start_time = time.time()
            self._condition.wait(timeout=duration)

    async def run_all_async(self, duration: int) -> None:
        """
        Run all async tests, including both warmup and duration.
        """
        async with self._condition:
            self._completed_operations.reset()
            self._last_completion_time = 0.0
            self._start_time = time.time()
            try:
                await asyncio.wait_for(self._condition.wait(), timeout=duration)
            except asyncio.TimeoutError:
                pass

    def start_events_sync(self) -> None:
        """
        Start the process for receiving events.
        """
        raise NotImplementedError("start_events_sync must be implemented for {}".format(self.__class__.__name__))

    def stop_events_sync(self) -> None:
        """
        Stop the process for receiving events.
        """
        raise NotImplementedError("stop_events_sync must be implemented for {}".format(self.__class__.__name__))

    async def start_events_async(self) -> None:
        """
        Start the process for receiving events.
        """
        raise NotImplementedError("start_events_async must be implemented for {}".format(self.__class__.__name__))

    async def stop_events_async(self) -> None:
        """
        Stop the process for receiving events.
        """
        raise NotImplementedError("stop_events_async must be implemented for {}".format(self.__class__.__name__))

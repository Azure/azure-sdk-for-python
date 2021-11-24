# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import cProfile
import os
import asyncio
import threading
import time
from typing import Optional, Any, Dict, List

from urllib.parse import urljoin

from ._perf_stress_base import _PerfTestBase
from ._policies import PerfTestProxyPolicy


class EventPerfTest(_PerfTestBase):

    def __init__(self, arguments):
        super().__init__(arguments)
        self._thread_lock = threading.Lock()
        self._thread_condition = threading.Condition()
        self._async_lock = asyncio.Lock()
        self._async_condition = asyncio.Condition()
        self._start_time = None
        self._duration = None
        self._error = None

    def event_raised_sync(self, *args, **kwargs):
        with self._thread_lock:
            self._completed_operations += 1
            self._last_completion_time = time.time() - self._start_time
    
    def error_raised_sync(self, *args, **kwargs):
        self._error = True

    async def event_raised_async(self, *args, **kwargs):
        async with self._async_lock:
            self._completed_operations += 1
            self._last_completion_time = time.time() - self._start_time

    async def error_raised_async(self, *args, **kwargs):
        self._error = True
    
    def shutdown_condition(self):
        return self._error or self._last_completion_time >= self._duration

    def run_all_sync(self, duration: int) -> None:
        """
        Run all sync tests, including both warmup and duration.
        """
        self._completed_operations = 0
        self._last_completion_time = 0.0
        self._start_time = time.time()
        self._duration = duration
        if self.args.profile:
            raise NotImplementedError("Profiler support for event tests pending.")
        else:
            with self._thread_condition:
                thread = threading.Thread(target=self.start_events_sync)
                thread.daemon = True
                thread.start()
                self._thread_condition.wait_for(self.shutdown_condition)
                self.stop_events_sync()
                thread.join()
        try:
            raise self._error
        except TypeError:
            pass

    async def run_all_async(self, duration: int) -> None:
        """
        Run all async tests, including both warmup and duration.
        """
        self._completed_operations = 0
        self._last_completion_time = 0.0
        self._start_time = time.time()
        self._duration = duration
        if self.args.profile:
            raise NotImplementedError("Profiler support for event tests pending.")
        else:
            async with self._async_condition:
                task = asyncio.ensure_future(self.start_events_async())
                await self._async_condition.wait_for(self.shutdown_condition)
                await self.stop_events_async()
                await task
        try:
            raise self._error
        except TypeError:
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

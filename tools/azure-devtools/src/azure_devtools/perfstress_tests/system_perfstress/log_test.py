# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import asyncio

from azure_devtools.perfstress_tests import PerfStressTest

# Used for logging every step and property of the perf test
class LogTest(PerfStressTest):
    _logged_global_completed_operations = 0

    start_time = time.time()

    def __init__(self, arguments):
        super().__init__(arguments)
        self._seconds_per_operation = 1.0 / (self._parallel_index + 1)
        self._logged_completed_operations = 0
        self.log("__init__()")

    async def global_setup(self):
        await super().global_setup()
        self.log("global_setup()")

    async def setup(self):
        await super().setup()
        self.log("setup()")

    def run_sync(self):
        time.sleep(self._seconds_per_operation)
        self._logged_completed_operations += 1
        type(self)._logged_global_completed_operations += 1

    async def run_async(self):
        await asyncio.sleep(self._seconds_per_operation)
        self._logged_completed_operations += 1
        type(self)._logged_global_completed_operations += 1

    async def cleanup(self):
        await super().cleanup()
        self.log(f'cleanup() - Completed Operations: {self._logged_completed_operations}')

    async def global_cleanup(self):
        await super().global_cleanup()
        self.log(f'global_cleanup() - Global Completed Operations: {self._logged_global_completed_operations}')

    def log(self, message):
        print(f'[{(time.time() - type(self).start_time):.3f}] [PID: {os.getpid()}] [Parallel: {self._parallel_index}] {message}')

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
from azure_devtools.perfstress_tests import PerfStressTest


class NoOpTest(PerfStressTest):
    def run_sync(self):
        pass

    async def run_async(self):
        # Yield on each call to avoid blocking the event loop.  Also simulates a real call to async IO.
        # Reduces throughput by almost a factor of 10 (1.3M vs 160k ops/sec), but allows for parallel execution
        # and should more accurately represent real-world async performance.
        await asyncio.sleep(0)

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import math
import time
import asyncio

from azure_devtools.perfstress_tests import PerfStressTest


# Used for verifying the perf framework correctly computes average throughput across parallel tests of different speed
class SleepTest(PerfStressTest):
    instance_count = 0

    def __init__(self, arguments):
        type(self).instance_count += 1
        self.seconds_per_operation = math.pow(2, type(self).instance_count)

    def run_sync(self):
        time.sleep(self.seconds_per_operation)

    async def run_async(self):
        await asyncio.sleep(self.seconds_per_operation)

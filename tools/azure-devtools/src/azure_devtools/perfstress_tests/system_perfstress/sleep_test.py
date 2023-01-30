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

    def __init__(self, arguments):
        super().__init__(arguments)
        self.seconds_per_operation = (self.args.initial_delay_ms / 1000) * math.pow(self.args.instance_growth_factor, self._parallel_index)

    def run_sync(self):
        time.sleep(self.seconds_per_operation)
        self.seconds_per_operation *= self.args.iteration_growth_factor

    async def run_async(self):
        await asyncio.sleep(self.seconds_per_operation)
        self.seconds_per_operation *= self.args.iteration_growth_factor

    @staticmethod
    def add_arguments(parser):
        super(SleepTest, SleepTest).add_arguments(parser)
        parser.add_argument('--initial-delay-ms', nargs='?', type=int, default=1000, help='Initial delay (in milliseconds)')
        
        # Used for verifying the perf framework correctly computes average throughput across parallel tests of different speed.
        # Each instance of this test completes operations at a different rate, to allow for testing scenarios where
        # some instances are still waiting when time expires.
        parser.add_argument('--instance-growth-factor', nargs='?', type=float, default=1,
            help='Instance growth factor.  The delay of instance N will be (InitialDelayMS * (InstanceGrowthFactor ^ InstanceCount)).')
        
        parser.add_argument('--iteration-growth-factor', nargs='?', type=float, default=1,
            help='Iteration growth factor.  The delay of iteration N will be (InitialDelayMS * (IterationGrowthFactor ^ IterationCount)).')

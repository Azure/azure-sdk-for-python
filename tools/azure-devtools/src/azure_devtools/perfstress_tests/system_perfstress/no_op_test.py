# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ..perf_stress_test import PerfStressTest


class NoOpTest(PerfStressTest):
    def run_sync(self):
        pass

    async def run_async(self):
        pass

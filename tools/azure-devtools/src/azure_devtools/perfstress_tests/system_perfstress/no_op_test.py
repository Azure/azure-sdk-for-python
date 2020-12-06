# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import PerfStressTest


class NoOpTest(PerfStressTest):
    def run_sync(self):
        pass

    async def run_async(self):
        pass

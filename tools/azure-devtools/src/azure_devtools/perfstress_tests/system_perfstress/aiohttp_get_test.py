# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import aiohttp

from azure_devtools.perfstress_tests import PerfStressTest


class AioHttpGetTest(PerfStressTest):
    async def global_setup(self):
        type(self).session = aiohttp.ClientSession()

    async def global_cleanup(self):
        await type(self).session.close()

    async def run_async(self):
        async with type(self).session.get(self.args.url) as response:
            await response.text()

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("-u", "--url", required=True)

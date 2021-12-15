# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import httpx

from azure_devtools.perfstress_tests import PerfStressTest


class HttpxGetTest(PerfStressTest):
    async def global_setup(self):
        type(self).client = httpx.AsyncClient()

    async def global_cleanup(self):
        await type(self).client.aclose()

    async def run_async(self):
        response = await type(self).client.get(self.args.url)
        _ = response.text

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("-u", "--url", required=True)

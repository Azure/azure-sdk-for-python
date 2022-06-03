# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from tornado import httpclient

from azure_devtools.perfstress_tests import PerfStressTest


class TornadoGetTest(PerfStressTest):
    async def global_setup(self):
        httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        type(self).client = httpclient.AsyncHTTPClient()

    async def run_async(self):
        await type(self).client.fetch(self.args.url)

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("-u", "--url", required=True)

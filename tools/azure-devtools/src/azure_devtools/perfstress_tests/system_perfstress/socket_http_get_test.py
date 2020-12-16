# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
from urllib.parse import urlparse

from azure_devtools.perfstress_tests import PerfStressTest


class SocketHttpGetTest(PerfStressTest):

    async def setup(self):
        parsed_url = urlparse(self.Arguments.url)
        hostname = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path

        message = f'GET {path} HTTP/1.1\r\nHost: {hostname}:{port}\r\n\r\n'
        self.message_bytes = message.encode()
        self.reader, self.writer = await asyncio.open_connection(parsed_url.hostname, parsed_url.port)
 
    async def cleanup(self):
        self.writer.close()

    async def run_async(self):
        self.writer.write(self.message_bytes)
        await self.reader.read(200)

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('-u', '--url', required=True)

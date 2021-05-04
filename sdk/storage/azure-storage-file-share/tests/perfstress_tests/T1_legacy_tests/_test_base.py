# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid

from azure_devtools.perfstress_tests import PerfStressTest

from azure.storage.file import FileService

class _LegacyServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_STORAGE_CONNECTION_STRING")
        if not _LegacyServiceTest.service_client or self.args.no_client_share:
            _LegacyServiceTest.service_client = FileService(connection_string=connection_string)
            if self.args.max_range_size:
                _LegacyServiceTest.service_client.MAX_RANGE_SIZE = self.args.max_range_size
        self.async_service_client = None
        self.service_client = _LegacyServiceTest.service_client

    @staticmethod
    def add_arguments(parser):
        super(_LegacyServiceTest, _LegacyServiceTest).add_arguments(parser)
        parser.add_argument('-r', '--max-range-size', nargs='?', type=int, help='Maximum size of data uploading in single HTTP PUT. Defaults to 4*1024*1024', default=4*1024*1024)
        parser.add_argument('-c', '--max-concurrency', nargs='?', type=int, help='Maximum number of concurrent threads used for data transfer. Defaults to 1', default=1)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of data to transfer.  Default is 10240.', default=10240)
        parser.add_argument('--no-client-share', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)


class _LegacyShareTest(_LegacyServiceTest):
    share_name = "perfstress-legacy-" + str(uuid.uuid4())

    def __init__(self, arguments):
        super().__init__(arguments)

    async def global_setup(self):
        await super().global_setup()
        self.service_client.create_share(self.share_name)

    async def global_cleanup(self):
        self.service_client.delete_share(self.share_name)
        await super().global_cleanup()

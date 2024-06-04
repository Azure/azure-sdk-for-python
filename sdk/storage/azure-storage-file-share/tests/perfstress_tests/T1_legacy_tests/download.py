# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from devtools_testutils.perfstress_tests import get_random_bytes, WriteStream

from ._test_base import _LegacyShareTest


class LegacyDownloadTest(_LegacyShareTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.file_name = "downloadtest"
        self.download_stream = WriteStream()

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        self.service_client.create_file_from_bytes(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            file=data)

    def run_sync(self):
        self.download_stream.reset()
        self.service_client.get_file_to_stream(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            stream=self.download_stream,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")

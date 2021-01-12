# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import get_random_bytes, WriteStream

from ._test_base_legacy import _LegacyContainerTest


class LegacyDownloadTest(_LegacyContainerTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.blob_name = "downloadtest"
        self.download_stream = WriteStream()

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        self.service_client.create_blob_from_bytes(
            container_name=self.container_name,
            blob_name=self.blob_name,
            blob=data)

    def run_sync(self):
        self.download_stream.reset()
        self.service_client.get_blob_to_stream(
            container_name=self.container_name,
            blob_name=self.blob_name,
            stream=self.download_stream,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")

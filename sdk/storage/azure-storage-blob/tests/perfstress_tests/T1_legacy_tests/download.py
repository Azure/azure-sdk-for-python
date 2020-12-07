# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import get_random_bytes

from ._test_base_legacy import _LegacyContainerTest


class LegacyDownloadTest(_LegacyContainerTest):
    blob_name = "downloadtest"

    async def global_setup(self):
        await super().global_setup()
        data = get_random_bytes(self.args.size)
        self.service_client.create_blob_from_bytes(
            container_name=self.container_name,
            blob_name=self.blob_name,
            blob=data)

    def run_sync(self):
        self.service_client.get_blob_to_bytes(
            container_name=self.container_name,
            blob_name=self.blob_name,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")

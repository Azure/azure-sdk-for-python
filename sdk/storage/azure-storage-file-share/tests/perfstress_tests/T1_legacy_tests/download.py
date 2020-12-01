# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base_legacy import _LegacyShareTest


class LegacyDownloadTest(_LegacyShareTest):
    file_name = "downloadtest"

    async def global_setup(self):
        await super().global_setup()
        data = b'a' * self.args.size
        self.service_client.create_file_from_bytes(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            file=data)

    def run_sync(self):
        self.service_client.get_file_to_bytes(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            max_connections=self.args.max_concurrency)

    async def run_async(self):
        raise NotImplementedError("Async not supported for legacy T1 tests.")

    @staticmethod
    def add_arguments(parser):
        super(LegacyDownloadTest, LegacyDownloadTest).add_arguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of files to download.  Default is 10240.', default=10240)

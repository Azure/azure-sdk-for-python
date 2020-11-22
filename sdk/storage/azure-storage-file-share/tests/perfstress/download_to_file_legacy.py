
import os
import tempfile

from ._test_base_legacy import _LegacyShareTest


class LegacyDownloadToFileTest(_LegacyShareTest):
    file_name = "downloadtest"

    async def GlobalSetupAsync(self):
        await super().GlobalSetupAsync()
        data = b'a' * self.Arguments.size
        self.service_client.create_file_from_bytes(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            file=data)
        self.temp_file = os.path.join(tempfile.gettempdir(), self.file_name)

    async def GlobalCleanupAsync(self):
        os.remove(self.temp_file)
        await super().GlobalCleanupAsync()

    def Run(self):
        self.service_client.get_file_to_path(
            share_name=self.share_name,
            directory_name=None,
            file_name=self.file_name,
            file_path=self.temp_file)

    async def RunAsync(self):
        raise NotImplementedError("Async not supported for legacy tests.")

    @staticmethod
    def AddArguments(parser):
        super(LegacyDownloadToFileTest, LegacyDownloadToFileTest).AddArguments(parser)
        parser.add_argument('-s', '--size', nargs='?', type=int, help='Size of files to download.  Default is 10240.', default=10240)

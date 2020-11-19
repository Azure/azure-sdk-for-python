import os

from azure_devtools.perfstress_tests import PerfStressTest

from azure.storage.fileshare import FileService

class _LegacyServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)

        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise Exception("Undefined environment variable AZURE_STORAGE_CONNECTION_STRING")

        if not _LegacyServiceTest.service_client or self.Arguments.service_client_per_instance:
            _LegacyServiceTest.service_client = FileService(connection_string=connection_string)
            if self.Arguments.max_range_size:
                _LegacyServiceTest.service_client.MAX_RANGE_SIZE = self.Arguments.max_range_size

        self.service_client = _LegacyServiceTest.service_client
        self.async_service_client = None


    @staticmethod
    def AddArguments(parser):
        super(_LegacyServiceTest, _LegacyServiceTest).AddArguments(parser)
        parser.add_argument('--max-range-size', nargs='?', type=int, help='Maximum size of file uploading in single HTTP PUT. Defaults to 4*1024*1024')
        parser.add_argument('--max-connections', nargs='?', type=int, help='Maximum concurrent connection threads used for transfer.  Default is 1.')
        parser.add_argument('--service-client-per-instance', action='store_true', help='Create one ServiceClient per test instance.  Default is to share a single ServiceClient.', default=False)

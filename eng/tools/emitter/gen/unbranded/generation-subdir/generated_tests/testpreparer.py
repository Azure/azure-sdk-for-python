# coding=utf-8
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools
from generation.subdir import RecursiveClient


class RecursiveClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(RecursiveClient)
        return self.create_client_from_credential(
            RecursiveClient,
            credential=credential,
            endpoint=endpoint,
        )


RecursivePreparer = functools.partial(
    PowerShellPreparer, "recursive", recursive_endpoint="https://fake_recursive_endpoint.com"
)

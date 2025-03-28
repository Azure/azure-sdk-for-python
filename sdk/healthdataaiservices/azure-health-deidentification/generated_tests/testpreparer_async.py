# coding=utf-8
from azure.health.deidentification.aio import DeidentificationClient
from devtools_testutils import AzureRecordedTestCase


class DeidentificationClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(DeidentificationClient, is_async=True)
        return self.create_client_from_credential(
            DeidentificationClient,
            credential=credential,
            endpoint=endpoint,
        )

# coding=utf-8
from azure.health.deidentification import DeidentificationClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class DeidentificationClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DeidentificationClient)
        return self.create_client_from_credential(
            DeidentificationClient,
            credential=credential,
            endpoint=endpoint,
        )


DeidentificationPreparer = functools.partial(
    PowerShellPreparer, "deidentification", deidentification_endpoint="https://fake_deidentification_endpoint.com"
)

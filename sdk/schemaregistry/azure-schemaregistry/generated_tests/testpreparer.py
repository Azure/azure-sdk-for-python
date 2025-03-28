# coding=utf-8
from azure.schemaregistry import SchemaRegistryClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class SchemaRegistryClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(SchemaRegistryClient)
        return self.create_client_from_credential(
            SchemaRegistryClient,
            credential=credential,
            endpoint=endpoint,
        )


SchemaRegistryPreparer = functools.partial(
    PowerShellPreparer, "schemaregistry", schemaregistry_endpoint="https://fake_schemaregistry_endpoint.com"
)

# coding=utf-8
from devtools_testutils import AzureRecordedTestCase
from schemaregistry.aio import SchemaRegistryClient


class SchemaRegistryClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(
            SchemaRegistryClient,
            credential=credential,
            endpoint=endpoint,
        )

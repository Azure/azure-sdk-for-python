# coding=utf-8
from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient, DocumentIntelligenceClient
from devtools_testutils import AzureRecordedTestCase


class DocumentIntelligenceClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(DocumentIntelligenceClient, is_async=True)
        return self.create_client_from_credential(
            DocumentIntelligenceClient,
            credential=credential,
            endpoint=endpoint,
        )


class DocumentIntelligenceAdministrationClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(DocumentIntelligenceAdministrationClient, is_async=True)
        return self.create_client_from_credential(
            DocumentIntelligenceAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )

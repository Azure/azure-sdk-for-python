# coding=utf-8
from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient, DocumentIntelligenceClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class DocumentIntelligenceClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DocumentIntelligenceClient)
        return self.create_client_from_credential(
            DocumentIntelligenceClient,
            credential=credential,
            endpoint=endpoint,
        )


DocumentIntelligencePreparer = functools.partial(
    PowerShellPreparer,
    "documentintelligence",
    documentintelligence_endpoint="https://fake_documentintelligence_endpoint.com",
)


class DocumentIntelligenceAdministrationClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DocumentIntelligenceAdministrationClient)
        return self.create_client_from_credential(
            DocumentIntelligenceAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )


DocumentIntelligenceAdministrationPreparer = functools.partial(
    PowerShellPreparer,
    "documentintelligenceadministration",
    documentintelligenceadministration_endpoint="https://fake_documentintelligenceadministration_endpoint.com",
)

# coding=utf-8
from azure.ai.resources.autogen.aio import MachineLearningServicesClient
from devtools_testutils import AzureRecordedTestCase


class MachineLearningServicesClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(MachineLearningServicesClient, is_async=True)
        return self.create_client_from_credential(
            MachineLearningServicesClient,
            credential=credential,
            endpoint=endpoint,
        )

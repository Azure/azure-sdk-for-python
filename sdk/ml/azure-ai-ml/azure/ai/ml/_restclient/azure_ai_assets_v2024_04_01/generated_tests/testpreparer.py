# coding=utf-8
from azure.ai.resources.autogen import MachineLearningServicesClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class MachineLearningServicesClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(MachineLearningServicesClient)
        return self.create_client_from_credential(
            MachineLearningServicesClient,
            credential=credential,
            endpoint=endpoint,
        )


MachineLearningServicesPreparer = functools.partial(
    PowerShellPreparer,
    "machinelearningservices",
    machinelearningservices_endpoint="https://fake_machinelearningservices_endpoint.com",
)

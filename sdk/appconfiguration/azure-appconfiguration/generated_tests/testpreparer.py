# coding=utf-8
from azure.appconfiguration import AzureAppConfigurationClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class AzureAppConfigurationClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(AzureAppConfigurationClient)
        return self.create_client_from_credential(
            AzureAppConfigurationClient,
            credential=credential,
            endpoint=endpoint,
        )


AzureAppConfigurationPreparer = functools.partial(
    PowerShellPreparer,
    "azureappconfiguration",
    azureappconfiguration_endpoint="https://fake_azureappconfiguration_endpoint.com",
)

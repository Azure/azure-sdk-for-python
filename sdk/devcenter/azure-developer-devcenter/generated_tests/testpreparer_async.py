# coding=utf-8
from azure.developer.devcenter.aio import DeploymentEnvironmentsClient, DevBoxesClient, DevCenterClient
from devtools_testutils import AzureRecordedTestCase


class DevCenterClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(DevCenterClient, is_async=True)
        return self.create_client_from_credential(
            DevCenterClient,
            credential=credential,
            endpoint=endpoint,
        )


class DevBoxesClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(DevBoxesClient, is_async=True)
        return self.create_client_from_credential(
            DevBoxesClient,
            credential=credential,
            endpoint=endpoint,
        )


class DeploymentEnvironmentsClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(DeploymentEnvironmentsClient, is_async=True)
        return self.create_client_from_credential(
            DeploymentEnvironmentsClient,
            credential=credential,
            endpoint=endpoint,
        )

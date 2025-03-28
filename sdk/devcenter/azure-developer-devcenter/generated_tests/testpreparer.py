# coding=utf-8
from azure.developer.devcenter import DeploymentEnvironmentsClient, DevBoxesClient, DevCenterClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class DevCenterClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DevCenterClient)
        return self.create_client_from_credential(
            DevCenterClient,
            credential=credential,
            endpoint=endpoint,
        )


DevCenterPreparer = functools.partial(
    PowerShellPreparer, "devcenter", devcenter_endpoint="https://fake_devcenter_endpoint.com"
)


class DevBoxesClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DevBoxesClient)
        return self.create_client_from_credential(
            DevBoxesClient,
            credential=credential,
            endpoint=endpoint,
        )


DevBoxesPreparer = functools.partial(
    PowerShellPreparer, "devboxes", devboxes_endpoint="https://fake_devboxes_endpoint.com"
)


class DeploymentEnvironmentsClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DeploymentEnvironmentsClient)
        return self.create_client_from_credential(
            DeploymentEnvironmentsClient,
            credential=credential,
            endpoint=endpoint,
        )


DeploymentEnvironmentsPreparer = functools.partial(
    PowerShellPreparer,
    "deploymentenvironments",
    deploymentenvironments_endpoint="https://fake_deploymentenvironments_endpoint.com",
)

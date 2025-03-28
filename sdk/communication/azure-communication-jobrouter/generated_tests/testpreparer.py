# coding=utf-8
from azure.communication.jobrouter import JobRouterAdministrationClient, JobRouterClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class JobRouterAdministrationClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(JobRouterAdministrationClient)
        return self.create_client_from_credential(
            JobRouterAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )


JobRouterAdministrationPreparer = functools.partial(
    PowerShellPreparer,
    "jobrouteradministration",
    jobrouteradministration_endpoint="https://fake_jobrouteradministration_endpoint.com",
)


class JobRouterClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(JobRouterClient)
        return self.create_client_from_credential(
            JobRouterClient,
            credential=credential,
            endpoint=endpoint,
        )


JobRouterPreparer = functools.partial(
    PowerShellPreparer, "jobrouter", jobrouter_endpoint="https://fake_jobrouter_endpoint.com"
)

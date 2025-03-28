# coding=utf-8
from azure.communication.jobrouter.aio import JobRouterAdministrationClient, JobRouterClient
from devtools_testutils import AzureRecordedTestCase


class JobRouterAdministrationClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(JobRouterAdministrationClient, is_async=True)
        return self.create_client_from_credential(
            JobRouterAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )


class JobRouterClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(JobRouterClient, is_async=True)
        return self.create_client_from_credential(
            JobRouterClient,
            credential=credential,
            endpoint=endpoint,
        )

# coding=utf-8
from azure.ai.vision.face.aio import FaceAdministrationClient, FaceClient, FaceSessionClient
from devtools_testutils import AzureRecordedTestCase


class FaceClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(FaceClient, is_async=True)
        return self.create_client_from_credential(
            FaceClient,
            credential=credential,
            endpoint=endpoint,
        )


class FaceSessionClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(FaceSessionClient, is_async=True)
        return self.create_client_from_credential(
            FaceSessionClient,
            credential=credential,
            endpoint=endpoint,
        )


class FaceAdministrationClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(FaceAdministrationClient, is_async=True)
        return self.create_client_from_credential(
            FaceAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )

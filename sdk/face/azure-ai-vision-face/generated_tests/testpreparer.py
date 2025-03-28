# coding=utf-8
from azure.ai.vision.face import FaceAdministrationClient, FaceClient, FaceSessionClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class FaceClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(FaceClient)
        return self.create_client_from_credential(
            FaceClient,
            credential=credential,
            endpoint=endpoint,
        )


FacePreparer = functools.partial(PowerShellPreparer, "face", face_endpoint="https://fake_face_endpoint.com")


class FaceSessionClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(FaceSessionClient)
        return self.create_client_from_credential(
            FaceSessionClient,
            credential=credential,
            endpoint=endpoint,
        )


FaceSessionPreparer = functools.partial(
    PowerShellPreparer, "facesession", facesession_endpoint="https://fake_facesession_endpoint.com"
)


class FaceAdministrationClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(FaceAdministrationClient)
        return self.create_client_from_credential(
            FaceAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )


FaceAdministrationPreparer = functools.partial(
    PowerShellPreparer, "faceadministration", faceadministration_endpoint="https://fake_faceadministration_endpoint.com"
)

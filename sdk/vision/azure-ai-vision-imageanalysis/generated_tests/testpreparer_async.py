# coding=utf-8
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from devtools_testutils import AzureRecordedTestCase


class ImageAnalysisClientTestBaseAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(ImageAnalysisClient, is_async=True)
        return self.create_client_from_credential(
            ImageAnalysisClient,
            credential=credential,
            endpoint=endpoint,
        )

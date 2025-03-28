# coding=utf-8
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
import functools


class ImageAnalysisClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(ImageAnalysisClient)
        return self.create_client_from_credential(
            ImageAnalysisClient,
            credential=credential,
            endpoint=endpoint,
        )


ImageAnalysisPreparer = functools.partial(
    PowerShellPreparer, "imageanalysis", imageanalysis_endpoint="https://fake_imageanalysis_endpoint.com"
)

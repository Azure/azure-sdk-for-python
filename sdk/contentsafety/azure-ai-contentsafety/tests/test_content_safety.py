import base64
import functools

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import *
from azure.core.credentials import AzureKeyCredential
from test_data import *

ContentSafetyPreparer = functools.partial(
    PowerShellPreparer,
    'content_safety',
    content_safety_endpoint="https://fake_cs_resource.cognitiveservices.azure.com/",
    content_safety_key="00000000000000000000000000000000"
)

class TestContentSafety(AzureRecordedTestCase):

    def create_client(self, endpoint, key):
        client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
        return client

class TestContentSafetyCase(TestContentSafety):

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text(self, content_safety_endpoint, content_safety_key):
        client = self.create_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        request = AnalyzeTextOptions(text=get_text_data(), categories=[])
        response = client.analyze_text(request)

        assert response.hate_result.severity > 0

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_image(self, content_safety_endpoint, content_safety_key):
        client = self.create_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        request = AnalyzeImageOptions(image=ImageData(content=base64.b64decode(get_image_content_data())))
        response = client.analyze_image(request)

        assert response.violence_result.severity > 0


# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, ImageData, AnalyzeImageOptions, TextBlocklist
from azure.core.credentials import AzureKeyCredential

ContentSafetyPreparer = functools.partial(
    EnvironmentVariableLoader,
    "content_safety",
    content_safety_endpoint="https://fake_cs_resource.cognitiveservices.azure.com",
    content_safety_key="00000000000000000000000000000000",
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

        text_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./samples/sample_data/text.txt"))
        with open(text_path) as f:
            request = AnalyzeTextOptions(text=f.readline(), categories=[])
        response = client.analyze_text(request)

        assert response is not None
        assert response.hate_result is not None
        assert response.violence_result is not None
        assert response.sexual_result is not None
        assert response.self_harm_result is not None
        assert response.hate_result.severity > 0

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_image(self, content_safety_endpoint, content_safety_key):
        client = self.create_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        image_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./samples/sample_data/image.jpg"))
        with open(image_path, "rb") as file:
            request = AnalyzeImageOptions(image=ImageData(content=file.read()))
        response = client.analyze_image(request)

        assert response.violence_result.severity > 0

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_create_blocklist(self, content_safety_endpoint, content_safety_key):
        client = self.create_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        name = "TestBlocklist"
        description = "Test blocklist management."
        response = client.create_or_update_text_blocklist(blocklist_name=name, resource={"description": description})

        assert response is not None
        assert response.blocklist_name == name
        assert response.description == description

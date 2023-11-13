# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import os

from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from azure.ai.contentsafety import ContentSafetyClient, BlocklistClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, ImageData, AnalyzeImageOptions, TextCategory

ContentSafetyPreparer = functools.partial(
    EnvironmentVariableLoader,
    "content_safety",
    content_safety_endpoint="https://fake_cs_resource.cognitiveservices.azure.com",
    content_safety_key="00000000000000000000000000000000",
)


class TestContentSafety(AzureRecordedTestCase):
    def create_contentsafety_client(self, endpoint, key):
        client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
        return client

    def create_blocklist_client(self, endpoint, key):
        client = BlocklistClient(endpoint, AzureKeyCredential(key))
        return client


class TestContentSafetyCase(TestContentSafety):
    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text(self, content_safety_endpoint, content_safety_key):
        client = self.create_contentsafety_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        text_path = os.path.abspath(
            os.path.join(os.path.abspath(__file__), "..", "..", "./samples/sample_data/text.txt")
        )
        with open(text_path) as f:
            request = AnalyzeTextOptions(text=f.readline(), categories=[])
        response = client.analyze_text(request)

        assert response is not None
        assert response.categories_analysis is not None
        assert next(item for item in response.categories_analysis if item.category == TextCategory.HATE) is not None
        assert next(item for item in response.categories_analysis if item.category == TextCategory.VIOLENCE) is not None
        assert next(item for item in response.categories_analysis if item.category == TextCategory.SEXUAL) is not None
        assert next(item for item in response.categories_analysis if item.category == TextCategory.SELF_HARM) is not None
        assert next(item for item in response.categories_analysis if item.category == TextCategory.HATE).severity > 0

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_image(self, content_safety_endpoint, content_safety_key):
        client = self.create_contentsafety_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        image_path = os.path.abspath(
            os.path.join(os.path.abspath(__file__), "..", "..", "./samples/sample_data/image.jpg")
        )
        with open(image_path, "rb") as file:
            request = AnalyzeImageOptions(image=ImageData(content=file.read()))
        response = client.analyze_image(request)

        assert response is not None
        assert response.categories_analysis is not None
        assert next(item for item in response.categories_analysis if item.category == TextCategory.VIOLENCE).severity > 0

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_create_blocklist(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        name = "TestBlocklist"
        description = "Test blocklist management."
        response = client.create_or_update_text_blocklist(blocklist_name=name, resource={"description": description})

        assert response is not None
        assert response.blocklist_name == name
        assert response.description == description

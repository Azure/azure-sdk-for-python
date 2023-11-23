# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import os

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.identity import ClientSecretCredential
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from azure.ai.contentsafety import ContentSafetyClient, BlocklistClient
from azure.ai.contentsafety.models import (
    AnalyzeTextOptions,
    ImageData,
    AnalyzeImageOptions,
    TextCategory,
    TextBlocklist,
    TextBlocklistItem,
    AddOrUpdateTextBlocklistItemsOptions,
)

ContentSafetyPreparer = functools.partial(
    EnvironmentVariableLoader,
    "content_safety",
    content_safety_endpoint="https://fake_cs_resource.cognitiveservices.azure.com",
    content_safety_key="00000000000000000000000000000000",
    content_safety_client_id="00000000000000000000000000000000",
    content_safety_client_secret="00000000000000000000000000000000",
    content_safety_tenant_id="00000000000000000000000000000000",
)


class TestContentSafety(AzureRecordedTestCase):
    def create_contentsafety_client(self, endpoint, key):
        client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
        return client

    def create_contentsafety_client_with_add_auth(self, endpoint, client_id, client_secret, tenant_id):
        client = ContentSafetyClient(endpoint, ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        ))
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
        assert (
            next(item for item in response.categories_analysis if item.category == TextCategory.SELF_HARM) is not None
        )
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
        assert (
            next(item for item in response.categories_analysis if item.category == TextCategory.VIOLENCE).severity > 0
        )

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text_with_blocklists(self, content_safety_endpoint, content_safety_key):
        client = self.create_contentsafety_client(content_safety_endpoint, content_safety_key)
        blocklist_client = self.create_blocklist_client(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestAnalyzeTextWithBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = blocklist_client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description)
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # Add blocklist item
        block_item_text_1 = "k*ll"
        block_item_text_2 = "h*te"
        block_items = [TextBlocklistItem(text=block_item_text_1), TextBlocklistItem(text=block_item_text_2)]
        add_item_response = blocklist_client.add_or_update_blocklist_items(
            blocklist_name=blocklist_name, options=AddOrUpdateTextBlocklistItemsOptions(blocklist_items=block_items)
        )
        if not add_item_response or not add_item_response.blocklist_items or len(add_item_response.blocklist_items) < 0:
            raise RuntimeError("Failed to add blocklist item.")

        input_text = "I h*te you and I want to k*ll you."
        analysis_result = client.analyze_text(
            AnalyzeTextOptions(text=input_text, blocklist_names=[blocklist_name], halt_on_blocklist_hit=False)
        )
        assert analysis_result is not None
        assert analysis_result.blocklists_match is not None
        assert any(block_item_text_1 in item.blocklist_item_text for item in analysis_result.blocklists_match) is True
        assert any(block_item_text_2 in item.blocklist_item_text for item in analysis_result.blocklists_match) is True

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text_with_aad_auth(self, content_safety_endpoint, content_safety_client_id, content_safety_client_secret, content_safety_tenant_id):
        client = self.create_contentsafety_client_with_add_auth(content_safety_endpoint, content_safety_client_id, content_safety_client_secret, content_safety_tenant_id)
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
        assert (
            next(item for item in response.categories_analysis if item.category == TextCategory.SELF_HARM) is not None
        )
        assert next(item for item in response.categories_analysis if item.category == TextCategory.HATE).severity > 0

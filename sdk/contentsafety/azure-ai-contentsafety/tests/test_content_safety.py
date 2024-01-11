# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os

from devtools_testutils import recorded_by_proxy

from azure.ai.contentsafety.models import (
    AnalyzeTextOptions,
    ImageData,
    AnalyzeImageOptions,
    TextCategory,
    TextBlocklist,
    TextBlocklistItem,
    AddOrUpdateTextBlocklistItemsOptions,
)
from test_case import ContentSafetyTest, ContentSafetyPreparer


class TestContentSafetyCase(ContentSafetyTest):
    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text(self, content_safety_endpoint, content_safety_key):
        client = self.create_content_safety_client_from_key(content_safety_endpoint, content_safety_key)

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
        client = self.create_content_safety_client_from_key(content_safety_endpoint, content_safety_key)

        image_path = os.path.abspath(
            os.path.join(os.path.abspath(__file__), "..", "..", "./samples/sample_data/image.jpg")
        )
        with open(image_path, "rb") as file:
            request = AnalyzeImageOptions(image=ImageData(content=file.read()))
        response = client.analyze_image(request)

        assert response is not None
        assert response.categories_analysis is not None

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text_with_blocklists(self, content_safety_endpoint, content_safety_key):
        content_safety_client = self.create_content_safety_client_from_key(content_safety_endpoint, content_safety_key)
        blocklist_client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestAnalyzeTextWithBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = blocklist_client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
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
        analysis_result = content_safety_client.analyze_text(
            AnalyzeTextOptions(text=input_text, blocklist_names=[blocklist_name], halt_on_blocklist_hit=False)
        )
        assert analysis_result is not None
        assert analysis_result.blocklists_match is not None
        assert any(block_item_text_1 in item.blocklist_item_text for item in analysis_result.blocklists_match) is True
        assert any(block_item_text_2 in item.blocklist_item_text for item in analysis_result.blocklists_match) is True

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text_with_entra_id_credential(self, content_safety_endpoint):
        client = self.create_content_safety_client_from_entra_id(content_safety_endpoint)

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

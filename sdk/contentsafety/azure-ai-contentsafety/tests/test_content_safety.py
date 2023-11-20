# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import os

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from azure.ai.contentsafety import ContentSafetyClient, BlocklistClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, ImageData, AnalyzeImageOptions, TextCategory, \
    TextBlocklist, ImageCategory, TextBlocklistItem, AddOrUpdateTextBlocklistItemsOptions, \
    RemoveTextBlocklistItemsOptions

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
    def test_create_blocklist(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint, content_safety_key)
        assert client is not None

        name = "TestBlocklist"
        description = "Test blocklist management."
        response = client.create_or_update_text_blocklist(
            blocklist_name=name,
            options=TextBlocklist(blocklist_name=name, description=description)
        )

        assert response is not None
        assert response.blocklist_name == name
        assert response.description == description

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_add_block_items (self, content_safety_endpoint,content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint,content_safety_key)

        blocklist_name = "TestBlocklist"
        block_item_text_1 = "k*ll"
        block_item_text_2 = "h*te"

        block_items = [TextBlocklistItem(text=block_item_text_1), TextBlocklistItem(text=block_item_text_2)]
        try:
            result = client.add_or_update_blocklist_items(
                blocklist_name=blocklist_name,
                options=AddOrUpdateTextBlocklistItemsOptions(blocklist_items=block_items)
            )
            if result and result.blocklist_items:
                print("\nBlock items added: ")
                for block_item in result.blocklist_items:
                    print(
                        f"BlockItemId: {block_item.blocklist_item_id}, Text: {block_item.text}, Description: {block_item.description}"
                    )
        except HttpResponseError as e:
            print("\nAdd block items failed: ")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_analyze_text_with_blocklists(self, content_safety_endpoint,content_safety_key):
        client = self.create_contentsafety_client(content_safety_endpoint,content_safety_key)

        blocklist_name = "TestBlocklist"
        input_text = "I h*te you and I want to k*ll you."

        try:
            # After you edit your blocklist, it usually takes effect in 5 minutes, please wait some time before analyzing with blocklist after editing.
            analysis_result = client.analyze_text(
                AnalyzeTextOptions(text=input_text, blocklist_names=[blocklist_name], halt_on_blocklist_hit=False)
            )
            if analysis_result and analysis_result.blocklists_match:
                print("\nBlocklist match results: ")
                for match_result in analysis_result.blocklists_match:
                    print(
                        f"BlocklistName: {match_result.blocklist_name}, BlockItemId: {match_result.blocklist_item_id}, "
                        f"BlockItemText: {match_result.blocklist_item_text}"
                    )
        except HttpResponseError as e:
            print("\nAnalyze text failed: ")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_list_text_blocklists(self, content_safety_endpoint,content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint,content_safety_key)

        try:
            blocklists = client.list_text_blocklists()
            if blocklists:
                print("\nList blocklists: ")
                for blocklist in blocklists:
                    print(f"Name: {blocklist.blocklist_name}, Description: {blocklist.description}")
        except HttpResponseError as e:
            print("\nList text blocklists failed: ")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_get_text_blocklist(self, content_safety_endpoint,content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint,content_safety_key)

        blocklist_name = "TestBlocklist"

        try:
            blocklist = client.get_text_blocklist(blocklist_name=blocklist_name)
            if blocklist:
                print("\nGet blocklist: ")
                print(f"Name: {blocklist.blocklist_name}, Description: {blocklist.description}")
        except HttpResponseError as e:
            print("\nGet text blocklist failed: ")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_list_block_items(self, content_safety_endpoint,content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint,content_safety_key)

        blocklist_name = "TestBlocklist"

        try:
            block_items = client.list_text_blocklist_items(blocklist_name=blocklist_name)
            if block_items:
                print("\nList block items: ")
                for block_item in block_items:
                    print(
                        f"BlockItemId: {block_item.blocklist_item_id}, Text: {block_item.text}, "
                        f"Description: {block_item.description}"
                    )
        except HttpResponseError as e:
            print("\nList block items failed: ")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_get_block_item(self, content_safety_endpoint,content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint,content_safety_key)

        blocklist_name = "TestBlocklist"
        block_item_text_1 = "k*ll"

        try:
            # Add a blockItem
            add_result = client.add_or_update_blocklist_items(
                blocklist_name=blocklist_name,
                options=AddOrUpdateTextBlocklistItemsOptions(
                    blocklist_items=[TextBlocklistItem(text=block_item_text_1)]),
            )
            if not add_result or not add_result.blocklist_items or len(add_result.blocklist_items) <= 0:
                raise RuntimeError("BlockItem not created.")
            block_item_id = add_result.blocklist_items[0].blocklist_item_id

            # Get this blockItem by blockItemId
            block_item = client.get_text_blocklist_item(blocklist_name=blocklist_name, blocklist_item_id=block_item_id)
            print("\nGet blockitem: ")
            print(
                f"BlockItemId: {block_item.blocklist_item_id}, Text: {block_item.text}, Description: {block_item.description}"
            )
        except HttpResponseError as e:
            print("\nGet block item failed: ")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_remove_block_items(self, content_safety_endpoint,content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint,content_safety_key)

        blocklist_name = "TestBlocklist"
        block_item_text_1 = "k*ll"

        try:
            # Add a blockItem
            add_result = client.add_or_update_blocklist_items(
                blocklist_name=blocklist_name,
                options=AddOrUpdateTextBlocklistItemsOptions(
                    blocklist_items=[TextBlocklistItem(text=block_item_text_1)]),
            )
            if not add_result or not add_result.blocklist_items or len(add_result.blocklist_items) <= 0:
                raise RuntimeError("BlockItem not created.")
            block_item_id = add_result.blocklist_items[0].blocklist_item_id

            # Remove this blockItem by blockItemId
            client.remove_blocklist_items(
                blocklist_name=blocklist_name,
                options=RemoveTextBlocklistItemsOptions(blocklist_item_ids=[block_item_id])
            )
            print(f"\nRemoved blockItem: {add_result.blocklist_items[0].blocklist_item_id}")
        except HttpResponseError as e:
            print("\nRemove block item failed: ")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_delete_blocklist(self, content_safety_endpoint,content_safety_key):
        client = self.create_blocklist_client(content_safety_endpoint,content_safety_key)

        blocklist_name = "TestBlocklist"

        try:
            client.delete_text_blocklist(blocklist_name=blocklist_name)
            print(f"\nDeleted blocklist: {blocklist_name}")
        except HttpResponseError as e:
            print("\nDelete blocklist failed:")
            if e.error:
                print(f"Error code: {e.error.code}")
                print(f"Error message: {e.error.message}")
                raise
            print(e)
            raise

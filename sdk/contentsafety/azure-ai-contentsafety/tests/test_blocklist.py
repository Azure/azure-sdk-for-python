# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.exceptions import HttpResponseError
from devtools_testutils import recorded_by_proxy

from azure.ai.contentsafety.models import (
    TextBlocklist,
    TextBlocklistItem,
    AddOrUpdateTextBlocklistItemsOptions,
    RemoveTextBlocklistItemsOptions,
)
from test_case import ContentSafetyTest, ContentSafetyPreparer


class TestBlocklistCase(ContentSafetyTest):
    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_create_blocklist(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        name = "TestBlocklist"
        description = "Test blocklist management."
        response = client.create_or_update_text_blocklist(
            blocklist_name=name, options=TextBlocklist(blocklist_name=name, description=description)
        )

        assert response is not None
        assert response.blocklist_name == name
        assert response.description == description

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_list_text_blocklists(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # List blocklist
        blocklists = list(client.list_text_blocklists())

        assert blocklists is not None
        assert any(blocklist_name in item["blocklistName"] for item in blocklists) is True
        assert any(blocklist_description in item["description"] for item in blocklists) is True

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_get_text_blocklist(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # Get blocklist
        blocklist = client.get_text_blocklist(blocklist_name=blocklist_name)
        assert blocklist is not None
        assert blocklist.blocklist_name == blocklist_name
        assert blocklist.description == blocklist_description

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_delete_blocklist(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestDeleteBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # Delete blocklist
        try:
            client.delete_text_blocklist(blocklist_name=blocklist_name)
        except HttpResponseError:
            raise

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_add_blocklist_items(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # Add blocklist item
        block_item_text_1 = "k*ll"
        block_item_text_2 = "h*te"
        block_items = [TextBlocklistItem(text=block_item_text_1), TextBlocklistItem(text=block_item_text_2)]
        response = client.add_or_update_blocklist_items(
            blocklist_name=blocklist_name, options=AddOrUpdateTextBlocklistItemsOptions(blocklist_items=block_items)
        )
        assert response is not None
        assert response.blocklist_items is not None
        assert any(block_item_text_1 in item["text"] for item in response.blocklist_items) is True
        assert any(block_item_text_2 in item["text"] for item in response.blocklist_items) is True

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_list_blocklist_items(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # Add blocklist item
        block_item_text_1 = "This is a test."
        block_item_text_2 = "This is a test 2."
        block_item_text_3 = "This is a test 3."
        block_item_text_4 = "This is a test 4."
        block_item_text_5 = "This is a test 5."
        block_items = [
            TextBlocklistItem(text=block_item_text_1),
            TextBlocklistItem(text=block_item_text_2),
            TextBlocklistItem(text=block_item_text_3),
            TextBlocklistItem(text=block_item_text_4),
            TextBlocklistItem(text=block_item_text_5),
        ]
        add_item_response = client.add_or_update_blocklist_items(
            blocklist_name=blocklist_name, options=AddOrUpdateTextBlocklistItemsOptions(blocklist_items=block_items)
        )
        if not add_item_response or not add_item_response.blocklist_items or len(add_item_response.blocklist_items) < 0:
            raise RuntimeError("Failed to add blocklist item.")

        # List blocklist item
        response = list(client.list_text_blocklist_items(blocklist_name=blocklist_name))
        assert response is not None
        items_count = len(response)
        assert items_count >= 5
        assert any(block_item_text_1 in item["text"] for item in response) is True
        assert any(block_item_text_2 in item["text"] for item in response) is True
        assert any(block_item_text_3 in item["text"] for item in response) is True
        assert any(block_item_text_4 in item["text"] for item in response) is True
        assert any(block_item_text_5 in item["text"] for item in response) is True

        # List blocklist item, test top
        response = list(client.list_text_blocklist_items(blocklist_name=blocklist_name, top=2))
        assert response is not None
        assert len(response) <= 2

        # List blocklist item, test skip
        response = list(client.list_text_blocklist_items(blocklist_name=blocklist_name, skip=2))
        assert response is not None
        assert len(response) <= items_count - 2

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_get_blocklist_item(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestBlocklist"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # Add blocklist item
        block_item_text_1 = "k*ll"
        block_items = [TextBlocklistItem(text=block_item_text_1)]
        add_item_response = client.add_or_update_blocklist_items(
            blocklist_name=blocklist_name, options=AddOrUpdateTextBlocklistItemsOptions(blocklist_items=block_items)
        )
        if not add_item_response or not add_item_response.blocklist_items or len(add_item_response.blocklist_items) < 0:
            raise RuntimeError("Failed to add blocklist item.")

        block_item_id = add_item_response.blocklist_items[0].blocklist_item_id

        # Get this blockItem by blockItemId
        blocklist_item = client.get_text_blocklist_item(blocklist_name=blocklist_name, blocklist_item_id=block_item_id)
        assert blocklist_item is not None
        assert blocklist_item.text == block_item_text_1

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_remove_blocklist_items(self, content_safety_endpoint, content_safety_key):
        client = self.create_blocklist_client_from_key(content_safety_endpoint, content_safety_key)

        # Create blocklist
        blocklist_name = "TestRemoveBlocklistItem"
        blocklist_description = "Test blocklist management."
        create_blocklist_response = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if not create_blocklist_response or not create_blocklist_response.blocklist_name:
            raise RuntimeError("Failed to create blocklist.")

        # Add blocklist item
        block_item_text_1 = "k*ll"
        block_items = [TextBlocklistItem(text=block_item_text_1)]
        add_item_response = client.add_or_update_blocklist_items(
            blocklist_name=blocklist_name, options=AddOrUpdateTextBlocklistItemsOptions(blocklist_items=block_items)
        )
        if not add_item_response or not add_item_response.blocklist_items or len(add_item_response.blocklist_items) < 0:
            raise RuntimeError("Failed to add blocklist item.")

        block_item_id = add_item_response.blocklist_items[0].blocklist_item_id

        try:
            # Remove this blockItem by blockItemId
            client.remove_blocklist_items(
                blocklist_name=blocklist_name,
                options=RemoveTextBlocklistItemsOptions(blocklist_item_ids=[block_item_id]),
            )
        except HttpResponseError:
            raise

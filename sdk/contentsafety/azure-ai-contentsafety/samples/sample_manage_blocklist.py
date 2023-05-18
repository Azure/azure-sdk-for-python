# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

def create_or_update_text_blocklist():
    # [START create_or_update_text_blocklist]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"
    blocklist_description = "Test blocklist management."

    try:
        blocklist = client.create_or_update_text_blocklist(blocklist_name=blocklist_name, resource={"description": blocklist_description})
        if blocklist is not None:
            print("\nBlocklist created or updated: ")
            print("Name: {}, Description: {}".format(blocklist.blocklist_name, blocklist.description))
    except HttpResponseError as e:
        print("\nCreate or update text blocklist failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END create_or_update_text_blocklist]

def add_block_items():
    # [START add_block_items]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.contentsafety.models import (
        TextBlockItemInfo,
        AddBlockItemsOptions
    )
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"
    block_item_text_1 = "k*ll"
    block_item_text_2 = "h*te"

    block_items = [TextBlockItemInfo(text=block_item_text_1), TextBlockItemInfo(text=block_item_text_2)]
    try:
        result = client.add_block_items(
            blocklist_name=blocklist_name,
            body=AddBlockItemsOptions(block_items=block_items),
        )
        if result is not None and result.value is not None:
            print("\nBlock items added: ")
            for block_item in result.value:
                print("BlockItemId: {}, Text: {}, Description: {}".format(block_item.block_item_id, block_item.text, block_item.description))
    except HttpResponseError as e:
        print("\nAdd block items failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END add_block_items]

def analyze_text_with_blocklists():
    # [START analyze_text_with_blocklists]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.contentsafety.models import AnalyzeTextOptions
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"
    input_text = "I h*te you and I want to k*ll you."

    try:
        # After you edit your blocklist, it usually takes effect in 5 minutes, please wait some time before analyzing with blocklist after editing.
        analysis_result = client.analyze_text(AnalyzeTextOptions(text=input_text, blocklist_names=[blocklist_name], break_by_blocklists=False))
        if analysis_result is not None and analysis_result.blocklists_match_results is not None:
            print("\nBlocklist match results: ")
            for match_result in analysis_result.blocklists_match_results:
                print("Block item was hit in text, Offset={}, Length={}.".format(match_result.offset, match_result.length))
                print("BlocklistName: {}, BlockItemId: {}, BlockItemText: {}".format(match_result.blocklist_name, match_result.block_item_id, match_result.block_item_text))
    except HttpResponseError as e:
        print("\nAnalyze text failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END analyze_text_with_blocklists]

def list_text_blocklists():
    # [START list_text_blocklists]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    try:
        blocklists = client.list_text_blocklists()
        if blocklists is not None:
            print("\nList blocklists: ")
            for blocklist in blocklists:
                print("Name: {}, Description: {}".format(blocklist.blocklist_name, blocklist.description))
    except HttpResponseError as e:
        print("\nList text blocklists failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END list_text_blocklists]

def get_text_blocklist():
    # [START get_text_blocklist]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"

    try:
        blocklist = client.get_text_blocklist(blocklist_name=blocklist_name)
        if blocklist is not None:
            print("\nGet blocklist: ")
            print("Name: {}, Description: {}".format(blocklist.blocklist_name, blocklist.description))
    except HttpResponseError as e:
        print("\nGet text blocklist failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END get_text_blocklist]

def list_block_items():
    # [START list_block_items]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"

    try:
        block_items = client.list_text_blocklist_items(blocklist_name=blocklist_name)
        if block_items is not None:
            print("\nList block items: ")
            for block_item in block_items:
                print("BlockItemId: {}, Text: {}, Description: {}".format(block_item.block_item_id, block_item.text, block_item.description))
    except HttpResponseError as e:
        print("\nList block items failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END list_block_items]

def get_block_item():
    # [START get_block_item]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.contentsafety.models import TextBlockItemInfo, AddBlockItemsOptions
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"
    block_item_text_1 = "k*ll"

    try:
        add_result = client.add_block_items(
            blocklist_name=blocklist_name,
            body=AddBlockItemsOptions(block_items=[TextBlockItemInfo(text=block_item_text_1)]),
        )
        if add_result is not None and add_result.value is not None and len(add_result.value) > 0:
            block_item_id = add_result.value[0].block_item_id
            block_item = client.get_text_blocklist_item(
                blocklist_name=blocklist_name,
                block_item_id= block_item_id
            )
            print("\nGet blockitem: ")
            print("BlockItemId: {}, Text: {}, Description: {}".format(block_item.block_item_id, block_item.text,
                                                                      block_item.description))
    except HttpResponseError as e:
        print("\nGet block item failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END get_block_item]

def remove_block_items():
    # [START remove_block_items]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.contentsafety.models import (
        TextBlockItemInfo,
        AddBlockItemsOptions,
        RemoveBlockItemsOptions
    )
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"
    block_item_text_1 = "k*ll"

    try:
        add_result = client.add_block_items(
            blocklist_name=blocklist_name,
            body=AddBlockItemsOptions(block_items=[TextBlockItemInfo(text=block_item_text_1)]),
        )
        if add_result is not None and add_result.value is not None and len(add_result.value) > 0:
            block_item_id = add_result.value[0].block_item_id
            client.remove_block_items(
                blocklist_name=blocklist_name,
                body=RemoveBlockItemsOptions(block_item_ids=[block_item_id])
            )
            print("\nRemoved blockItem: {}".format(add_result.value[0].block_item_id))
    except HttpResponseError as e:
        print("\nRemove block item failed: ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END remove_block_items]

def delete_blocklist():
    # [START delete_blocklist]

    import os
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError

    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

    # Create an Content Safety client
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))

    blocklist_name = "TestBlocklist"

    try:
        client.delete_text_blocklist(blocklist_name=blocklist_name)
        print("\nDeleted blocklist: {}".format(blocklist_name))
    except HttpResponseError as e:
        print("\nDelete blocklist failed:")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            raise
        print(e)
        raise

    # [END delete_blocklist]

if __name__ == "__main__":
    create_or_update_text_blocklist()
    add_block_items()
    analyze_text_with_blocklists()
    list_text_blocklists()
    get_text_blocklist()
    list_block_items()
    get_block_item()
    remove_block_items()
    delete_blocklist()

import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import (
    TextBlocklist,
    TextBlockItemInfo,
    AddBlockItemsOptions,
    RemoveBlockItemsOptions,
    AnalyzeTextOptions,
)
from azure.core.exceptions import HttpResponseError
import time


key = os.environ["CONTENT_SAFETY_KEY"]
endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]

# Create an Content Safety client
client = ContentSafetyClient(endpoint, AzureKeyCredential(key))


def list_text_blocklists():
    try:
        return client.list_text_blocklists()
    except HttpResponseError as e:
        print("List text blocklists failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        print(e)
        raise

def create_or_update_text_blocklist(name, description):
    try:
        return client.create_or_update_text_blocklist(
            blocklist_name=name, resource=TextBlocklist(description=description)
        )
    except HttpResponseError as e:
        print("Create or update text blocklist failed. ")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        print(e)
        raise


def get_text_blocklist(name):
    try:
        return client.get_text_blocklist(blocklist_name=name)
    except HttpResponseError as e:
        print("Get text blocklist failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        print(e)
        raise


def list_block_items(name):
    try:
        response = client.list_text_blocklist_items(blocklist_name=name)
        return list(response)
    except HttpResponseError as e:
        print("List block items failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        print(e)
        raise


def remove_block_items(name, items):
    request = RemoveBlockItemsOptions(block_item_ids=[i.block_item_id for i in items])
    try:
        client.remove_block_items(blocklist_name=name, body=request)
        return True
    except HttpResponseError as e:
        print("Remove block items failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return False
        print(e)
        raise


def add_block_items(name, items):
    block_items = [TextBlockItemInfo(text=i) for i in items]
    try:
        response = client.add_block_items(
            blocklist_name=name,
            body=AddBlockItemsOptions(block_items=block_items),
        )
        return response.value
    except HttpResponseError as e:
        print("Add block items failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        print(e)
        raise


def get_block_item(name, item_id):
    try:
        return client.get_text_blocklist_item(blocklist_name=name, block_item_id=item_id)
    except HttpResponseError as e:
        print("Get block item failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        print(e)
        raise


def analyze_text_with_blocklists(name, text):
    try:
        response = client.analyze_text(AnalyzeTextOptions(text=text, blocklist_names=[name], break_by_blocklists=False))
        return response.blocklists_match_results
    except HttpResponseError as e:
        print("Analyze text failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        print(e)
        raise


def delete_blocklist(name):
    try:
        client.delete_text_blocklist(blocklist_name=name)
        return True
    except HttpResponseError as e:
        print("Delete blocklist failed.")
        if e.error is not None:
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return False
        print(e)
        raise


if __name__ == "__main__":
    blocklist_name = "TestBlocklist"
    blocklist_description = "Test blocklist management."

    # list blocklists
    result = list_text_blocklists()
    if result is not None:
        print("List blocklists: ")
        for l in result:
            print(l)

    # create blocklist
    create_or_update_text_blocklist(name=blocklist_name, description=blocklist_description)
    result = get_text_blocklist(blocklist_name)
    if result is not None:
        print("Blocklist created: {}".format(result))

    block_item_text_1 = "k*ll"
    block_item_text_2 = "h*te"
    input_text = "I h*te you and I want to k*ll you."

    # add block items
    result = add_block_items(name=blocklist_name, items=[block_item_text_1, block_item_text_2])
    if result is not None:
        print("Block items added: {}".format(result))

    # remove one blocklist item
    if remove_block_items(name=blocklist_name, items=[result[0]]):
        print("Block item removed: {}".format(result[0]))

    result = list_block_items(name=blocklist_name)
    if result is not None:
        print("Remaining block items: {}".format(result))

    # analyze text
    print("Waiting for blocklist service update...")
    time.sleep(30)
    match_results = analyze_text_with_blocklists(name=blocklist_name, text=input_text)
    for match_result in match_results:
        print("Block item was hit, offset={}, length={}.".format(match_result.offset, match_result.length))
        block_item = get_block_item(blocklist_name, match_result.block_item_id)
        if block_item is not None:
            print("Get block item: {}".format(block_item))

    # delete blocklist
    if delete_blocklist(name=blocklist_name):
        print("Blocklist {} deleted successfully.".format(blocklist_name))
    print("Waiting for blocklist service update...")
    time.sleep(30)

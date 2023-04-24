import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import *
from azure.core.exceptions import HttpResponseError
import time


class ManageBlocklist(object):
    def __init__(self):
        CONTENT_SAFETY_KEY = os.environ["CONTENT_SAFETY_KEY"]
        CONTENT_SAFETY_ENDPOINT = os.environ["CONTENT_SAFETY_ENDPOINT"]

        # Create an Content Safety client
        self.client = ContentSafetyClient(CONTENT_SAFETY_ENDPOINT, AzureKeyCredential(CONTENT_SAFETY_KEY))

    def list_text_blocklists(self):
        try:
            return self.client.list_text_blocklists()
        except HttpResponseError as e:
            print("List text blocklists failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

    def create_or_update_text_blocklist(self, name, description):
        try:
            return self.client.create_or_update_text_blocklist(
                blocklist_name=name, resource=TextBlocklist(description=description)
            )
        except HttpResponseError as e:
            print("Create or update text blocklist failed. ")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

    def get_text_blocklist(self, name):
        try:
            return self.client.get_text_blocklist(blocklist_name=name)
        except HttpResponseError as e:
            print("Get text blocklist failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

    def list_block_items(self, name):
        try:
            response = self.client.list_text_blocklist_items(blocklist_name=name)
            return list(response)
        except HttpResponseError as e:
            print("List block items failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

    def remove_block_items(self, name, items):
        request = RemoveBlockItemsOptions(block_item_ids=[i.block_item_id for i in items])
        try:
            self.client.remove_block_items(blocklist_name=name, body=request)
            return True
        except HttpResponseError as e:
            print("Remove block items failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return False
        except Exception as e:
            print(e)
            return False

    def add_block_items(self, name, items):
        block_items = [TextBlockItemInfo(text=i) for i in items]
        try:
            response = self.client.add_block_items(
                blocklist_name=name,
                body=AddBlockItemsOptions(block_items=block_items),
            )
        except HttpResponseError as e:
            print("Add block items failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None

        except Exception as e:
            print(e)
            return None

        return response.value

    def get_block_item(self, name, item_id):
        try:
            return self.client.get_text_blocklist_item(blocklist_name=name, block_item_id=item_id)
        except HttpResponseError as e:
            print("Get block item failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

    def analyze_text_with_blocklists(self, name, text):
        try:
            response = self.client.analyze_text(
                AnalyzeTextOptions(text=text, blocklist_names=[name], break_by_blocklists=False)
            )
        except HttpResponseError as e:
            print("Analyze text failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

        return response.blocklists_match_results

    def delete_blocklist(self, name):
        try:
            self.client.delete_text_blocklist(blocklist_name=name)
            return True
        except HttpResponseError as e:
            print("Delete blocklist failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return False
        except Exception as e:
            print(e)
            return False


if __name__ == "__main__":
    sample = ManageBlocklist()

    blocklist_name = "Test Blocklist"
    blocklist_description = "Test blocklist management."

    # list blocklists
    result = sample.list_text_blocklists()
    if result is not None:
        print("List blocklists: ")
        for l in result:
            print(l)

    # create blocklist
    sample.create_or_update_text_blocklist(name=blocklist_name, description=blocklist_description)
    result = sample.get_text_blocklist(blocklist_name)
    if result is not None:
        print("Blocklist created: {}".format(result))

    block_item_text_1 = "k*ll"
    block_item_text_2 = "h*te"
    input_text = "I h*te you and I want to k*ll you."

    # add block items
    result = sample.add_block_items(name=blocklist_name, items=[block_item_text_1, block_item_text_2])
    if result is not None:
        print("Block items added: {}".format(result))

    # remove one blocklist item
    if sample.remove_block_items(name=blocklist_name, items=[result[0]]):
        print("Block item removed: {}".format(result[0]))

    result = sample.list_block_items(name=blocklist_name)
    if result is not None:
        print("Remaining block items: {}".format(result))

    # analyze text
    print("Waiting for blocklist service update...")
    time.sleep(30)
    match_results = sample.analyze_text_with_blocklists(name=blocklist_name, text=input_text)
    for match_result in match_results:
        print("Block item was hit, offset={}, length={}.".format(match_result.offset, match_result.length))
        block_item = sample.get_block_item(blocklist_name, match_result.block_item_id)
        if block_item is not None:
            print("Get block item: {}".format(block_item))

    # delete blocklist
    if sample.delete_blocklist(name=blocklist_name):
        print("Blocklist {} deleted successfully.".format(blocklist_name))
    print("Waiting for blocklist service update...")
    time.sleep(30)

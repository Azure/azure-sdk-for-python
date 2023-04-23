import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import *
from azure.core.exceptions import HttpResponseError

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
            print("Get text blocklists failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

    def create_or_update_text_blocklist(self, name, description):
        try:
            response = self.client.create_or_update_text_blocklist(blocklist_name=name,
                                                                   resource=TextBlocklist(description=description))
        except HttpResponseError as e:
            print("Create or update text blocklist failed. ")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None
        except Exception as e:
            print(e)
            return None

        return response

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

    def add_block_items(self, name, item):
        # check if item already exists
        for i in self.client.list_text_blocklist_items(blocklist_name=name):
            if i.text == item:
                return i

        # add item if not exists
        try:
            response = self.client.add_block_items(blocklist_name=name,
                                        body=AddBlockItemsOptions(
                                           block_items=[TextBlockItemInfo(text="f*ck"),
                                                        TextBlockItemInfo(text="h*te")]))
        except HttpResponseError as e:
            print("Add block items failed.")
            print("Error code: {}".format(e.error.code))
            print("Error message: {}".format(e.error.message))
            return None

        except Exception as e:
            print(e)
            return None

        return response.block_items


    def analyze_text_with_blocklists(self, name, text):
        try:
            response = self.client.analyze_text(AnalyzeTextOptions(text=text, blocklist_names=[name],
                                                                   break_by_blocklists=False))
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
        print("Get blocklists: ")
        for l in result:
            print(l)

    # create blocklist
    result = sample.create_or_update_text_blocklist(name=blocklist_name, description=blocklist_description)
    if result is not None:
        print("Blocklist created: {}".format(result))

    # get blocklist
    result = sample.get_text_blocklist(blocklist_name)
    if result is not None:
        print("Get blocklist: {}".format(result))

    block_item_text = "h*te"
    input_text = "I h*te you"

    # add block items
    result = sample.add_block_items(name=blocklist_name, item=block_item_text)
    print("Block items added: {}".format(result))

    # analyze text
    result = sample.analyze_text_with_blocklists(name=blocklist_name, text=input_text)
    for match_result in result:
        print("Block item {} in blocklist {} was hit, offset={}, length={}."
              .format(match_result.block_item_text,
                      match_result.blocklist_name,
                      match_result.offset,
                      match_result.length))

    # delete blocklist
    if sample.delete_blocklist(name=blocklist_name):
        print("Blocklist {} deleted successfully.".format(blocklist_name))



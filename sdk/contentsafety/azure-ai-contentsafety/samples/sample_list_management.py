import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import *


class ListManagement(object):
    def list_management(self):
        SUBSCRIPTION_KEY = "19b54286b8ac49fc8d064eded98dd48e"
        CONTENT_SAFETY_ENDPOINT = "https://cm-carnegie-ppe-use.ppe.cognitiveservices.azure.com/"

        #create an Content Safety client
        client = ContentSafetyClient(CONTENT_SAFETY_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

        #build request
        request = TextList(description="A test list")

        # analyze text
        try:
            LIST_NAME = "test-list"

            # list text lists
            all_test_lists = client.list_text_lists()
            print(next(all_test_lists))

            # create list
            response = client.create_or_update_list(list_name=LIST_NAME, resource=request)

            # get list
            test_list = client.get_text_list(list_name=LIST_NAME)
            print(test_list)

            # add items to list
            add_items_request = BatchCreateTextListItemsRequest(items=[TextListItemInfo(text="test item 1", language="en"),
                                                                      TextListItemInfo(text="test item 2", language="fr")])
            client.add_items(list_name=LIST_NAME, body=add_items_request)

            # list items
            test_items = client.list_text_list_items(list_name=LIST_NAME)
            test_item_id = next(test_items).item_id

            # get item
            test_item = client.get_text_list_item(list_name=LIST_NAME, item_id=test_item_id)

            # remove items from list
            remove_items_request = BatchDeleteTextListItemsRequest(item_ids=[test_item_id])
            client.remove_items(remove_items_request)

            # delete list
            client.delete_text_list(list_name="test-list")
        except Exception as e:
            print(
                "Error code: {}".format(e.error.code),
                "Error message: {}".format(e.error.message),
            )
if __name__=="__main__":
    sample = ListManagement()
    sample.list_management()

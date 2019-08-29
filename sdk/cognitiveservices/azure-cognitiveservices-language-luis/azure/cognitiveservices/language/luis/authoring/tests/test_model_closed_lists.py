from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from baseTest import *
import unittest


class ModelClosedListsTests(unittest.TestCase):

    @use_client
    def test_list_closed_lists(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])
        result = client.model.list_closed_lists(global_app_id, "0.1")
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert(len(result) > 0)

    @use_client
    def test_add_closed_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert(list_id != empty_id)

    @use_client
    def test_get_closed_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])
        list = client.model.get_closed_list(global_app_id, "0.1", list_id)
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert("States" == list.name)
        assert(3 == len(list.sub_lists))

    @use_client
    def test_update_closed_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])
        update = {
            'name': "New States",
            'sub_lists': [
                {
                    "canonical_form": "Texas",
                    "list": ["tx", "texas"]
                }
            ]
        }
        client.model.update_closed_list(
            global_app_id, "0.1", list_id, update['sub_lists'], update['name'])
        updated = client.model.get_closed_list(global_app_id, "0.1", list_id)
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert("New States" == updated.name)
        assert(1 == len(updated.sub_lists))
        assert("Texas" == updated.sub_lists[0].canonical_form)

    @use_client
    def test_delete_closed_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        lists = client.model.list_closed_lists(global_app_id, "0.1")
        for o in lists:
            assert(o.id != list_id)

    @use_client
    def test_patch_closed_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])

        sub = [
            {
                "canonical_form": "Texas",
                "list": ["tx", "texas"]
            },
            {
                "canonical_form": "Florida",
                "list": ["fl", "florida"]
            }
        ]

        client.model.patch_closed_list(global_app_id, "0.1", list_id, sub)
        list = client.model.get_closed_list(global_app_id, "0.1", list_id)
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert(5 == len(list.sub_lists))
        found1 = False
        found2 = False
        for o in list.sub_lists:
            if o.canonical_form == "Texas" and len(o.list) == 2:
                found1 = True
            if o.canonical_form == "Florida" and len(o.list) == 2:
                found2 = True
        assert(found1 and found2 == True)

    @use_client
    def test_add_sub_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])
        sublist_id = client.model.add_sub_list(global_app_id, "0.1", list_id, {
            "canonical_form": "Texas",
            "list": ["tx", "texas"]
        })
        list = client.model.get_closed_list(global_app_id, "0.1", list_id)
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert(4 == len(list.sub_lists))
        found = False
        for o in list.sub_lists:
            if o.canonical_form == "Texas" and len(o.list) == 2:
                found1 = True
        assert(found == True)

    @use_client
    def test_delete_sub_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])

        list = client.model.get_closed_list(global_app_id, "0.1", list_id)
        sublist_id = None
        for o in list.sub_lists:
            if o.canonical_form == "New York":
                sublist_id = o.id
        client.model.delete_sub_list(global_app_id, "0.1", list_id, sublist_id)
        list = client.model.get_closed_list(global_app_id, "0.1", list_id)
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert(2 == len(list.sub_lists))
        for o in list.sub_lists:
            assert(o.canonical_form != "New York")

    @use_client
    def test_update_sub_list(self, client: LUISAuthoringClient):
        list_id = client.model.add_closed_list(
            global_app_id, "0.1", closed_list_sample['sub_lists'], closed_list_sample['name'])

        list = client.model.get_closed_list(global_app_id, "0.1", list_id)
        sublist_id = None
        for o in list.sub_lists:
            if o.canonical_form == "New York":
                sublist_id = o.id

        client.model.update_sub_list(
            global_app_id, "0.1", list_id, sublist_id, "New Yorkers", ["NYC", "NY", "New York"])
        list = client.model.get_closed_list(global_app_id, "0.1", list_id)
        client.model.delete_closed_list(global_app_id, "0.1", list_id)
        assert(3 == len(list.sub_lists))
        for o in list.sub_lists:
            assert(o.canonical_form != "New York")

        found = False
        for o in list.sub_lists:
            if o.canonical_form == "New Yorkers" and len(o.list) == 3:
                found1 = True
        assert(found == True)

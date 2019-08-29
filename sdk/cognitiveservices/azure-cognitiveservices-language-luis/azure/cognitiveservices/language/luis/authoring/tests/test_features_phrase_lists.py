from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from baseTest import *
import unittest


class FeaturesPhraseLists(unittest.TestCase):
    @use_client
    def test_add_phrase_list(self, client: LUISAuthoringClient):
        id = client.features.add_phrase_list(global_app_id, global_version_id, {
            'name': "DayOfWeek1",
            'phrases': "monday,tuesday,wednesday,thursday,friday,saturday,sunday",
            'is_exchangeable': True
        })
        phrases = client.features.get_phrase_list(
            global_app_id, global_version_id, id)
        client.features.delete_phrase_list(
            global_app_id, global_version_id, id)

        assert(phrases is not None)
        assert("DayOfWeek1" == phrases.name)
        assert(
            "monday,tuesday,wednesday,thursday,friday,saturday,sunday" == phrases.phrases)

    @use_client
    def test_list_phrase_lists(self, client: LUISAuthoringClient):
        id = client.features.add_phrase_list(global_app_id, global_version_id, {
            'name': "DayOfWeek2",
            'phrases': "monday,tuesday,wednesday,thursday,friday,saturday,sunday",
            'is_exchangeable': True
        })
        phrases = client.features.list_phrase_lists(
            global_app_id, global_version_id)
        client.features.delete_phrase_list(
            global_app_id, global_version_id, id)
        assert(len(phrases) > 0)

    @use_client
    def test_get_phrase_list(self, client: LUISAuthoringClient):
        id = client.features.add_phrase_list(global_app_id, global_version_id, {
            'name': "DayOfWeek3",
            'phrases': "monday,tuesday,wednesday,thursday,friday,saturday,sunday",
            'is_exchangeable': True
        })
        phrase = client.features.get_phrase_list(
            global_app_id, global_version_id, id)
        client.features.delete_phrase_list(
            global_app_id, global_version_id, id)
        assert("DayOfWeek3" == phrase.name)
        assert(phrase.is_active)
        assert(phrase.is_exchangeable)

    @use_client
    def test_update_phrase_list(self, client: LUISAuthoringClient):
        id = client.features.add_phrase_list(global_app_id, global_version_id, {
            'name': "DayOfWeek4",
            'phrases': "monday,tuesday,wednesday,thursday,friday,saturday,sunday",
            'is_exchangeable': True
        })
        client.features.update_phrase_list(global_app_id, global_version_id, id, {
            'is_active': False,
            'name': "Month",
            'phrases': "january,february,march,april,may,june,july,august,september,october,november,december"
        })
        updated = client.features.get_phrase_list(
            global_app_id, global_version_id, id)
        client.features.delete_phrase_list(
            global_app_id, global_version_id, id)
        assert("Month" == updated.name)
        assert("january,february,march,april,may,june,july,august,september,october,november,december" == updated.phrases)
        assert(updated.is_active == False)

    @use_client
    def test_delete_phrase_list(self, client: LUISAuthoringClient):
        id = client.features.add_phrase_list(global_app_id, global_version_id, {
            'name': "DayOfWeek5",
            'phrases': "monday,tuesday,wednesday,thursday,friday,saturday,sunday",
            'is_exchangeable': True
        })
        phrase = client.features.get_phrase_list(
            global_app_id, global_version_id, id)
        client.features.delete_phrase_list(
            global_app_id, global_version_id, id)
        phrases = client.features.list_phrase_lists(
            global_app_id, global_version_id)
        for o in phrases:
            assert(o.id != id)

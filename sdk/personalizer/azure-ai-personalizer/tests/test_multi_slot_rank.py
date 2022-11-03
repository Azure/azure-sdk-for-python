# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers


class TestMultiSlotRank(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_rank_with_no_context_features(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        personalizer_helpers.enable_multi_slot(personalizer_endpoint, personalizer_api_key, self.is_live)
        event_id = "123456789"
        request = {"actions": get_actions(), "slots": get_slots(), "eventId": event_id}
        response = client.rank_multi_slot(request)
        assert event_id == response.get("eventId")
        slots = response.get("slots")
        assert len(slots) == len(get_slots())
        assert slots[0]['rewardActionId'] == "NewsArticle"
        assert slots[1]['rewardActionId'] == "SportsArticle"

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_rank_with_context_features(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        personalizer_helpers.enable_multi_slot(personalizer_endpoint, personalizer_api_key, self.is_live)
        event_id = "123456789"
        request = {
            "eventId": event_id,
            "actions": get_actions(),
            "slots": get_slots(),
            "contextFeatures": get_context_features()
        }
        response = client.rank_multi_slot(request)
        slots = response.get("slots")
        assert len(slots) == len(get_slots())
        assert slots[0]['rewardActionId'] == "NewsArticle"
        assert slots[1]['rewardActionId'] == "SportsArticle"


def get_actions():
    return [
        {"id": "NewsArticle", "features": [{"type": "News"}]},
        {"id": "SportsArticle", "features": [{"type": "Sports"}]},
        {"id": "EntertainmentArticle", "features": [{"type": "Entertainment"}]},
    ]


def get_context_features():
    return [
        {"user": {"profileType": "anonymousUser", "latLong": "47.6,-122.1"}},
        {"environment": {"dayOfMonth": "28", "monthOfYear": "8", "weather": "Sunny"}},
        {"device": {"mobile": True, "windows": True}},
        {"recentActivity": {"itemsInCart": 3}},
    ]


def get_slots():
    return [{
        "id": "Main Article",
        "baselineAction": "NewsArticle",
        "positionFeatures": [{"Size": "Large", "Position": "Top Middle"}],
        "excludedActions": ["SportsArticle", "EntertainmentArticle"],
        },
        {
            "id": "Side Bar",
            "baselineAction": "SportsArticle",
            "positionFeatures": [{"Size": "Small", "Position": "Bottom Right"}],
            "excludedActions": ["EntertainmentArticle"],
        }]

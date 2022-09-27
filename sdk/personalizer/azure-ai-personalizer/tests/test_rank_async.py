import pytest
from devtools_testutils import AzureRecordedTestCase
import helpers

class TestRank(AzureRecordedTestCase):

    @helpers.PersonalizerPreparer()
    @pytest.mark.asyncio
    def test_rank_with_no_context_features(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        actions = [
        {
            'id': "Person",
            'features': [
            { 'videoType': "documentary", 'videoLength': 35, 'director': "CarlSagan" },
            { 'mostWatchedByAge': "30-35" },
            ],
        }];
        request = {"actions": actions }
        client.rank(request)

    @helpers.PersonalizerPreparer()
    @pytest.mark.asyncio
    def test_rank_with_context_features(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        actions = [
        {
            "id": "Person1",
            "features": [
            { "videoType": "documentary", "videoLength": 35, "director": "CarlSagan" },
            { "mostWatchedByAge": "30-35" },
            ],
        },
        {
            "id": "Person2",
            "features": [
            { "videoType": "documentary", "videoLength": 35, "director": "CarlSagan" },
            { "mostWatchedByAge": "40-45" },
            ],
        }]
        contextFeatures = [
        { "Features": { "day": "tuesday", "time": "night", "weather": "rainy" } },
        {
            "Features": {
            "payingUser": True,
            "favoriteGenre": "documentary",
            "hoursOnSite": 0.12,
            "lastWatchedType": "movie",
            },
        }]
        eventId = "123456789"
        request = {
        "eventId": eventId,
        "actions": actions,
        "contextFeatures": contextFeatures,
        "excludedActions": ["Person1"],
        };
        client.rank(request)

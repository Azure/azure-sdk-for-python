# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
import personalizer_helpers_async

import personalizer_helpers


class TestRank(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_rank_with_no_context_features(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_client(personalizer_endpoint,
                                                                             personalizer_api_key)
        actions = [
            {
                'id': "Person",
                'features': [
                    {'videoType': "documentary", 'videoLength': 35, 'director': "CarlSagan"},
                    {'mostWatchedByAge': "30-35"},
                ],
            }];
        request = {"actions": actions}
        await client.rank(request)

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_rank_with_context_features(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_client(personalizer_endpoint,
                                                                             personalizer_api_key)
        actions = [
            {
                "id": "Video1",
                "features": [
                    {"videoType": "documentary", "videoLength": 35, "director": "CarlSagan"},
                    {"mostWatchedByAge": "30-35"},
                ],
            },
            {
                "id": "Video2",
                "features": [
                    {"videoType": "documentary", "videoLength": 35, "director": "CarlSagan"},
                    {"mostWatchedByAge": "40-45"},
                ],
            }]
        context_features = [
            {"currentContext": {"day": "tuesday", "time": "night", "weather": "rainy"}},
            {
                "userContext": {
                    "payingUser": True,
                    "favoriteGenre": "documentary",
                    "hoursOnSite": 0.12,
                    "lastWatchedType": "movie",
                },
            }]
        event_id = "123456789"
        request = {
            "eventId": event_id,
            "actions": actions,
            "contextFeatures": context_features,
            "excludedActions": ["Video1"],
        }
        await client.rank(request)

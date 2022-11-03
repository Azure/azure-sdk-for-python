# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import personalizer_helpers
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
import personalizer_helpers_async

import personalizer_helpers


class TestEventAsync(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_reward(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_client(
            personalizer_endpoint, personalizer_api_key)
        await client.reward("event_id_returned_by_rank", {"value": 1.0})

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_activate(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_client(
            personalizer_endpoint, personalizer_api_key)
        await client.activate("event_id_returned_by_rank")

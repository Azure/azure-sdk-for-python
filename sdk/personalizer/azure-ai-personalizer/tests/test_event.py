# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers

class TestEvent(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_reward(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        client.reward("event_id_returned_by_rank", {"value": 1.0})

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_activate(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        client.activate("event_id_returned_by_rank")

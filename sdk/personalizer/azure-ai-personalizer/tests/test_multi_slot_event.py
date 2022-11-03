# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers


class TestMultiSlotEvent(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_multi_slot_reward(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        personalizer_helpers.enable_multi_slot(personalizer_endpoint, personalizer_api_key, self.is_live)
        event_id = "123456789"
        client.reward_multi_slot(event_id, {"reward": [{"slotId": "slot_id_to_be_rewarded", "value": 1.0}]})

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_multi_slot_activate(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        personalizer_helpers.enable_multi_slot(personalizer_endpoint, personalizer_api_key, self.is_live)
        event_id = "123456789"
        client.activate_multi_slot(event_id)

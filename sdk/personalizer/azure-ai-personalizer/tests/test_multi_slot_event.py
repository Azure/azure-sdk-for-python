from devtools_testutils import AzureRecordedTestCase
import helpers


class TestMultiSlotEvent(AzureRecordedTestCase):

    @helpers.PersonalizerPreparer()
    def test_multi_slot_reward(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        event_id = "123456789"
        client.multi_slot_events.reward(event_id, {"reward": [{"slotId": "myslotid", "value": 1.0}]})

    @helpers.PersonalizerPreparer()
    def test_multi_slot_activate(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        event_id = "123456789"
        client.multi_slot_events.activate(event_id)

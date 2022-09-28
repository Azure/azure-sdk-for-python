from devtools_testutils import AzureTestCase
import personalizer_helpers

class TestEvent(AzureTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    def test_reward(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client =  personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        client.events.reward("myeventid", {"value": 1.0})

    @personalizer_helpers.PersonalizerPreparer()
    def test_activate(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client =  personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        client.events.activate("myeventid")

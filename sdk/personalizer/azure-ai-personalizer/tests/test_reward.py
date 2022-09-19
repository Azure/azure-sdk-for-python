import functools
from azure.ai.personalizer import PersonalizerClient
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader

PersonalizerPreparer = functools.partial(
    EnvironmentVariableLoader,
    'personalizer',
    personalizer_endpoint_single_slot="https://REDACTED.cognitiveservices.azure.com",
    personalizer_api_key_single_slot="REDACTED",
)

class TestRank(AzureRecordedTestCase):

    def create_personalizer_client(self, personalizer_endpoint_single_slot, personalizer_api_key_single_slot):
        credential = AzureKeyCredential(personalizer_api_key_single_slot)
        client = PersonalizerClient(personalizer_endpoint_single_slot, credential=credential)
        return client

    @PersonalizerPreparer()
    def test_reward(self, **kwargs):
        personalizer_endpoint_single_slot = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key_single_slot = kwargs.pop('personalizer_api_key_single_slot')
        client = self.create_personalizer_client(personalizer_endpoint_single_slot, personalizer_api_key_single_slot)
        client.events.reward("eventid", {"value": 1.0})
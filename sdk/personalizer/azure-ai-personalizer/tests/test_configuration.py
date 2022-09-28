from devtools_testutils import AzureTestCase
import personalizer_helpers
import time


def configuration_equals(actual, expected):
    assert actual.get('modelExportFrequency') == expected.get('modelExportFrequency')
    assert actual.get('defaultReward') == expected.get('defaultReward')
    assert actual.get('modelRetrainDays') == expected.get('modelRetrainDays')
    assert actual.get('rewardWaitTime') == expected.get('rewardWaitTime')
    assert actual.get('explorationPercentage') == expected.get('explorationPercentage')
    assert actual.get('logRetentionDays') == expected.get('logRetentionDays')


def policy_equals(actual, expected):
    assert actual.get('arguments') == expected.get('arguments')


class TestConfiguration(AzureTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    def test_update_configuration(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client =  personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        configuration = {
            "rewardAggregation": "average",
            "modelExportFrequency": "PT3M",
            "defaultReward": 1.0,
            "modelRetrainDays": 0,
            "rewardWaitTime": "PT4H",
            "explorationPercentage": 0.3,
            "logRetentionDays": -1,
            "learningMode": "Online",
        }
        updated_configuration = client.service_configuration.update(configuration)
        configuration_equals(configuration, updated_configuration)
        self.sleep(30)
        new_configuration = client.service_configuration.get()
        configuration_equals(new_configuration, configuration)

    @personalizer_helpers.PersonalizerPreparer()
    def test_update_policy(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client =  personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        policy = {
            "name": "app1",
            "arguments": "--cb_explore_adf --quadratic GT --quadratic MR --quadratic GR --quadratic ME --quadratic OT --quadratic OE --quadratic OR --quadratic MS --quadratic GX --ignore A --cb_type ips --epsilon 0.2",
        }
        updated_policy = client.policy.update(policy)
        self.sleep(30)
        policy_equals(updated_policy, policy)
        new_policy = client.policy.get()
        policy_equals(new_policy, policy)

    @personalizer_helpers.PersonalizerPreparer()
    def test_reset_policy(self, **kwargs):
        default_policy = {
            "name": "app1",
            "arguments": "--cb_explore_adf --epsilon 0.2 --power_t 0 -l 0.001 --cb_type mtr -q ::",
        }
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client =  personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        new_policy = client.policy.reset()
        self.sleep(30)
        policy_equals(new_policy, default_policy)

    def sleep(self, delay):
        if self.is_live:
            time.sleep(delay)

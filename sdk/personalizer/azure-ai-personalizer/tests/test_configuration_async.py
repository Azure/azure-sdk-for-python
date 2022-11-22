# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
import personalizer_helpers_async
import asyncio

import personalizer_helpers

def configuration_equals(actual, expected):
    assert actual.get('modelExportFrequency') == expected.get('modelExportFrequency')
    assert actual.get('defaultReward') == expected.get('defaultReward')
    assert actual.get('modelRetrainDays') == expected.get('modelRetrainDays')
    assert actual.get('rewardWaitTime') == expected.get('rewardWaitTime')
    assert actual.get('explorationPercentage') == expected.get('explorationPercentage')
    assert actual.get('logRetentionDays') == expected.get('logRetentionDays')


def policy_equals(actual, expected):
    assert actual.get('arguments') == expected.get('arguments')


class TestConfigurationAsync(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_update_configuration(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
        old_configuration = await client.get_service_configuration()
        configuration = {
            "rewardAggregation": "average",
            "modelExportFrequency": "PT3M",
            "defaultReward": 1.0,
            "modelRetrainDays": 2,
            "rewardWaitTime": "PT4H",
            "explorationPercentage": 0.3,
            "logRetentionDays": -1,
            "learningMode": "Online",
        }
        updated_configuration = await client.update_service_configuration(configuration)
        configuration_equals(configuration, updated_configuration)
        await self.sleep(30)
        new_configuration = await client.get_service_configuration()
        configuration_equals(new_configuration, configuration)

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_update_policy(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
        policy = {
            "name": "app1",
            "arguments": "--cb_explore_adf --quadratic GT --quadratic MR --quadratic GR --quadratic ME --quadratic OT "
                         "--quadratic OE --quadratic OR --quadratic MS --quadratic GX --ignore A --cb_type ips "
                         "--epsilon 0.2",
        }
        updated_policy = await client.update_policy(policy)
        await self.sleep(30)
        policy_equals(updated_policy, policy)
        new_policy = await client.get_policy()
        policy_equals(new_policy, policy)

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy_async
    async def test_reset_policy(self, **kwargs):
        default_policy = {
            "name": "app1",
            "arguments": "--cb_explore_adf --epsilon 0.2 --power_t 0 -l 0.001 --cb_type mtr -q ::",
        }
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_admin_client(
            personalizer_endpoint, personalizer_api_key)
        new_policy = await client.reset_policy()
        await self.sleep(30)
        policy_equals(new_policy, default_policy)

    async def sleep(self, delay):
        if self.is_live:
            await asyncio.sleep(delay)

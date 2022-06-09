# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from _router_test_case_async import AsyncRouterTestCase
from _decorators_async import RouterPreparersAsync
from _validators import DistributionPolicyValidator
from _shared.asynctestcase import AsyncCommunicationTestCase
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter.aio import RouterClient
from azure.communication.jobrouter import (
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode
)

min_concurrent_offer_count = 1
max_concurrent_offer_count = 1

distribution_modes = [
    BestWorkerMode(min_concurrent_offers = min_concurrent_offer_count,
                   max_concurrent_offers = max_concurrent_offer_count),
    LongestIdleMode(min_concurrent_offers = min_concurrent_offer_count,
                    max_concurrent_offers = max_concurrent_offer_count),
    RoundRobinMode(min_concurrent_offers = min_concurrent_offer_count,
                   max_concurrent_offers = max_concurrent_offer_count)
]


# The test class name needs to start with "Test" to get collected by pytest
class TestDistributionPolicyAsync(AsyncRouterTestCase):
    def __init__(self, method_name):
        super(TestDistributionPolicyAsync, self).__init__(method_name)

        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]

    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: RouterClient = self.create_client()
            async with router_client:
                if self._testMethodName in self.distribution_policy_ids \
                        and any(self.distribution_policy_ids[self._testMethodName]):
                    for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                        await router_client.delete_distribution_policy(identifier = policy_id)

    def setUp(self):
        super(TestDistributionPolicyAsync, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestDistributionPolicyAsync, self).tearDown()

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_distribution_policy(self):
        dp_identifier = "tst_create_dp_async"
        router_client: RouterClient = self.create_client()

        async with router_client:
            for mode in distribution_modes:
                distribution_policy_response = await router_client.create_distribution_policy(
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                self.distribution_policy_ids[self._testMethodName] = [dp_identifier]

                assert distribution_policy_response is not None
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = distribution_policy_response,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_distribution_policy(self):
        dp_identifier = "tst_update_dp_async"
        router_client: RouterClient = self.create_client()

        async with router_client:
            for mode in distribution_modes:
                # Arrange
                distribution_policy_response = await router_client.create_distribution_policy(
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                self.distribution_policy_ids[self._testMethodName] = [dp_identifier]

                assert distribution_policy_response is not None
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = distribution_policy_response,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                # Act
                mode.min_concurrent_offers = 2
                mode.max_concurrent_offers = 2
                distribution_policy_response.mode = mode

                updated_distribution_policy = await router_client.update_distribution_policy(
                    identifier = dp_identifier,
                    distribution_policy = distribution_policy_response
                )

                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = updated_distribution_policy,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_distribution_policy(self):
        dp_identifier = "tst_get_dp_async"
        router_client: RouterClient = self.create_client()

        async with router_client:
            for mode in distribution_modes:
                distribution_policy_response = await router_client.create_distribution_policy(
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                self.distribution_policy_ids[self._testMethodName] = [dp_identifier]

                assert distribution_policy_response is not None
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = distribution_policy_response,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                queried_distribution_policy = await router_client.get_distribution_policy(identifier = dp_identifier)
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = queried_distribution_policy,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_distribution_policy(self):
        dp_identifier = "tst_delete_dp_async"
        router_client: RouterClient = self.create_client()

        async with router_client:
            for mode in distribution_modes:
                distribution_policy_response = await router_client.create_distribution_policy(
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                assert distribution_policy_response is not None
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = distribution_policy_response,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                await router_client.delete_distribution_policy(identifier = dp_identifier)
                with pytest.raises(ResourceNotFoundError) as nfe:
                    await router_client.get_distribution_policy(identifier = dp_identifier)
                assert nfe.value.reason == "Not Found"
                assert nfe.value.status_code == 404

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_distribution_policy(self):
        dp_identifiers = ["tst_list_dp_1_async", "tst_list_dp_2_async", "tst_list_dp_3_async"]
        created_dp_response = {}
        policy_count = len(dp_identifiers)
        router_client: RouterClient = self.create_client()
        self.distribution_policy_ids[self._testMethodName] = []

        async with router_client:
            for identifier in dp_identifiers:
                distribution_policy_response = await router_client.create_distribution_policy(
                    identifier = identifier,
                    name = identifier,
                    offer_ttl_seconds = 10.0,
                    mode = distribution_modes[0]
                )

                # add for cleanup
                self.distribution_policy_ids[self._testMethodName].append(identifier)

                assert distribution_policy_response is not None
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = distribution_policy_response,
                    identifier = identifier,
                    name = identifier,
                    offer_ttl_seconds = 10.0,
                    mode = distribution_modes[0]
                )
                created_dp_response[distribution_policy_response.id] = distribution_policy_response

            policies = router_client.list_distribution_policies(results_per_page = 2)

            async for policy_page in policies.by_page():
                list_of_policies = [i async for i in policy_page]
                assert len(list_of_policies) <= 2

                for policy in list_of_policies:
                    response_at_creation = created_dp_response.get(policy.id, None)

                    if not response_at_creation:
                        continue

                    DistributionPolicyValidator.validate_distribution_policy(
                        distribution_policy = policy,
                        identifier = response_at_creation.id,
                        name = response_at_creation.name,
                        offer_ttl_seconds = response_at_creation.offer_ttl_seconds,
                        mode = response_at_creation.mode
                    )
                    policy_count -= 1

        # all policies created were listed
        assert policy_count == 0

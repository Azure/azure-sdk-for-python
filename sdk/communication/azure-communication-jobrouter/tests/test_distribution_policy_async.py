# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import copy
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from _router_test_case_async import AsyncRouterRecordedTestCase
from _decorators_async import RouterPreparersAsync
from _validators import DistributionPolicyValidator
from _shared.asynctestcase import AsyncCommunicationTestCase
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter.aio import RouterAdministrationClient
from azure.communication.jobrouter import (
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode, DistributionPolicy
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
class TestDistributionPolicyAsync(AsyncRouterRecordedTestCase):
    async def clean_up(self, **kwargs):
        # delete in live mode
        if not self.is_playback():
            router_client: RouterAdministrationClient = self.create_admin_client()
            async with router_client:
                if self._testMethodName in self.distribution_policy_ids \
                        and any(self.distribution_policy_ids[self._testMethodName]):
                    for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                        await router_client.delete_distribution_policy(distribution_policy_id = policy_id)

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_distribution_policy(self, **kwargs):
        dp_identifier = "tst_create_dp_async"
        router_client: RouterAdministrationClient = self.create_admin_client()

        async with router_client:
            for mode in distribution_modes:
                policy: DistributionPolicy = DistributionPolicy(
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                distribution_policy_response = await router_client.create_distribution_policy(
                    distribution_policy_id = dp_identifier,
                    distribution_policy = policy
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

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_distribution_policy(self, **kwargs):
        dp_identifier = "tst_update_dp_async"
        router_client: RouterAdministrationClient = self.create_admin_client()

        async with router_client:
            for mode in distribution_modes:
                # Arrange

                policy: DistributionPolicy = DistributionPolicy(
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                distribution_policy_response = await router_client.create_distribution_policy(
                    distribution_policy_id = dp_identifier,
                    distribution_policy = policy
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
                mode_copy = copy.deepcopy(mode)
                mode_copy.min_concurrent_offers = 2
                mode_copy.max_concurrent_offers = 2
                distribution_policy_response.mode = mode

                updated_distribution_policy = await router_client.update_distribution_policy(
                    dp_identifier,
                    distribution_policy_response
                )

                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = updated_distribution_policy,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode_copy
                )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_distribution_policy_w_kwargs(self, **kwargs):
        dp_identifier = "tst_update_dp_w_kwargs_async"
        router_client: RouterAdministrationClient = self.create_admin_client()

        async with router_client:
            for mode in distribution_modes:
                # Arrange

                policy: DistributionPolicy = DistributionPolicy(
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                distribution_policy_response = await router_client.create_distribution_policy(
                    distribution_policy_id = dp_identifier,
                    distribution_policy = policy
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
                mode_copy = copy.deepcopy(mode)
                mode_copy.min_concurrent_offers = 2
                mode_copy.max_concurrent_offers = 2
                distribution_policy_response.mode = mode_copy

                updated_distribution_policy = await router_client.update_distribution_policy(
                    dp_identifier,
                    mode = distribution_policy_response.mode
                )

                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = updated_distribution_policy,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode_copy
                )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_distribution_policy(self, **kwargs):
        dp_identifier = "tst_get_dp_async"
        router_client: RouterAdministrationClient = self.create_admin_client()

        async with router_client:
            for mode in distribution_modes:
                policy: DistributionPolicy = DistributionPolicy(
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                distribution_policy_response = await router_client.create_distribution_policy(
                    distribution_policy_id = dp_identifier,
                    distribution_policy = policy
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

                queried_distribution_policy = await router_client\
                    .get_distribution_policy(distribution_policy_id = dp_identifier)
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = queried_distribution_policy,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_distribution_policy(self, **kwargs):
        dp_identifier = "tst_delete_dp_async"
        router_client: RouterAdministrationClient = self.create_admin_client()

        async with router_client:
            for mode in distribution_modes:
                policy: DistributionPolicy = DistributionPolicy(
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                distribution_policy_response = await router_client.create_distribution_policy(
                    distribution_policy_id = dp_identifier,
                    distribution_policy = policy
                )

                assert distribution_policy_response is not None
                DistributionPolicyValidator.validate_distribution_policy(
                    distribution_policy = distribution_policy_response,
                    identifier = dp_identifier,
                    name = dp_identifier,
                    offer_ttl_seconds = 10.0,
                    mode = mode
                )

                await router_client.delete_distribution_policy(distribution_policy_id = dp_identifier)
                with pytest.raises(ResourceNotFoundError) as nfe:
                    await router_client.get_distribution_policy(distribution_policy_id = dp_identifier)
                assert nfe.value.reason == "Not Found"
                assert nfe.value.status_code == 404

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_distribution_policy(self, **kwargs):
        dp_identifiers = ["tst_list_dp_1_async", "tst_list_dp_2_async", "tst_list_dp_3_async"]
        created_dp_response = {}
        policy_count = len(dp_identifiers)
        router_client: RouterAdministrationClient = self.create_admin_client()
        self.distribution_policy_ids[self._testMethodName] = []

        async with router_client:
            for identifier in dp_identifiers:
                policy: DistributionPolicy = DistributionPolicy(
                    name = identifier,
                    offer_ttl_seconds = 10.0,
                    mode = distribution_modes[0]
                )

                distribution_policy_response = await router_client.create_distribution_policy(
                    distribution_policy_id = identifier,
                    distribution_policy = policy
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

                for policy_item in list_of_policies:
                    response_at_creation = created_dp_response.get(policy_item.distribution_policy.id, None)

                    if not response_at_creation:
                        continue

                    DistributionPolicyValidator.validate_distribution_policy(
                        distribution_policy = policy_item.distribution_policy,
                        identifier = response_at_creation.id,
                        name = response_at_creation.name,
                        offer_ttl_seconds = response_at_creation.offer_ttl_seconds,
                        mode = response_at_creation.mode
                    )
                    policy_count -= 1

        # all policies created were listed
        assert policy_count == 0

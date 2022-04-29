# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from _router_test_case import RouterTestCase
from _shared.utils import get_http_logging_policy
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter import (
    RouterClient,
    DistributionPolicy,
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

#region helpers


def validate_id(
        distribution_policy,
        id,
        **kwargs
):
    assert distribution_policy.id == id


def validate_name(
        distribution_policy,
        name,
        **kwargs
):
    assert distribution_policy.name == name


def validate_offer_ttl(
        distribution_policy,
        offer_ttl_seconds,
        **kwargs
):
    assert distribution_policy.offer_ttl_seconds == offer_ttl_seconds


def validate_longest_idle_mode(distribution_policy, mode, **kwargs):
    assert distribution_policy.mode.kind == "longest-idle"


def validate_round_robin_mode(distribution_policy, mode, **kwargs):
    assert distribution_policy.mode.kind == "round-robin"


def validate_best_worker_mode(distribution_policy, mode, **kwargs):
    assert distribution_policy.mode.kind == "best-worker"
    # TODO: Add more validations for best worker mode


def validate_distribution_mode(
        distribution_policy,
        mode,
        **kwargs
):
    assert isinstance(distribution_policy.mode, type(mode)) is True
    assert distribution_policy.mode.min_concurrent_offers == mode.min_concurrent_offers
    assert distribution_policy.mode.max_concurrent_offers == mode.max_concurrent_offers

    if isinstance(mode, LongestIdleMode):
        validate_longest_idle_mode(distribution_policy, mode)
    elif isinstance(mode, RoundRobinMode):
        validate_round_robin_mode(distribution_policy, mode)
    elif isinstance(mode, BestWorkerMode):
        validate_best_worker_mode(distribution_policy, mode)
    else:
        raise AssertionError("Unable to determine mode type")


def validate_distribution_policy(distribution_policy, **kwargs):

    if not kwargs.get("identifier", None):
        validate_id(distribution_policy, kwargs.pop("identifier"))

    if not kwargs.get("name", None):
        validate_name(distribution_policy, kwargs.pop("name"))

    if not kwargs.get("offer_ttl_seconds", None):
        validate_offer_ttl(distribution_policy, kwargs.pop("offer_ttl_seconds"))

    if not kwargs.get("mode", None):
        validate_distribution_mode(distribution_policy, kwargs.pop("mode"))

#endregion helpers


class DistributionPolicyTest(RouterTestCase):
    def __init__(self, method_name):
        super(DistributionPolicyTest, self).__init__(method_name)

    def setUp(self):
        super(DistributionPolicyTest, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint
        self.policy_ids = []

        self.router_client = RouterClient.from_connection_string(
            conn_str = self.connection_str,
            http_logging_policy=get_http_logging_policy())

    def tearDown(self):
        super(DistributionPolicyTest, self).tearDown()

        # delete in live mode
        if not self.is_playback():
            if any(self.policy_ids):
                for policy_id in self.policy_ids:
                    self.router_client.delete_distribution_policy(identifier = policy_id)

    def test_create_distribution_policy(self):
        dp_identifier = "tst_create_dp"
        for mode in distribution_modes:
            distribution_policy_response = self.router_client.upsert_distribution_policy(
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

            assert distribution_policy_response is not None
            validate_distribution_policy(
                distribution_policy = distribution_policy_response,
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

        # cleanup
        self.policy_ids.append(dp_identifier)

    def test_update_distribution_policy(self):
        dp_identifier = "tst_update_dp"
        for mode in distribution_modes:
            # Arrange
            distribution_policy_response = self.router_client.upsert_distribution_policy(
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

            assert distribution_policy_response is not None
            validate_distribution_policy(
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

            updated_distribution_policy = self.router_client.upsert_distribution_policy(
                identifier = dp_identifier,
                distribution_policy = distribution_policy_response
            )

            validate_distribution_policy(
                distribution_policy = updated_distribution_policy,
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

        # cleanup
        self.policy_ids.append(dp_identifier)

    def test_get_distribution_policy(self):
        dp_identifier = "tst_get_dp"
        for mode in distribution_modes:
            distribution_policy_response = self.router_client.upsert_distribution_policy(
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

            assert distribution_policy_response is not None
            validate_distribution_policy(
                distribution_policy = distribution_policy_response,
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

            queried_distribution_policy = self.router_client.get_distribution_policy(identifier = dp_identifier)
            validate_distribution_policy(
                distribution_policy = queried_distribution_policy,
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

        # cleanup
        self.policy_ids.append(dp_identifier)

    def test_delete_distribution_policy(self):
        dp_identifier = "tst_delete_dp"
        for mode in distribution_modes:
            distribution_policy_response = self.router_client.upsert_distribution_policy(
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

            assert distribution_policy_response is not None
            validate_distribution_policy(
                distribution_policy = distribution_policy_response,
                identifier = dp_identifier,
                name = dp_identifier,
                offer_ttl_seconds = 10.0,
                mode = mode
            )

            self.router_client.delete_distribution_policy(identifier = dp_identifier)
            with pytest.raises(ResourceNotFoundError) as nfe:
                self.router_client.get_distribution_policy(identifier = dp_identifier)
            assert nfe.value.reason == "Not Found"
            assert nfe.value.status_code == 404

    def test_list_distribution_policy(self):
        dp_identifiers = ["tst_list_dp_1", "tst_list_dp_2", "tst_list_dp_3"]
        created_dp_response = {}
        policy_count = len(dp_identifiers)
        for identifier in dp_identifiers:
            distribution_policy_response = self.router_client.upsert_distribution_policy(
                identifier = identifier,
                name = identifier,
                offer_ttl_seconds = 10.0,
                mode = distribution_modes[0]
            )

            assert distribution_policy_response is not None
            validate_distribution_policy(
                distribution_policy = distribution_policy_response,
                identifier = identifier,
                name = identifier,
                offer_ttl_seconds = 10.0,
                mode = distribution_modes[0]
            )
            created_dp_response[distribution_policy_response.id] = distribution_policy_response

        policies = self.router_client.list_distribution_policies(results_per_page = 2)
        for policy_page in policies.by_page():
            list_of_policies = list(policy_page)
            assert len(list_of_policies) <= 2

            for policy in list_of_policies:
                reponse_at_creation = created_dp_response.get(policy.id, None)

                if not reponse_at_creation:
                    continue

                validate_distribution_policy(
                    distribution_policy = policy,
                    identifier = reponse_at_creation.id,
                    name = reponse_at_creation.name,
                    offer_ttl_seconds = reponse_at_creation.offer_ttl_seconds,
                    mode = reponse_at_creation.mode
                )
                policy_count -= 1

        # all policies created were listed
        assert policy_count == 0

        # cleanup
        self.policy_ids.extend(dp_identifiers)

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Live integration test for the topic runtime filter-count properties.

The topic-level ``sql_filter_count`` / ``correlation_filter_count`` runtime
properties are served by the 2024-05 service API version (the admin client's
default) and are populated only on a service build carrying the feature, so this
test runs live only.
"""
import pytest

from azure.servicebus.management import (
    ServiceBusAdministrationClient,
    CorrelationRuleFilter,
    SqlRuleFilter,
)
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, get_credential
from sb_env_loader import ServiceBusPreparer


class TestServiceBusAdministrationClientTopicFilterCounts(AzureMgmtRecordedTestCase):
    @pytest.mark.live_test_only
    @ServiceBusPreparer()
    @recorded_by_proxy
    def test_topic_filter_counts_live(self, servicebus_fully_qualified_namespace, **kwargs):
        credential = get_credential()
        mgmt_service = ServiceBusAdministrationClient(
            fully_qualified_namespace=servicebus_fully_qualified_namespace, credential=credential
        )
        topic_name = "topic_filter_counts"
        subscription_name = "sub1"
        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)

            # A new subscription carries a default $Default rule (a SQL TrueFilter). Add an
            # explicit SQL rule and a correlation rule so the topic-level counts are non-zero.
            mgmt_service.create_rule(topic_name, subscription_name, "sqlRule", filter=SqlRuleFilter("1=1"))
            mgmt_service.create_rule(
                topic_name,
                subscription_name,
                "correlationRule",
                filter=CorrelationRuleFilter(correlation_id="abc"),
            )

            runtime_properties = mgmt_service.get_topic_runtime_properties(topic_name)

            # $Default (TrueFilter) + sqlRule = 2 SQL filters; correlationRule = 1 correlation filter.
            assert runtime_properties.sql_filter_count == 2
            assert runtime_properties.correlation_filter_count == 1
        finally:
            mgmt_service.delete_topic(topic_name)

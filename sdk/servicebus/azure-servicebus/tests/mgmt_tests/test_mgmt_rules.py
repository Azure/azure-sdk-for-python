#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import logging
import pytest

import msrest
from azure.servicebus.management import ServiceBusManagementClient, RuleDescription, CorrelationRuleFilter, SqlRuleFilter, TrueRuleFilter, FalseRuleFilter, SqlRuleAction
from utilities import get_logger
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusNamespacePreparer
)

from mgmt_test_utilities import clear_topics

_logger = get_logger(logging.DEBUG)

class ServiceBusManagementClientRuleTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_create(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "topic_testaddf"
        subscription_name = "sub_testkkk"
        rule_name_1 = 'test_rule_1'
        rule_name_2 = 'test_rule_2'
        rule_name_3 = 'test_rule_3'

        correlation_fitler = CorrelationRuleFilter(correlation_id='testcid')
        sql_rule_action = SqlRuleAction(sql_expression="SET Priority = 'low'")
        rule_1 = RuleDescription(name=rule_name_1, filter=correlation_fitler, action=sql_rule_action)

        sql_filter = SqlRuleFilter("Priority = 'low'")
        rule_2 = RuleDescription(name=rule_name_2, filter=sql_filter)

        bool_filter = TrueRuleFilter()
        rule_3 = RuleDescription(name=rule_name_3, filter=bool_filter)

        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)

            mgmt_service.create_rule(topic_name, subscription_name, rule_1)
            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name_1)
            assert type(rule_desc.filter) == CorrelationRuleFilter
            assert rule_desc.filter.correlation_id == 'testcid'
            assert rule_desc.action.sql_expression == "SET Priority = 'low'"

            mgmt_service.create_rule(topic_name, subscription_name, rule_2)
            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name_2)
            assert type(rule_desc.filter) == SqlRuleFilter
            assert rule_desc.filter.sql_expression == "Priority = 'low'"

            mgmt_service.create_rule(topic_name, subscription_name, rule_3)
            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name_3)
            assert type(rule_desc.filter) == TrueRuleFilter

        finally:
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name_1)
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name_2)
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name_3)
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_create_duplicate(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dqkodq"
        subscription_name = 'kkaqo'
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")
        rule = RuleDescription(name=rule_name, filter=sql_filter)
        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule)
            with pytest.raises(ResourceExistsError):
                mgmt_service.create_rule(topic_name, subscription_name, rule)
        finally:
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name)
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_update_success(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")
        rule = RuleDescription(name=rule_name, filter=sql_filter)

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_description, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule)

            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name)

            assert type(rule_desc.filter) == SqlRuleFilter
            assert rule_desc.filter.sql_expression == "Priority = 'low'"

            correlation_fitler = CorrelationRuleFilter(correlation_id='testcid')
            sql_rule_action = SqlRuleAction(sql_expression="SET Priority = 'low'")

            rule_desc.filter = correlation_fitler
            rule_desc.action = sql_rule_action
            mgmt_service.update_rule(topic_description, subscription_description, rule_desc)

            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name)
            assert type(rule_desc.filter) == CorrelationRuleFilter
            assert rule_desc.filter.correlation_id == 'testcid'
            assert rule_desc.action.sql_expression == "SET Priority = 'low'"

        finally:
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name)
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_update_invalid(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")
        rule = RuleDescription(name=rule_name, filter=sql_filter)

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_name, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule)

            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name)

            # handle a null update properly.
            with pytest.raises(AttributeError):
                mgmt_service.update_rule(topic_name, subscription_name, None)

            # handle an invalid type update properly.
            with pytest.raises(AttributeError):
                mgmt_service.update_rule(topic_name, subscription_name, Exception("test"))

            # change the name to a topic that doesn't exist; should fail.
            rule_desc.name = "iewdm"
            with pytest.raises(HttpResponseError):
                mgmt_service.update_rule(topic_name, subscription_description, rule_desc)
            rule_desc.name = rule_name

            # change the name to a topic with an invalid name exist; should fail.
            rule_desc.name = ''
            with pytest.raises(msrest.exceptions.ValidationError):
                mgmt_service.update_rule(topic_name, subscription_description, rule_desc)
            rule_desc.name = rule_name

        finally:
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name)
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_list_and_delete(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusManagementClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "topic_testaddf"
        subscription_name = "sub_testkkk"
        rule_name_1 = 'test_rule_1'
        rule_name_2 = 'test_rule_2'
        rule_name_3 = 'test_rule_3'

        sql_filter_1 = SqlRuleFilter("Priority = 'low'")
        sql_filter_2 = SqlRuleFilter("Priority = 'middle'")
        sql_filter_3 = SqlRuleFilter("Priority = 'high'")
        rule_1 = RuleDescription(name=rule_name_1, filter=sql_filter_1)
        rule_2 = RuleDescription(name=rule_name_2, filter=sql_filter_2)
        rule_3 = RuleDescription(name=rule_name_3, filter=sql_filter_3)

        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)

            rules = list(mgmt_service.list_rules(topic_name, subscription_name))
            assert len(rules) == 1  # by default there is a True filter

            mgmt_service.create_rule(topic_name, subscription_name, rule_1)
            mgmt_service.create_rule(topic_name, subscription_name, rule_2)
            mgmt_service.create_rule(topic_name, subscription_name, rule_3)

            rules = list(mgmt_service.list_rules(topic_name, subscription_name))
            assert len(rules) == 3 + 1

            mgmt_service.delete_rule(topic_name, subscription_name, rule_name_2)
            rules = list(mgmt_service.list_rules(topic_name, subscription_name))
            assert len(rules) == 2 + 1
            assert rules[0].name == "$Default"
            assert rules[1].name == rule_name_1
            assert type(rules[1].filter) == SqlRuleFilter
            assert rules[1].filter.sql_expression == "Priority = 'low'"
            assert rules[2].name == rule_name_3
            assert type(rules[2].filter) == SqlRuleFilter
            assert rules[2].filter.sql_expression == "Priority = 'high'"

            mgmt_service.delete_rule(topic_name, subscription_name, rule_name_1)
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name_3)

            rules = list(mgmt_service.list_rules(topic_name, subscription_name))
            assert len(rules) == 1

        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

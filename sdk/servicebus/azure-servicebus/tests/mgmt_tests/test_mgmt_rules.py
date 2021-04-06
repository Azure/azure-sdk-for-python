#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import logging
import pytest
from datetime import datetime, timedelta

import msrest
from azure.servicebus.management import ServiceBusAdministrationClient, RuleProperties, CorrelationRuleFilter, SqlRuleFilter, TrueRuleFilter, FalseRuleFilter, SqlRuleAction
from azure.servicebus.management._constants import INT32_MAX_VALUE
from utilities import get_logger
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusNamespacePreparer
)

from mgmt_test_utilities import clear_topics

_logger = get_logger(logging.DEBUG)

class ServiceBusAdministrationClientRuleTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_create(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "topic_testaddf"
        subscription_name = "sub_testkkk"
        rule_name_1 = 'test_rule_1'
        rule_name_2 = 'test_rule_2'
        rule_name_3 = 'test_rule_3'
        rule_name_4 = 'test_rule_4'

        correlation_fitler = CorrelationRuleFilter(correlation_id='testcid', properties={
            "key_string": "str1",
            "key_int": 2,
            "key_long": INT32_MAX_VALUE + 3,
            "key_bool": False,
            "key_datetime": datetime(2020, 7, 5, 11, 12, 13),
            "key_duration": timedelta(days=1, hours=2, minutes=3)
        })
        sql_rule_action = SqlRuleAction(sql_expression="SET Priority = @param", parameters={
            "@param": datetime(2020, 7, 5, 11, 12, 13),
        })

        sql_filter = SqlRuleFilter("Priority = @param1", parameters={
            "@param1": "str1",
        })

        bool_filter = TrueRuleFilter()

        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)

            mgmt_service.create_rule(topic_name, subscription_name, rule_name_1, filter=correlation_fitler, action=sql_rule_action)
            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name_1)
            rule_properties = rule_desc.filter.properties
            assert type(rule_desc.filter) == CorrelationRuleFilter
            assert rule_desc.filter.correlation_id == 'testcid'
            assert rule_desc.action.sql_expression == "SET Priority = @param"
            assert rule_desc.action.parameters["@param"] == datetime(2020, 7, 5, 11, 12, 13)
            assert rule_properties["key_string"] == "str1"
            assert rule_properties["key_int"] == 2
            assert rule_properties["key_long"] == INT32_MAX_VALUE + 3
            assert rule_properties["key_bool"] is False
            assert rule_properties["key_datetime"] == datetime(2020, 7, 5, 11, 12, 13)
            assert rule_properties["key_duration"] == timedelta(days=1, hours=2, minutes=3)

            mgmt_service.create_rule(topic_name, subscription_name, rule_name_2, filter=sql_filter)
            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name_2)
            assert type(rule_desc.filter) == SqlRuleFilter
            assert rule_desc.filter.sql_expression == "Priority = @param1"
            assert rule_desc.filter.parameters["@param1"] == "str1"

            mgmt_service.create_rule(topic_name, subscription_name, rule_name_3, filter=bool_filter)
            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name_3)
            assert type(rule_desc.filter) == TrueRuleFilter

            mgmt_service.create_rule(topic_name, subscription_name, rule_name_4)
            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name_4)
            assert type(rule_desc.filter) == TrueRuleFilter

        finally:
            try:
                mgmt_service.delete_rule(topic_name, subscription_name, rule_name_1)
            except:
                pass
            try:
                mgmt_service.delete_rule(topic_name, subscription_name, rule_name_2)
            except:
                pass
            try:
                mgmt_service.delete_rule(topic_name, subscription_name, rule_name_3)
            except:
                pass
            try:
                mgmt_service.delete_rule(topic_name, subscription_name, rule_name_4)
            except:
                pass
            try:
                mgmt_service.delete_subscription(topic_name, subscription_name)
            except:
                pass
            try:
                mgmt_service.delete_topic(topic_name)
            except:
                pass


    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_create_duplicate(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dqkodq"
        subscription_name = 'kkaqo'
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")
        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule_name, filter=sql_filter)
            with pytest.raises(ResourceExistsError):
                mgmt_service.create_rule(topic_name, subscription_name, rule_name, filter=sql_filter)
        finally:
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name)
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_update_success(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_description.name, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule_name, filter=sql_filter)

            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name)

            assert type(rule_desc.filter) == SqlRuleFilter
            assert rule_desc.filter.sql_expression == "Priority = 'low'"

            correlation_fitler = CorrelationRuleFilter(correlation_id='testcid')
            sql_rule_action = SqlRuleAction(sql_expression="SET Priority = 'low'")

            rule_desc.filter = correlation_fitler
            rule_desc.action = sql_rule_action
            mgmt_service.update_rule(topic_description.name, subscription_description.name, rule_desc)

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
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_name, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule_name, filter=sql_filter)

            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name)

            # handle a null update properly.
            with pytest.raises(TypeError):
                mgmt_service.update_rule(topic_name, subscription_name, None)

            # handle an invalid type update properly.
            with pytest.raises(TypeError):
                mgmt_service.update_rule(topic_name, subscription_name, Exception("test"))

            # change the name to a topic that doesn't exist; should fail.
            rule_desc.name = "iewdm"
            with pytest.raises(HttpResponseError):
                mgmt_service.update_rule(topic_name, subscription_description.name, rule_desc)
            rule_desc.name = rule_name

            # change the name to a topic with an invalid name exist; should fail.
            rule_desc.name = ''
            with pytest.raises(msrest.exceptions.ValidationError):
                mgmt_service.update_rule(topic_name, subscription_description.name, rule_desc)
            rule_desc.name = rule_name

        finally:
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name)
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_list_and_delete(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "topic_testaddf"
        subscription_name = "sub_testkkk"
        rule_name_1 = 'test_rule_1'
        rule_name_2 = 'test_rule_2'
        rule_name_3 = 'test_rule_3'

        sql_filter_1 = SqlRuleFilter("Priority = 'low'")
        sql_filter_2 = SqlRuleFilter("Priority = 'middle'")
        sql_filter_3 = SqlRuleFilter("Priority = 'high'")

        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)

            rules = list(mgmt_service.list_rules(topic_name, subscription_name))
            assert len(rules) == 1  # by default there is a True filter

            mgmt_service.create_rule(topic_name, subscription_name, rule_name_1, filter=sql_filter_1)
            mgmt_service.create_rule(topic_name, subscription_name, rule_name_2, filter=sql_filter_2)
            mgmt_service.create_rule(topic_name, subscription_name, rule_name_3, filter=sql_filter_3)

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

    def test_rule_properties_constructor(self):
        with pytest.raises(TypeError):
            RuleProperties("randomname")

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_rule_update_dict_success(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjruid"
        subscription_name = "eqkovcd"
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_description.name, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule_name, filter=sql_filter)

            rule_desc = mgmt_service.get_rule(topic_name, subscription_name, rule_name)

            assert type(rule_desc.filter) == SqlRuleFilter
            assert rule_desc.filter.sql_expression == "Priority = 'low'"

            correlation_fitler = CorrelationRuleFilter(correlation_id='testcid')
            sql_rule_action = SqlRuleAction(sql_expression="SET Priority = 'low'")

            rule_desc.filter = correlation_fitler
            rule_desc.action = sql_rule_action
            rule_desc_dict = dict(rule_desc)
            mgmt_service.update_rule(topic_description.name, subscription_description.name, rule_desc_dict)

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
    def test_mgmt_rule_update_dict_error(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjruid"
        subscription_name = "eqkovcd"
        rule_name = 'rule'
        sql_filter = SqlRuleFilter("Priority = 'low'")

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_description.name, subscription_name)
            mgmt_service.create_rule(topic_name, subscription_name, rule_name, filter=sql_filter)

            # send in rule dict without non-name keyword args
            rule_description_only_name = {"name": topic_name}
            with pytest.raises(TypeError):
                mgmt_service.update_rule(topic_description.name, subscription_description.name, rule_description_only_name)

        finally:
            mgmt_service.delete_rule(topic_name, subscription_name, rule_name)
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

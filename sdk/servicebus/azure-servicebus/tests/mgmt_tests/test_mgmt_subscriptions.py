#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import logging
import pytest
import datetime

import msrest
from azure.servicebus.management import ServiceBusAdministrationClient, SubscriptionProperties
from utilities import get_logger
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusNamespacePreparer
)

from mgmt_test_utilities import clear_topics

_logger = get_logger(logging.DEBUG)


class ServiceBusAdministrationClientSubscriptionTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_create_by_name(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "topic_testaddf"
        subscription_name = "sub_testkkk"

        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)
            subscription = mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription.name == subscription_name
            assert subscription.availability_status == 'Available'
            assert subscription.status == 'Active'
        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_create_with_subscription_description(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "iweidk"
        subscription_name = "kdosako"
        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(
                topic_name,
                subscription_name=subscription_name,
                auto_delete_on_idle=datetime.timedelta(minutes=10),
                dead_lettering_on_message_expiration=True,
                default_message_time_to_live=datetime.timedelta(minutes=11),
                enable_batched_operations=True,
                lock_duration=datetime.timedelta(seconds=13),
                max_delivery_count=14,
                requires_session=True
            )
            subscription = mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription.name == subscription_name
            assert subscription.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert subscription.dead_lettering_on_message_expiration == True
            assert subscription.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert subscription.enable_batched_operations == True
            assert subscription.lock_duration == datetime.timedelta(seconds=13)
            assert subscription.max_delivery_count == 14
            assert subscription.requires_session == True
        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_create_duplicate(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dqkodq"
        subscription_name = 'kkaqo'
        try:
            mgmt_service.create_topic(topic_name)
            mgmt_service.create_subscription(topic_name, subscription_name)
            with pytest.raises(ResourceExistsError):
                mgmt_service.create_subscription(topic_name, subscription_name)
        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_update_success(self, servicebus_namespace_connection_string, servicebus_namespace, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjrui"
        subscription_name = "eqkovc"

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_description.name, subscription_name)

            # Try updating one setting.
            subscription_description.lock_duration = datetime.timedelta(minutes=2)
            mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription_description.lock_duration == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            subscription_description.auto_delete_on_idle = datetime.timedelta(minutes=10)
            subscription_description.dead_lettering_on_message_expiration = True
            subscription_description.default_message_time_to_live = datetime.timedelta(minutes=11)
            subscription_description.lock_duration = datetime.timedelta(seconds=12)
            subscription_description.max_delivery_count = 14
            # topic_description.enable_partitioning = True # Cannot be changed after creation
            # topic_description.requires_session = True # Cannot be changed after creation

            mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = mgmt_service.get_subscription(topic_description.name, subscription_name)

            assert subscription_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert subscription_description.dead_lettering_on_message_expiration == True
            assert subscription_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert subscription_description.max_delivery_count == 14
            assert subscription_description.lock_duration == datetime.timedelta(seconds=12)
            # assert topic_description.enable_partitioning == True
            # assert topic_description.requires_session == True

            # Finally, test forward_to (separately, as it changes auto_delete_on_idle when you enable it.)
            subscription_description.forward_to = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, topic_name)
            subscription_description.forward_dead_lettered_messages_to = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, topic_name)
            mgmt_service.update_subscription(topic_description.name, subscription_description)
            subscription_description = mgmt_service.get_subscription(topic_description.name, subscription_name)
            # Note: We endswith to avoid the fact that the servicebus_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert subscription_description.forward_to.endswith(".servicebus.windows.net/{}".format(topic_name))
            assert subscription_description.forward_dead_lettered_messages_to.endswith(".servicebus.windows.net/{}".format(topic_name))

        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_update_invalid(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dfjfj"
        subscription_name = "kwqxc"
        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_name, subscription_name)

            # handle a null update properly.
            with pytest.raises(TypeError):
                mgmt_service.update_subscription(topic_name, None)

            # handle an invalid type update properly.
            with pytest.raises(TypeError):
                mgmt_service.update_subscription(topic_name, Exception("test"))

            # change the name to a topic that doesn't exist; should fail.
            subscription_description.name = "iewdm"
            with pytest.raises(HttpResponseError):
                mgmt_service.update_subscription(topic_name, subscription_description)
            subscription_description.name = subscription_name

            # change the name to a topic with an invalid name exist; should fail.
            subscription_description.name = ''
            with pytest.raises(msrest.exceptions.ValidationError):
                mgmt_service.update_subscription(topic_name, subscription_description)
            subscription_description.name = topic_name

            # change to a setting with an invalid value; should still fail.
            subscription_description.lock_duration = datetime.timedelta(days=25)
            with pytest.raises(HttpResponseError):
                mgmt_service.update_subscription(topic_name, subscription_description)
            subscription_description.lock_duration = datetime.timedelta(minutes=5)
        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_delete(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = 'test_topicgda'
        subscription_name_1 = 'test_sub1da'
        subscription_name_2 = 'test_sub2gcv'
        mgmt_service.create_topic(topic_name)

        mgmt_service.create_subscription(topic_name, subscription_name_1)
        subscriptions = list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 1

        mgmt_service.create_subscription(topic_name, subscription_name_2)
        subscriptions = list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 2

        description = mgmt_service.get_subscription(topic_name, subscription_name_1)
        mgmt_service.delete_subscription(topic_name, description.name)

        subscriptions = list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 1 and subscriptions[0].name == subscription_name_2

        mgmt_service.delete_subscription(topic_name, subscription_name_2)

        subscriptions = list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 0
        mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_list(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = 'lkoqxc'
        subscription_name_1 = 'testsub1'
        subscription_name_2 = 'testsub2'

        mgmt_service.create_topic(topic_name)
        subscriptions = list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 0
        mgmt_service.create_subscription(topic_name, subscription_name_1)
        mgmt_service.create_subscription(topic_name, subscription_name_2)
        subscriptions = list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 2
        assert subscriptions[0].name == subscription_name_1
        assert subscriptions[1].name == subscription_name_2
        mgmt_service.delete_subscription(topic_name, subscription_name_1)
        mgmt_service.delete_subscription(topic_name, subscription_name_2)
        subscriptions = list(mgmt_service.list_subscriptions(topic_name))
        assert len(subscriptions) == 0
        mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_list_runtime_properties(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = 'dkoamv'
        subscription_name = 'cxqplc'
        mgmt_service.create_topic(topic_name)

        subs = list(mgmt_service.list_subscriptions(topic_name))
        subs_infos = list(mgmt_service.list_subscriptions_runtime_properties(topic_name))

        assert len(subs) == len(subs_infos) == 0

        mgmt_service.create_subscription(topic_name, subscription_name)

        subs = list(mgmt_service.list_subscriptions(topic_name))
        subs_infos = list(mgmt_service.list_subscriptions_runtime_properties(topic_name))

        assert len(subs) == 1 and len(subs_infos) == 1

        assert subs[0].name == subs_infos[0].name == subscription_name

        info = subs_infos[0]

        assert info.accessed_at_utc is not None
        assert info.updated_at_utc is not None

        assert info.active_message_count == 0
        assert info.dead_letter_message_count == 0
        assert info.transfer_dead_letter_message_count == 0
        assert info.transfer_message_count == 0

        mgmt_service.delete_subscription(topic_name, subscription_name)
        subs_infos = list(mgmt_service.list_subscriptions_runtime_properties(topic_name))
        assert len(subs_infos) == 0

        mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_get_runtime_properties_basic(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = 'dcvxqa'
        subscription_name = 'xvazzag'

        mgmt_service.create_topic(topic_name)
        mgmt_service.create_subscription(topic_name, subscription_name)
        sub_runtime_properties = mgmt_service.get_subscription_runtime_properties(topic_name, subscription_name)

        assert sub_runtime_properties
        assert sub_runtime_properties.name == subscription_name
        assert sub_runtime_properties.created_at_utc is not None
        assert sub_runtime_properties.accessed_at_utc is not None
        assert sub_runtime_properties.updated_at_utc is not None

        assert sub_runtime_properties.active_message_count == 0
        assert sub_runtime_properties.dead_letter_message_count == 0
        assert sub_runtime_properties.transfer_dead_letter_message_count == 0
        assert sub_runtime_properties.transfer_message_count == 0

        mgmt_service.delete_subscription(topic_name, subscription_name)
        mgmt_service.delete_topic(topic_name)

    def test_subscription_properties_constructor(self):
        with pytest.raises(TypeError):
            SubscriptionProperties("randomname")

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_update_dict_success(self, servicebus_namespace_connection_string, servicebus_namespace, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjruid"
        subscription_name = "eqkovcd"

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_description.name, subscription_name)
            subscription_description_dict = dict(subscription_description)

            # Try updating one setting.
            subscription_description_dict["lock_duration"] = datetime.timedelta(minutes=2)
            mgmt_service.update_subscription(topic_description.name, subscription_description_dict)
            subscription_description = mgmt_service.get_subscription(topic_name, subscription_name)
            assert subscription_description.lock_duration == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            subscription_description_dict = dict(subscription_description)
            subscription_description_dict["auto_delete_on_idle"] = datetime.timedelta(minutes=10)
            subscription_description_dict["dead_lettering_on_message_expiration"] = True
            subscription_description_dict["default_message_time_to_live"] = datetime.timedelta(minutes=11)
            subscription_description_dict["lock_duration"] = datetime.timedelta(seconds=12)
            subscription_description_dict["max_delivery_count"] = 14
            # topic_description.enable_partitioning = True # Cannot be changed after creation
            # topic_description.requires_session = True # Cannot be changed after creation

            mgmt_service.update_subscription(topic_description.name, subscription_description_dict)
            subscription_description = mgmt_service.get_subscription(topic_description.name, subscription_name)

            assert subscription_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert subscription_description.dead_lettering_on_message_expiration == True
            assert subscription_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert subscription_description.max_delivery_count == 14
            assert subscription_description.lock_duration == datetime.timedelta(seconds=12)
            # assert topic_description.enable_partitioning == True
            # assert topic_description.requires_session == True

            # Finally, test forward_to (separately, as it changes auto_delete_on_idle when you enable it.)
            subscription_description_dict = dict(subscription_description)
            subscription_description_dict["forward_to"] = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, topic_name)
            subscription_description_dict["forward_dead_lettered_messages_to"] = "sb://{}.servicebus.windows.net/{}".format(servicebus_namespace.name, topic_name)
            mgmt_service.update_subscription(topic_description.name, subscription_description_dict)
            subscription_description = mgmt_service.get_subscription(topic_description.name, subscription_name)
            # Note: We endswith to avoid the fact that the servicebus_namespace_name is replacered locally but not in the properties bag, and still test this.
            assert subscription_description.forward_to.endswith(".servicebus.windows.net/{}".format(topic_name))
            assert subscription_description.forward_dead_lettered_messages_to.endswith(".servicebus.windows.net/{}".format(topic_name))

        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_subscription_update_dict_error(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dfjdfj"
        subscription_name = "kwqxd"

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            subscription_description = mgmt_service.create_subscription(topic_description.name, subscription_name)
            # send in subscription dict without non-name keyword args
            subscription_description_only_name = {"name": topic_name}
            with pytest.raises(TypeError):
                mgmt_service.update_subscription(topic_description.name, subscription_description_only_name)
        finally:
            mgmt_service.delete_subscription(topic_name, subscription_name)
            mgmt_service.delete_topic(topic_name)

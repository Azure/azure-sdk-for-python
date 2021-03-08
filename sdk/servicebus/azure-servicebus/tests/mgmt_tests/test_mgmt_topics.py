#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import logging
import pytest
import datetime

import msrest
from azure.servicebus.management import ServiceBusAdministrationClient, TopicProperties
from utilities import get_logger
from azure.core.exceptions import HttpResponseError, ResourceExistsError

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusNamespacePreparer
)

from mgmt_test_utilities import clear_topics

_logger = get_logger(logging.DEBUG)


class ServiceBusAdministrationClientTopicTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_create_by_name(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "topic_testaddf"

        try:
            mgmt_service.create_topic(topic_name)
            topic = mgmt_service.get_topic(topic_name)
            assert topic.name == topic_name
            assert topic.availability_status == 'Available'
            assert topic.status == 'Active'
        finally:
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_create_with_topic_description(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "iweidk"
        try:
            mgmt_service.create_topic(
                topic_name=topic_name,
                auto_delete_on_idle=datetime.timedelta(minutes=10),
                default_message_time_to_live=datetime.timedelta(minutes=11),
                duplicate_detection_history_time_window=datetime.timedelta(minutes=12),
                enable_batched_operations=True,
                enable_express=True,
                enable_partitioning=True,
                max_size_in_megabytes=3072
            )
            topic = mgmt_service.get_topic(topic_name)
            assert topic.name == topic_name
            assert topic.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert topic.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert topic.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
            assert topic.enable_batched_operations
            assert topic.enable_express
            assert topic.enable_partitioning
            assert topic.max_size_in_megabytes % 3072 == 0
        finally:
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_create_duplicate(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dqkodq"
        try:
            mgmt_service.create_topic(topic_name)
            with pytest.raises(ResourceExistsError):
                mgmt_service.create_topic(topic_name)
        finally:
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_update_success(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjrui"

        try:
            topic_description = mgmt_service.create_topic(topic_name)

            # Try updating one setting.
            topic_description.default_message_time_to_live = datetime.timedelta(minutes=2)
            mgmt_service.update_topic(topic_description)
            topic_description = mgmt_service.get_topic(topic_name)
            assert topic_description.default_message_time_to_live == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            topic_description.auto_delete_on_idle = datetime.timedelta(minutes=10)
            topic_description.default_message_time_to_live = datetime.timedelta(minutes=11)
            topic_description.duplicate_detection_history_time_window = datetime.timedelta(minutes=12)
            topic_description.enable_batched_operations = True
            topic_description.enable_express = True
            # topic_description.enable_partitioning = True # Cannot be changed after creation
            topic_description.max_size_in_megabytes = 3072
            # topic_description.requires_duplicate_detection = True # Read only
            # topic_description.requires_session = True # Cannot be changed after creation
            topic_description.support_ordering = True

            mgmt_service.update_topic(topic_description)
            topic_description = mgmt_service.get_topic(topic_name)

            assert topic_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert topic_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert topic_description.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
            assert topic_description.enable_batched_operations == True
            assert topic_description.enable_express == True
            # assert topic_description.enable_partitioning == True
            assert topic_description.max_size_in_megabytes == 3072
            # assert topic_description.requires_duplicate_detection == True
            # assert topic_description.requires_session == True
            assert topic_description.support_ordering == True
        finally:
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_update_invalid(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dfjfj"
        try:
            topic_description = mgmt_service.create_topic(topic_name)

            # handle a null update properly.
            with pytest.raises(TypeError):
                mgmt_service.update_topic(None)

            # handle an invalid type update properly.
            with pytest.raises(TypeError):
                mgmt_service.update_topic(Exception("test"))

            # change the name to a topic that doesn't exist; should fail.
            topic_description.name = "iewdm"
            with pytest.raises(HttpResponseError):
                mgmt_service.update_topic(topic_description)
            topic_description.name = topic_name

            # change the name to a topic with an invalid name exist; should fail.
            topic_description.name = ''
            with pytest.raises(msrest.exceptions.ValidationError):
                mgmt_service.update_topic(topic_description)
            topic_description.name = topic_name

            # change to a setting with an invalid value; should still fail.
            topic_description.duplicate_detection_history_time_window = datetime.timedelta(days=25)
            with pytest.raises(HttpResponseError):
                mgmt_service.update_topic(topic_description)
            topic_description.duplicate_detection_history_time_window = datetime.timedelta(minutes=5)
        finally:
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_delete(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        mgmt_service.create_topic('test_topic')
        topics = list(mgmt_service.list_topics())
        assert len(topics) == 1

        mgmt_service.create_topic('txt/.-_123')
        topics = list(mgmt_service.list_topics())
        assert len(topics) == 2

        description = mgmt_service.get_topic('test_topic')
        mgmt_service.delete_topic(description.name)

        topics = list(mgmt_service.list_topics())
        assert len(topics) == 1 and topics[0].name == 'txt/.-_123'

        description = mgmt_service.get_topic('txt/.-_123')
        mgmt_service.delete_topic(description.name)

        topics = list(mgmt_service.list_topics())
        assert len(topics) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_list(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topics = list(mgmt_service.list_topics())
        assert len(topics) == 0
        mgmt_service.create_topic("test_topic_1")
        mgmt_service.create_topic("test_topic_2")
        topics = list(mgmt_service.list_topics())
        assert len(topics) == 2
        assert topics[0].name == "test_topic_1"
        assert topics[1].name == "test_topic_2"
        mgmt_service.delete_topic("test_topic_1")
        mgmt_service.delete_topic("test_topic_2")
        topics = list(mgmt_service.list_topics())
        assert len(topics) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_list_runtime_properties(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topics = list(mgmt_service.list_topics())
        topics_infos = list(mgmt_service.list_topics_runtime_properties())

        assert len(topics) == len(topics_infos) == 0

        mgmt_service.create_topic("test_topic")

        topics = list(mgmt_service.list_topics())
        topics_infos = list(mgmt_service.list_topics_runtime_properties())

        assert len(topics) == 1 and len(topics_infos) == 1

        assert topics[0].name == topics_infos[0].name == "test_topic"

        info = topics_infos[0]

        assert info.accessed_at_utc is not None
        assert info.updated_at_utc is not None
        assert info.subscription_count is 0

        assert info.size_in_bytes == 0
        assert info.scheduled_message_count == 0

        mgmt_service.delete_topic("test_topic")
        topics_infos = list(mgmt_service.list_topics_runtime_properties())
        assert len(topics_infos) == 0

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_get_runtime_properties_basic(self, servicebus_namespace_connection_string):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        mgmt_service.create_topic("test_topic")
        topic_runtime_properties = mgmt_service.get_topic_runtime_properties("test_topic")

        assert topic_runtime_properties
        assert topic_runtime_properties.name == "test_topic"
        assert topic_runtime_properties.created_at_utc is not None
        assert topic_runtime_properties.accessed_at_utc is not None
        assert topic_runtime_properties.updated_at_utc is not None
        assert topic_runtime_properties.size_in_bytes == 0
        assert topic_runtime_properties.subscription_count is 0
        assert topic_runtime_properties.scheduled_message_count == 0
        mgmt_service.delete_topic("test_topic")

    def test_topic_properties_constructor(self):
        with pytest.raises(TypeError):
            TopicProperties("randomname")

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_update_dict_success(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "fjruid"

        try:
            topic_description = mgmt_service.create_topic(topic_name)
            topic_description_dict = dict(topic_description)

            # Try updating one setting.
            topic_description_dict["default_message_time_to_live"] = datetime.timedelta(minutes=2)
            mgmt_service.update_topic(topic_description_dict)
            topic_description = mgmt_service.get_topic(topic_name)
            assert topic_description.default_message_time_to_live == datetime.timedelta(minutes=2)

            # Now try updating all settings.
            topic_description_dict = dict(topic_description)
            topic_description_dict["auto_delete_on_idle"] = datetime.timedelta(minutes=10)
            topic_description_dict["default_message_time_to_live"] = datetime.timedelta(minutes=11)
            topic_description_dict["duplicate_detection_history_time_window"] = datetime.timedelta(minutes=12)
            topic_description_dict["enable_batched_operations"] = True
            topic_description_dict["enable_express"] = True
            # topic_description_dict["enable_partitioning"] = True # Cannot be changed after creation
            topic_description_dict["max_size_in_megabytes"] = 3072
            # topic_description_dict["requires_duplicate_detection"] = True # Read only
            # topic_description_dict["requires_session"] = True # Cannot be changed after creation
            topic_description_dict["support_ordering"] = True

            mgmt_service.update_topic(topic_description_dict)
            topic_description = mgmt_service.get_topic(topic_name)

            assert topic_description.auto_delete_on_idle == datetime.timedelta(minutes=10)
            assert topic_description.default_message_time_to_live == datetime.timedelta(minutes=11)
            assert topic_description.duplicate_detection_history_time_window == datetime.timedelta(minutes=12)
            assert topic_description.enable_batched_operations == True
            assert topic_description.enable_express == True
            # assert topic_description.enable_partitioning == True
            assert topic_description.max_size_in_megabytes == 3072
            # assert topic_description.requires_duplicate_detection == True
            # assert topic_description.requires_session == True
            assert topic_description.support_ordering == True
        finally:
            mgmt_service.delete_topic(topic_name)

    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_topic_update_dict_error(self, servicebus_namespace_connection_string, **kwargs):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        clear_topics(mgmt_service)
        topic_name = "dfjdfj"
        try:
            topic_description = mgmt_service.create_topic(topic_name)
            # send in topic dict without non-name keyword args
            topic_description_only_name = {"name": topic_name}
            with pytest.raises(TypeError):
                mgmt_service.update_topic(topic_description_only_name)
        finally:
            mgmt_service.delete_topic(topic_name)

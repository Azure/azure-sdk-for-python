# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import base64
import os
import random
import sys
import time
import unittest

from datetime import datetime
from azure.common import (
    AzureHttpError,
    AzureMissingResourceHttpError,
    AzureConflictHttpError,
)
from azure.servicebus._control_client._http import HTTPError
from azure.servicebus._control_client import (
    AZURE_SERVICEBUS_NAMESPACE,
    AZURE_SERVICEBUS_ACCESS_KEY,
    AZURE_SERVICEBUS_ISSUER,
    AzureServiceBusPeekLockError,
    AzureServiceBusResourceNotFound,
    Message,
    Queue,
    Rule,
    ServiceBusService,
    Subscription,
    Topic,
)
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from .servicebus_testcase import ServiceBusTestCase


class ServiceBusServiceBusTest(ServiceBusTestCase):

    def setUp(self):
        super(ServiceBusServiceBusTest, self).setUp()

        self.sbs = ServiceBusService(
            self.settings.SERVICEBUS_NAME,
            shared_access_key_name=self.settings.SERVICEBUS_SAS_KEY_NAME,
            shared_access_key_value=self.settings.SERVICEBUS_SAS_KEY_VALUE,
        )

        self._set_service_options(self.sbs, self.settings)

        self.queue_name = self.get_resource_name('utqueue')
        self.topic_name = self.get_resource_name('uttopic')

        self.additional_queue_names = []
        self.additional_topic_names = []

    def tearDown(self):
        if not self.is_playback():
            try:
                self.sbs.delete_queue(self.queue_name)
            except:
                pass

            for name in self.additional_queue_names:
                try:
                    self.sbs.delete_queue(name)
                except:
                    pass

            try:
                self.sbs.delete_topic(self.topic_name)
            except:
                pass

            for name in self.additional_topic_names:
                try:
                    self.sbs.delete_topic(name)
                except:
                    pass

        return super(ServiceBusServiceBusTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _create_queue(self, queue_name):
        self.sbs.create_queue(queue_name, None, True)

    def _create_queue_and_send_msg(self, queue_name, msg):
        self._create_queue(queue_name)
        self.sbs.send_queue_message(queue_name, msg)

    def _create_topic(self, topic_name):
        self.sbs.create_topic(topic_name, None, True)

    def _create_topic_and_subscription(self, topic_name, subscription_name):
        self._create_topic(topic_name)
        self._create_subscription(topic_name, subscription_name)

    def _create_subscription(self, topic_name, subscription_name):
        self.sbs.create_subscription(topic_name, subscription_name, None, True)

    #--Test cases for service bus service -------------------------------------

    def test_create_service_bus_missing_arguments(self):
        # Arrange
        if AZURE_SERVICEBUS_NAMESPACE in os.environ:
            del os.environ[AZURE_SERVICEBUS_NAMESPACE]
        if AZURE_SERVICEBUS_ACCESS_KEY in os.environ:
            del os.environ[AZURE_SERVICEBUS_ACCESS_KEY]
        if AZURE_SERVICEBUS_ISSUER in os.environ:
            del os.environ[AZURE_SERVICEBUS_ISSUER]

        # Act
        with self.assertRaises(ValueError):
            sbs = ServiceBusService()

        # Assert

    @unittest.skip('ACS is deprecated and this test cannot be run live anymore')
    def test_create_service_bus_env_variables(self):
        # Arrange
        os.environ[AZURE_SERVICEBUS_NAMESPACE] = self.settings.SERVICEBUS_NAME
        os.environ[AZURE_SERVICEBUS_ACCESS_KEY] = self.settings.SERVICEBUS_ACS_KEY
        os.environ[AZURE_SERVICEBUS_ISSUER] = 'owner'

        # Act
        sbs = ServiceBusService()

        if AZURE_SERVICEBUS_NAMESPACE in os.environ:
            del os.environ[AZURE_SERVICEBUS_NAMESPACE]
        if AZURE_SERVICEBUS_ACCESS_KEY in os.environ:
            del os.environ[AZURE_SERVICEBUS_ACCESS_KEY]
        if AZURE_SERVICEBUS_ISSUER in os.environ:
            del os.environ[AZURE_SERVICEBUS_ISSUER]

        # Assert
        self.assertIsNotNone(sbs)
        self.assertEqual(sbs.service_namespace, self.settings.SERVICEBUS_NAME)
        self.assertEqual(sbs.account_key, self.settings.SERVICEBUS_ACS_KEY)
        self.assertEqual(sbs.issuer, 'owner')

    #--Test cases for queues --------------------------------------------------
    @record
    def test_create_queue_no_options(self):
        # Arrange

        # Act
        created = self.sbs.create_queue(self.queue_name)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_queue_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_queue(self.queue_name, None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_queue_with_options(self):
        # Arrange

        # Act
        queue_options = Queue()
        queue_options.default_message_time_to_live = 'PT1M'
        queue_options.duplicate_detection_history_time_window = 'PT5M'
        queue_options.enable_batched_operations = False
        queue_options.dead_lettering_on_message_expiration = False
        queue_options.lock_duration = 'PT1M'
        queue_options.max_delivery_count = 15
        queue_options.max_size_in_megabytes = 5120
        queue_options.message_count = 0
        queue_options.requires_duplicate_detection = False
        queue_options.requires_session = False
        queue_options.size_in_bytes = 0
        created = self.sbs.create_queue(self.queue_name, queue_options)

        # Assert
        self.assertTrue(created)
        queue = self.sbs.get_queue(self.queue_name)
        self.assertEqual('PT1M', queue.default_message_time_to_live)
        self.assertEqual('PT5M', queue.duplicate_detection_history_time_window)
        self.assertEqual(False, queue.enable_batched_operations)
        self.assertEqual(False, queue.dead_lettering_on_message_expiration)
        self.assertEqual('PT1M', queue.lock_duration)
        self.assertEqual(15, queue.max_delivery_count)
        self.assertEqual(5120, queue.max_size_in_megabytes)
        self.assertEqual(0, queue.message_count)
        self.assertEqual(False, queue.requires_duplicate_detection)
        self.assertEqual(False, queue.requires_session)
        self.assertEqual(0, queue.size_in_bytes)

    @record
    def test_create_queue_with_already_existing_queue(self):
        # Arrange

        # Act
        created1 = self.sbs.create_queue(self.queue_name)
        created2 = self.sbs.create_queue(self.queue_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_create_queue_with_already_existing_queue_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_queue(self.queue_name)
        with self.assertRaises(AzureConflictHttpError):
            self.sbs.create_queue(self.queue_name, None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_get_queue_with_existing_queue(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        queue = self.sbs.get_queue(self.queue_name)

        # Assert
        self.assertIsNotNone(queue)
        self.assertEqual(queue.name, self.queue_name)

    @record
    def test_get_queue_with_non_existing_queue(self):
        # Arrange

        # Act
        with self.assertRaises(AzureServiceBusResourceNotFound):
            resp = self.sbs.get_queue(self.queue_name)

        # Assert

    @record
    def test_list_queues(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        queues = self.sbs.list_queues()
        for queue in queues:
            name = queue.name

        # Assert
        self.assertIsNotNone(queues)
        self.assertNamedItemInContainer(queues, self.queue_name)

    @record
    def test_list_queues_with_special_chars(self):
        # Arrange
        # Name must start and end with an alphanumeric and can only contain
        # letters, numbers, periods, hyphens, forward slashes and underscores.
        other_queue_name = self.queue_name + 'txt/.-_123'
        self.additional_queue_names = [other_queue_name]
        self._create_queue(other_queue_name)

        # Act
        queues = self.sbs.list_queues()

        # Assert
        self.assertIsNotNone(queues)
        self.assertNamedItemInContainer(queues, other_queue_name)

    @record
    def test_delete_queue_with_existing_queue(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        deleted = self.sbs.delete_queue(self.queue_name)

        # Assert
        self.assertTrue(deleted)
        queues = self.sbs.list_queues()
        self.assertNamedItemNotInContainer(queues, self.queue_name)

    @record
    def test_delete_queue_with_existing_queue_fail_not_exist(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        deleted = self.sbs.delete_queue(self.queue_name, True)

        # Assert
        self.assertTrue(deleted)
        queues = self.sbs.list_queues()
        self.assertNamedItemNotInContainer(queues, self.queue_name)

    @record
    def test_delete_queue_with_non_existing_queue(self):
        # Arrange

        # Act
        deleted = self.sbs.delete_queue(self.queue_name)

        # Assert
        self.assertFalse(deleted)

    @record
    def test_delete_queue_with_non_existing_queue_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sbs.delete_queue(self.queue_name, True)

        # Assert

    @record
    def test_send_queue_message(self):
        # Arrange
        self._create_queue(self.queue_name)
        sent_msg = Message(b'send message')

        # Act
        self.sbs.send_queue_message(self.queue_name, sent_msg)

        # Assert

    @record
    def test_send_queue_message_batch(self):
        # https://docs.microsoft.com/rest/api/servicebus/send-message-batch

        # Arrange
        self._create_queue(self.queue_name)
        sent_msg_1 = Message(b'This is the first message',
                             broker_properties={'Label': 'M1',
                                                'TimeToLiveTimeSpan': '0.00:00:40'}
                             )
        sent_msg_2 = Message(b'This is the second message',
                             broker_properties={'Label': 'M2'},
                             custom_properties={'Priority': 'Low'}
                             )
        sent_msg_3 = Message(b'This is the third message',
                             broker_properties={'Label': 'M3'},
                             custom_properties={'Priority': 'Medium',
                                                'Customer': 'ABC'}
                             )

        # Act
        self.sbs.send_queue_message_batch(self.queue_name, [sent_msg_1, sent_msg_2, sent_msg_3])
        received_msg_1 = self.sbs.receive_queue_message(self.queue_name, False)
        received_msg_2 = self.sbs.receive_queue_message(self.queue_name, False)
        received_msg_3 = self.sbs.receive_queue_message(self.queue_name, False)

        # Assert
        self.assertEqual(sent_msg_1.body, received_msg_1.body)
        self.assertEqual(sent_msg_2.body, received_msg_2.body)
        self.assertEqual(sent_msg_3.body, received_msg_3.body)

    @record
    def test_receive_queue_message_read_delete_mode(self):
        # Assert
        sent_msg = Message(b'receive message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_receive_queue_message_with_broker_properties(self):
        # Assert
        sent_msg = Message(b'receive message')
        sent_msg.broker_properties = \
            '{"ForcePersistence": false, "Label": "My label" }'
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)
        self.assertEqual("My label", received_msg.broker_properties['Label'])
        self.assertEqual(False, received_msg.broker_properties['ForcePersistence'])

    @record
    def test_receive_queue_message_with_broker_properties_as_a_dict(self):
        # Assert
        sent_msg = Message(b'receive message')
        sent_msg.broker_properties = \
            {"ForcePersistence": False, "Label": "My label"}
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)
        self.assertEqual("My label", received_msg.broker_properties['Label'])
        self.assertEqual(False, received_msg.broker_properties['ForcePersistence'])

    @record
    def test_receive_queue_message_read_delete_mode_throws_on_delete(self):
        # Assert
        sent_msg = Message(b'receive message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)
        with self.assertRaises(AzureServiceBusPeekLockError):
            received_msg.delete()

        # Assert

    @record
    def test_receive_queue_message_read_delete_mode_throws_on_unlock(self):
        # Assert
        sent_msg = Message(b'receive message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)
        with self.assertRaises(AzureServiceBusPeekLockError):
            received_msg.renew_lock()
        with self.assertRaises(AzureServiceBusPeekLockError):
            received_msg.unlock()

        # Assert

    @record
    def test_receive_queue_message_peek_lock_mode(self):
        # Arrange
        sent_msg = Message(b'peek lock message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, True)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_receive_queue_message_delete(self):
        # Arrange
        sent_msg = Message(b'peek lock message delete')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, True)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_receive_queue_message_delete_with_slash(self):
        # Arrange
        self.queue_name = self.get_resource_name('ut/queue')
        sent_msg = Message(b'peek lock message delete')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, True)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_receive_queue_message_unlock(self):
        # Arrange
        sent_msg = Message(b'peek lock message unlock')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, True)
        received_msg.renew_lock()
        received_msg.unlock()

        # Assert
        received_again_msg = self.sbs.receive_queue_message(
            self.queue_name, True)
        received_again_msg.delete()
        self.assertIsNotNone(received_msg)
        self.assertIsNotNone(received_again_msg)
        self.assertEqual(sent_msg.body, received_msg.body)
        self.assertEqual(received_again_msg.body, received_msg.body)

    @record
    def test_get_dead_letter_queue(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        dead_letter_name = ServiceBusService.format_dead_letter_queue_name(
            self.queue_name)
        try:
            self.sbs.receive_queue_message(dead_letter_name, timeout=2)
        except Exception:
            # Assert
            self.fail("Dead Letter queue not found")

    @record
    def test_send_queue_message_with_custom_message_type(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        sent_msg = Message(
            b'<text>peek lock message custom message type</text>',
            type='text/xml')
        self.sbs.send_queue_message(self.queue_name, sent_msg)
        received_msg = self.sbs.receive_queue_message(self.queue_name, True, 5)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual('text/xml', received_msg.type)

    @record
    def test_send_queue_message_with_custom_message_properties(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        props = {'hello': 'world',
                 'number': 42,
                 'active': True,
                 'deceased': False,
                 'large': 8555111000,
                 'floating': 3.14,
                 'dob': datetime(2011, 12, 14),
                 'double_quote_message': 'This "should" work fine',
                 'quote_message': "This 'should' work fine"}
        sent_msg = Message(b'message with properties', custom_properties=props)
        self.sbs.send_queue_message(self.queue_name, sent_msg)
        received_msg = self.sbs.receive_queue_message(self.queue_name, True, 5)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(received_msg.custom_properties['hello'], 'world')
        self.assertEqual(received_msg.custom_properties['number'], 42)
        self.assertEqual(received_msg.custom_properties['active'], True)
        self.assertEqual(received_msg.custom_properties['deceased'], False)
        self.assertEqual(received_msg.custom_properties['large'], 8555111000)
        self.assertEqual(received_msg.custom_properties['floating'], 3.14)
        self.assertEqual(
            received_msg.custom_properties['dob'], datetime(2011, 12, 14))
        self.assertEqual(
            received_msg.custom_properties['double_quote_message'], 'This "should" work fine')
        self.assertEqual(
            received_msg.custom_properties['quote_message'], "This 'should' work fine")

    @unittest.skip('flaky')
    def test_receive_queue_message_timeout_5(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        start = datetime.now()
        received_msg = self.sbs.receive_queue_message(self.queue_name, True, 5)
        duration = datetime.now() - start

        # Assert
        self.assertGreater(duration.total_seconds(), 3)
        self.assertLess(duration.total_seconds(), 10)
        self.assertIsNotNone(received_msg)
        self.assertIsNone(received_msg.body)

    @unittest.skip('flaky')
    def test_receive_queue_message_timeout_50(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        start = datetime.now()
        received_msg = self.sbs.receive_queue_message(
            self.queue_name, True, 50)
        duration = datetime.now() - start

        # Assert
        self.assertGreater(duration.total_seconds(), 48)
        self.assertLess(duration.total_seconds(), 55)
        self.assertIsNotNone(received_msg)
        self.assertIsNone(received_msg.body)

    @unittest.skip('flaky')
    def test_receive_queue_message_timeout_50_http_timeout(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        self.sbs.timeout = 10
        try:
            received_msg = self.sbs.receive_queue_message(
                self.queue_name, True, 50)
            self.assertTrue(False, 'Failed to trigger an HTTP timeout')
        except:
            pass

        # Assert

    #--Test cases for topics/subscriptions ------------------------------------
    @record
    def test_create_topic_no_options(self):
        # Arrange

        # Act
        created = self.sbs.create_topic(self.topic_name)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_topic_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_topic(self.topic_name, None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_topic_with_options(self):
        # Arrange

        # Act
        topic_options = Topic()
        topic_options.default_message_time_to_live = 'PT1M'
        topic_options.duplicate_detection_history_time_window = 'PT5M'
        topic_options.enable_batched_operations = False
        topic_options.max_size_in_megabytes = 5120
        topic_options.requires_duplicate_detection = False
        topic_options.size_in_bytes = 0
        # TODO: MaximumNumberOfSubscriptions is not supported?
        created = self.sbs.create_topic(self.topic_name, topic_options)

        # Assert
        self.assertTrue(created)
        topic = self.sbs.get_topic(self.topic_name)
        self.assertEqual('PT1M', topic.default_message_time_to_live)
        self.assertEqual('PT5M', topic.duplicate_detection_history_time_window)
        self.assertEqual(False, topic.enable_batched_operations)
        self.assertEqual(5120, topic.max_size_in_megabytes)
        self.assertEqual(False, topic.requires_duplicate_detection)
        self.assertEqual(0, topic.size_in_bytes)

    @record
    def test_create_topic_with_already_existing_topic(self):
        # Arrange

        # Act
        created1 = self.sbs.create_topic(self.topic_name)
        created2 = self.sbs.create_topic(self.topic_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_create_topic_with_already_existing_topic_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_topic(self.topic_name)
        with self.assertRaises(AzureConflictHttpError):
            self.sbs.create_topic(self.topic_name, None, True)

        # Assert
        self.assertTrue(created)

    @record
    @unittest.skip('undesirable output, this is old enough, backwards compatibility can be deleted')
    def test_topic_backwards_compatibility_warning(self):
        # Arrange
        topic_options = Topic()
        topic_options.max_size_in_megabytes = 5120

        # Act
        val = topic_options.max_size_in_mega_bytes

        # Assert
        self.assertEqual(val, 5120)

        # Act
        topic_options.max_size_in_mega_bytes = 1024

        # Assert
        self.assertEqual(topic_options.max_size_in_megabytes, 1024)

    @record
    def test_get_topic_with_existing_topic(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        topic = self.sbs.get_topic(self.topic_name)

        # Assert
        self.assertIsNotNone(topic)
        self.assertEqual(topic.name, self.topic_name)

    @record
    def test_get_topic_with_non_existing_topic(self):
        # Arrange

        # Act
        with self.assertRaises(AzureServiceBusResourceNotFound):
            self.sbs.get_topic(self.topic_name)

        # Assert

    @record
    def test_list_topics(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        topics = self.sbs.list_topics()
        for topic in topics:
            name = topic.name

        # Assert
        self.assertIsNotNone(topics)
        self.assertNamedItemInContainer(topics, self.topic_name)

    @record
    def test_list_topics_with_special_chars(self):
        # Arrange
        # Name must start and end with an alphanumeric and can only contain
        # letters, numbers, periods, hyphens, forward slashes and underscores.
        other_topic_name = self.topic_name + 'txt/.-_123'
        self.additional_topic_names = [other_topic_name]
        self._create_topic(other_topic_name)

        # Act
        topics = self.sbs.list_topics()

        # Assert
        self.assertIsNotNone(topics)
        self.assertNamedItemInContainer(topics, other_topic_name)

    @record
    def test_delete_topic_with_existing_topic(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        deleted = self.sbs.delete_topic(self.topic_name)

        # Assert
        self.assertTrue(deleted)
        topics = self.sbs.list_topics()
        self.assertNamedItemNotInContainer(topics, self.topic_name)

    @record
    def test_delete_topic_with_existing_topic_fail_not_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        deleted = self.sbs.delete_topic(self.topic_name, True)

        # Assert
        self.assertTrue(deleted)
        topics = self.sbs.list_topics()
        self.assertNamedItemNotInContainer(topics, self.topic_name)

    @record
    def test_delete_topic_with_non_existing_topic(self):
        # Arrange

        # Act
        deleted = self.sbs.delete_topic(self.topic_name)

        # Assert
        self.assertFalse(deleted)

    @record
    def test_delete_topic_with_non_existing_topic_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sbs.delete_topic(self.topic_name, True)

        # Assert

    @record
    def test_create_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created = self.sbs.create_subscription(
            self.topic_name, 'MySubscription')

        # Assert
        self.assertTrue(created)

    @record
    def test_create_subscription_with_options(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        subscription_options = Subscription()
        subscription_options.dead_lettering_on_filter_evaluation_exceptions = False
        subscription_options.dead_lettering_on_message_expiration = False
        subscription_options.default_message_time_to_live = 'PT15M'
        subscription_options.enable_batched_operations = False
        subscription_options.lock_duration = 'PT1M'
        subscription_options.max_delivery_count = 15
        #message_count is read-only
        subscription_options.message_count = 0
        subscription_options.requires_session = False
        created = self.sbs.create_subscription(
            self.topic_name, 'MySubscription', subscription_options)

        # Assert
        self.assertTrue(created)
        subscription = self.sbs.get_subscription(
            self.topic_name, 'MySubscription')
        self.assertEqual(
            False, subscription.dead_lettering_on_filter_evaluation_exceptions)
        self.assertEqual(
            False, subscription.dead_lettering_on_message_expiration)
        self.assertEqual('PT15M', subscription.default_message_time_to_live)
        self.assertEqual(False, subscription.enable_batched_operations)
        self.assertEqual('PT1M', subscription.lock_duration)
        # self.assertEqual(15, subscription.max_delivery_count) #no idea why
        # max_delivery_count is always 10
        self.assertEqual(0, subscription.message_count)
        self.assertEqual(False, subscription.requires_session)

    @record
    def test_create_subscription_fail_on_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created = self.sbs.create_subscription(
            self.topic_name, 'MySubscription', None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_subscription_with_already_existing_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created1 = self.sbs.create_subscription(
            self.topic_name, 'MySubscription')
        created2 = self.sbs.create_subscription(
            self.topic_name, 'MySubscription')

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_create_subscription_with_already_existing_subscription_fail_on_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created = self.sbs.create_subscription(
            self.topic_name, 'MySubscription')
        with self.assertRaises(AzureConflictHttpError):
            self.sbs.create_subscription(
                self.topic_name, 'MySubscription', None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_list_subscriptions(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription2')

        # Act
        subscriptions = self.sbs.list_subscriptions(self.topic_name)

        # Assert
        self.assertIsNotNone(subscriptions)
        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0].name, 'MySubscription2')

    @record
    def test_get_subscription_with_existing_subscription(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription3')

        # Act
        subscription = self.sbs.get_subscription(
            self.topic_name, 'MySubscription3')

        # Assert
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.name, 'MySubscription3')

    @record
    def test_get_subscription_with_non_existing_subscription(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription3')

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sbs.get_subscription(self.topic_name, 'MySubscription4')

        # Assert

    @record
    def test_delete_subscription_with_existing_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)
        self._create_subscription(self.topic_name, 'MySubscription4')
        self._create_subscription(self.topic_name, 'MySubscription5')

        # Act
        deleted = self.sbs.delete_subscription(
            self.topic_name, 'MySubscription4')

        # Assert
        self.assertTrue(deleted)
        subscriptions = self.sbs.list_subscriptions(self.topic_name)
        self.assertIsNotNone(subscriptions)
        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0].name, 'MySubscription5')

    @record
    def test_delete_subscription_with_existing_subscription_fail_not_exist(self):
        # Arrange
        self._create_topic(self.topic_name)
        self._create_subscription(self.topic_name, 'MySubscription4')
        self._create_subscription(self.topic_name, 'MySubscription5')

        # Act
        deleted = self.sbs.delete_subscription(
            self.topic_name, 'MySubscription4', True)

        # Assert
        self.assertTrue(deleted)
        subscriptions = self.sbs.list_subscriptions(self.topic_name)
        self.assertIsNotNone(subscriptions)
        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0].name, 'MySubscription5')

    @record
    def test_delete_subscription_with_non_existing_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        deleted = self.sbs.delete_subscription(
            self.topic_name, 'MySubscription')

        # Assert
        self.assertFalse(deleted)

    @record
    def test_delete_subscription_with_non_existing_subscription_fail_not_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sbs.delete_subscription(
                self.topic_name, 'MySubscription', True)

        # Assert

    @record
    def test_create_rule_no_options(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1')

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_no_options_fail_on_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_with_already_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created1 = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1')
        created2 = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1')

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_create_rule_with_already_existing_rule_fail_on_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1')
        with self.assertRaises(AzureConflictHttpError):
            self.sbs.create_rule(
                self.topic_name, 'MySubscription', 'MyRule1', None, True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_with_options_sql_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'SqlFilter'
        rule1.filter_expression = 'number > 40'
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_with_options_true_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'TrueFilter'
        rule1.filter_expression = '1=1'
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_with_options_false_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'FalseFilter'
        rule1.filter_expression = '1=0'
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_with_options_correlation_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'CorrelationFilter'
        rule1.filter_expression = 'myid'
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_with_options_empty_rule_action(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.action_type = 'EmptyRuleAction'
        rule1.action_expression = ''
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_rule_with_options_sql_rule_action(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.action_type = 'SqlRuleAction'
        rule1.action_expression = "SET number = 5"
        created = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    @record
    def test_list_rules(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        resp = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule2')

        # Act
        rules = self.sbs.list_rules(self.topic_name, 'MySubscription')

        # Assert
        self.assertEqual(len(rules), 2)

    @record
    def test_get_rule_with_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule = self.sbs.get_rule(self.topic_name, 'MySubscription', '$Default')

        # Assert
        self.assertIsNotNone(rule)
        self.assertEqual(rule.name, '$Default')

    @record
    def test_get_rule_with_non_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sbs.get_rule(self.topic_name,
                              'MySubscription', 'NonExistingRule')

        # Assert

    @record
    def test_get_rule_with_existing_rule_with_options(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_rule = Rule()
        sent_rule.filter_type = 'SqlFilter'
        sent_rule.filter_expression = 'number > 40'
        sent_rule.action_type = 'SqlRuleAction'
        sent_rule.action_expression = 'SET number = 5'
        self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule1', sent_rule)

        # Act
        received_rule = self.sbs.get_rule(
            self.topic_name, 'MySubscription', 'MyRule1')

        # Assert
        self.assertIsNotNone(received_rule)
        self.assertEqual(received_rule.name, 'MyRule1')
        self.assertEqual(received_rule.filter_type, sent_rule.filter_type)
        self.assertEqual(received_rule.filter_expression,
                         sent_rule.filter_expression)
        self.assertEqual(received_rule.action_type, sent_rule.action_type)
        self.assertEqual(received_rule.action_expression,
                         sent_rule.action_expression)

    @record
    def test_delete_rule_with_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        resp = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule3')
        resp = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule4')

        # Act
        deleted1 = self.sbs.delete_rule(
            self.topic_name, 'MySubscription', 'MyRule4')
        deleted2 = self.sbs.delete_rule(
            self.topic_name, 'MySubscription', '$Default')

        # Assert
        self.assertTrue(deleted1)
        self.assertTrue(deleted2)
        rules = self.sbs.list_rules(self.topic_name, 'MySubscription')
        self.assertIsNotNone(rules)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, 'MyRule3')

    @record
    def test_delete_rule_with_existing_rule_fail_not_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        resp = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule3')
        resp = self.sbs.create_rule(
            self.topic_name, 'MySubscription', 'MyRule4')

        # Act
        deleted1 = self.sbs.delete_rule(
            self.topic_name, 'MySubscription', 'MyRule4', True)
        deleted2 = self.sbs.delete_rule(
            self.topic_name, 'MySubscription', '$Default', True)

        # Assert
        self.assertTrue(deleted1)
        self.assertTrue(deleted2)
        rules = self.sbs.list_rules(self.topic_name, 'MySubscription')
        self.assertIsNotNone(rules)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, 'MyRule3')

    @record
    def test_delete_rule_with_non_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        deleted = self.sbs.delete_rule(
            self.topic_name, 'MySubscription', 'NonExistingRule')

        # Assert
        self.assertFalse(deleted)

    @record
    def test_delete_rule_with_non_existing_rule_fail_not_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sbs.delete_rule(
                self.topic_name, 'MySubscription', 'NonExistingRule', True)

        # Assert

    @record
    def test_send_topic_message(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')

        # Act
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Assert

    @record
    def test_send_topic_message_batch(self):
        # https://docs.microsoft.com/rest/api/servicebus/send-message-batch

        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg_1 = Message(b'This is the first message',
                             broker_properties={'Label': 'M1',
                                                'TimeToLiveTimeSpan': '0.00:00:40'}
                             )
        sent_msg_2 = Message(b'This is the second message',
                             broker_properties={'Label': 'M2'},
                             custom_properties={'Priority': 'Low'}
                             )
        sent_msg_3 = Message(b'This is the third message',
                             broker_properties={'Label': 'M3'},
                             custom_properties={'Priority': 'Medium',
                                                'Customer': 'ABC'}
                             )

        # Act
        self.sbs.send_topic_message_batch(self.topic_name, [sent_msg_1, sent_msg_2, sent_msg_3])
        received_msg_1 = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)
        received_msg_2 = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)
        received_msg_3 = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)

        # Assert
        self.assertEqual(sent_msg_1.body, received_msg_1.body)
        self.assertEqual(sent_msg_2.body, received_msg_2.body)
        self.assertEqual(sent_msg_3.body, received_msg_3.body)

    @record
    def test_receive_subscription_message_read_delete_mode(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_receive_subscription_message_read_delete_mode_throws_on_delete(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)
        with self.assertRaises(AzureServiceBusPeekLockError):
            received_msg.delete()

        # Assert

    @record
    def test_receive_subscription_message_read_delete_mode_throws_on_unlock(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)
        with self.assertRaises(AzureServiceBusPeekLockError):
            received_msg.renew_lock()
        with self.assertRaises(AzureServiceBusPeekLockError):
            received_msg.unlock()

        # Assert

    @record
    def test_receive_subscription_message_peek_lock_mode(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', True, 5)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_get_dead_letter_subscription(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        dead_letter_name = ServiceBusService.format_dead_letter_subscription_name(
            'MySubscription')
        try:
            self.sbs.receive_subscription_message(
                self.topic_name, dead_letter_name, timeout=2)
        except Exception:
            # Assert
            self.fail("Dead Letter subscription not found")

    @record
    def test_receive_subscription_message_delete(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', True, 5)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_receive_subscription_message_delete_with_slash(self):
        # Arrange
        self.topic_name = self.get_resource_name('ut/topic')
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', True, 5)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_receive_subscription_message_unlock(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(b'subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', True)
        received_msg.renew_lock()
        received_msg.unlock()

        # Assert
        received_again_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', True)
        received_again_msg.delete()
        self.assertIsNotNone(received_msg)
        self.assertIsNotNone(received_again_msg)
        self.assertEqual(sent_msg.body, received_msg.body)
        self.assertEqual(received_again_msg.body, received_msg.body)

    @record
    def test_with_filter(self):
         # Single filter
        called = []

        def my_filter(request, next):
            called.append(True)
            return next(request)

        sbs = self.sbs.with_filter(my_filter)
        sbs.create_topic(self.topic_name + '0', None, True)

        self.assertTrue(called)

        del called[:]

        sbs.delete_topic(self.topic_name + '0')

        self.assertTrue(called)
        del called[:]

        # Chained filters
        def filter_a(request, next):
            called.append('a')
            return next(request)

        def filter_b(request, next):
            called.append('b')
            return next(request)

        sbs = self.sbs.with_filter(filter_a).with_filter(filter_b)
        sbs.create_topic(self.topic_name + '0', None, True)

        self.assertEqual(called, ['b', 'a'])

        sbs.delete_topic(self.topic_name + '0')

        self.assertEqual(called, ['b', 'a', 'b', 'a'])

    @unittest.skip('requires extra setup')
    def test_two_identities(self):
        # In order to run this test, 2 service bus service identities are
        # created using the sbaztool available at:
        # http://code.msdn.microsoft.com/windowsazure/Authorization-SBAzTool-6fd76d93
        #
        # Use the following commands to create 2 identities and grant access
        # rights.
        # Replace <servicebusnamespace> with the namespace specified in the
        # test .json file
        # Replace <servicebuskey> with the key specified in the test .json file
        # This only needs to be executed once, after the service bus namespace
        # is created.
        #
        # sbaztool makeid user1 NoHEoD6snlvlhZm7yek9Etxca3l0CYjfc19ICIJZoUg= -n <servicebusnamespace> -k <servicebuskey>
        # sbaztool grant Send /path1 user1 -n <servicebusnamespace> -k <servicebuskey>
        # sbaztool grant Listen /path1 user1 -n <servicebusnamespace> -k <servicebuskey>
        # sbaztool grant Manage /path1 user1 -n <servicebusnamespace> -k
        # <servicebuskey>

        # sbaztool makeid user2 Tb6K5qEgstyRBwp86JEjUezKj/a+fnkLFnibfgvxvdg= -n <servicebusnamespace> -k <servicebuskey>
        # sbaztool grant Send /path2 user2 -n <servicebusnamespace> -k <servicebuskey>
        # sbaztool grant Listen /path2 user2 -n <servicebusnamespace> -k <servicebuskey>
        # sbaztool grant Manage /path2 user2 -n <servicebusnamespace> -k
        # <servicebuskey>

        sbs1 = ServiceBusService(self.settings.SERVICEBUS_NAME,
                                 'NoHEoD6snlvlhZm7yek9Etxca3l0CYjfc19ICIJZoUg=',
                                 'user1')
        sbs2 = ServiceBusService(self.settings.SERVICEBUS_NAME,
                                 'Tb6K5qEgstyRBwp86JEjUezKj/a+fnkLFnibfgvxvdg=',
                                 'user2')

        queue1_name = 'path1/queue' + str(random.randint(1, 10000000))
        queue2_name = 'path2/queue' + str(random.randint(1, 10000000))

        try:
            # Create queues, success
            sbs1.create_queue(queue1_name)
            sbs2.create_queue(queue2_name)

            # Receive messages, success
            msg = sbs1.receive_queue_message(queue1_name, True, 1)
            self.assertIsNone(msg.body)
            msg = sbs1.receive_queue_message(queue1_name, True, 1)
            self.assertIsNone(msg.body)
            msg = sbs2.receive_queue_message(queue2_name, True, 1)
            self.assertIsNone(msg.body)
            msg = sbs2.receive_queue_message(queue2_name, True, 1)
            self.assertIsNone(msg.body)

            # Receive messages, failure
            with self.assertRaises(AzureHttpError):
                msg = sbs1.receive_queue_message(queue2_name, True, 1)
            with self.assertRaises(AzureHttpError):
                msg = sbs2.receive_queue_message(queue1_name, True, 1)
        finally:
            try:
                sbs1.delete_queue(queue1_name)
            except:
                pass
            try:
                sbs2.delete_queue(queue2_name)
            except:
                pass

    @record
    def test_unicode_create_queue_unicode_name(self):
        # Arrange
        self.queue_name = self.queue_name + u'啊齄丂狛狜'

        # Act
        with self.assertRaises(AzureHttpError):
            created = self.sbs.create_queue(self.queue_name)

        # Assert

    @record
    def test_send_queue_message_unicode(self):
        '''Test for auto-encoding of unicode text'''

        # Arrange
        data = u'receive message啊齄丂狛狜'
        sent_msg = Message(data)
        self._create_queue(self.queue_name)

        # Act
        self.sbs.send_queue_message(self.queue_name, sent_msg)

        # Assert
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)
        self.assertIsNotNone(received_msg)
        self.assertEqual(received_msg.body, data.encode('utf-8'))

    @record
    def test_unicode_receive_queue_message_unicode_data(self):
        # Assert
        sent_msg = Message(u'receive message啊齄丂狛狜'.encode('utf-8'))
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_unicode_receive_queue_message_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)
        sent_msg = Message(binary_data)
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_unicode_create_subscription_unicode_name(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        with self.assertRaises(AzureHttpError):
            created = self.sbs.create_subscription(
                self.topic_name, u'MySubscription啊齄丂狛狜')

        # Assert

    @record
    def test_unicode_create_rule_unicode_name(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        with self.assertRaises(AzureHttpError):
            created = self.sbs.create_rule(
                self.topic_name, 'MySubscription', 'MyRule啊齄丂狛狜')

        # Assert

    @record
    def test_send_topic_message_unicode(self):
        '''Test for auto-encoding of unicode text.'''
        # Arrange
        data = u'receive message啊齄丂狛狜'
        sent_msg = Message(data)
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Assert
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)
        self.assertIsNotNone(received_msg)
        self.assertEqual(received_msg.body, data.encode('utf-8'))

    @record
    def test_unicode_receive_subscription_message_unicode_data(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(u'subscription message啊齄丂狛狜'.encode('utf-8'))
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

    @record
    def test_unicode_receive_subscription_message_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message(binary_data)
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_subscription_message(
            self.topic_name, 'MySubscription', False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEqual(sent_msg.body, received_msg.body)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

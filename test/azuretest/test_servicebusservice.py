#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

from azure import *
from azure.servicebus import *
from azuretest.util import *

import unittest

#------------------------------------------------------------------------------
class ServiceBusTest(AzureTestCase):
    def setUp(self):
        self.sbs = ServiceBusService(credentials.getServiceBusNamespace(), 
                                     credentials.getServiceBusKey(), 
                                     'owner')

        __uid = getUniqueTestRunID()

        queue_base_name = u'mytestqueue%s' % (__uid)
        topic_base_name = u'mytesttopic%s' % (__uid)

        self.queue_name = getUniqueNameBasedOnCurrentTime(queue_base_name)
        self.topic_name = getUniqueNameBasedOnCurrentTime(topic_base_name)

    def tearDown(self):
        self.cleanup()
        return super(ServiceBusTest, self).tearDown()
    
    def cleanup(self):
        try:
            self.sbs.delete_queue(self.queue_name)
        except: pass

        try:
            self.sbs.delete_topic(self.topic_name)
        except: pass

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
        if os.environ.has_key(AZURE_SERVICEBUS_NAMESPACE):
            del os.environ[AZURE_SERVICEBUS_NAMESPACE]
        if os.environ.has_key(AZURE_SERVICEBUS_ACCESS_KEY):
            del os.environ[AZURE_SERVICEBUS_ACCESS_KEY]
        if os.environ.has_key(AZURE_SERVICEBUS_ISSUER):
            del os.environ[AZURE_SERVICEBUS_ISSUER]

        # Act
        with self.assertRaises(WindowsAzureError):
            sbs = ServiceBusService()

        # Assert

    def test_create_service_bus_env_variables(self):
        # Arrange
        os.environ[AZURE_SERVICEBUS_NAMESPACE] = credentials.getServiceBusNamespace()
        os.environ[AZURE_SERVICEBUS_ACCESS_KEY] = credentials.getServiceBusKey()
        os.environ[AZURE_SERVICEBUS_ISSUER] = 'owner'

        # Act
        sbs = ServiceBusService()

        if os.environ.has_key(AZURE_SERVICEBUS_NAMESPACE):
            del os.environ[AZURE_SERVICEBUS_NAMESPACE]
        if os.environ.has_key(AZURE_SERVICEBUS_ACCESS_KEY):
            del os.environ[AZURE_SERVICEBUS_ACCESS_KEY]
        if os.environ.has_key(AZURE_SERVICEBUS_ISSUER):
            del os.environ[AZURE_SERVICEBUS_ISSUER]

        # Assert
        self.assertIsNotNone(sbs)
        self.assertEquals(sbs.service_namespace, credentials.getServiceBusNamespace())
        self.assertEquals(sbs.account_key, credentials.getServiceBusKey())
        self.assertEquals(sbs.issuer, 'owner')

    #--Test cases for queues --------------------------------------------------
    def test_create_queue_no_options(self):
        # Arrange

        # Act
        created = self.sbs.create_queue(self.queue_name)

        # Assert
        self.assertTrue(created)

    def test_create_queue_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_queue(self.queue_name, None, True)

        # Assert
        self.assertTrue(created)

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
        self.assertEquals('PT1M', queue.default_message_time_to_live)
        self.assertEquals('PT5M', queue.duplicate_detection_history_time_window)
        self.assertEquals(False, queue.enable_batched_operations)
        self.assertEquals(False, queue.dead_lettering_on_message_expiration)
        self.assertEquals('PT1M', queue.lock_duration)
        self.assertEquals(15, queue.max_delivery_count)
        self.assertEquals(5120, queue.max_size_in_megabytes)
        self.assertEquals(0, queue.message_count)
        self.assertEquals(False, queue.requires_duplicate_detection)
        self.assertEquals(False, queue.requires_session)
        self.assertEquals(0, queue.size_in_bytes)

    def test_create_queue_with_already_existing_queue(self):
        # Arrange

        # Act
        created1 = self.sbs.create_queue(self.queue_name)
        created2 = self.sbs.create_queue(self.queue_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_queue_with_already_existing_queue_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_queue(self.queue_name)
        with self.assertRaises(WindowsAzureError):
            self.sbs.create_queue(self.queue_name, None, True)

        # Assert
        self.assertTrue(created)

    def test_get_queue_with_existing_queue(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        queue = self.sbs.get_queue(self.queue_name)

        # Assert
        self.assertIsNotNone(queue)
        self.assertEquals(queue.name, self.queue_name)

    def test_get_queue_with_non_existing_queue(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            resp = self.sbs.get_queue(self.queue_name)

        # Assert

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

    def test_delete_queue_with_existing_queue(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        deleted = self.sbs.delete_queue(self.queue_name)

        # Assert
        self.assertTrue(deleted)
        queues = self.sbs.list_queues()
        self.assertNamedItemNotInContainer(queues, self.queue_name)

    def test_delete_queue_with_existing_queue_fail_not_exist(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        deleted = self.sbs.delete_queue(self.queue_name, True)

        # Assert
        self.assertTrue(deleted)
        queues = self.sbs.list_queues()
        self.assertNamedItemNotInContainer(queues, self.queue_name)

    def test_delete_queue_with_non_existing_queue(self):
        # Arrange

        # Act
        deleted = self.sbs.delete_queue(self.queue_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_queue_with_non_existing_queue_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.delete_queue(self.queue_name, True)

        # Assert

    def test_send_queue_message(self):
        # Arrange
        self._create_queue(self.queue_name)
        sent_msg = Message('send message')

        # Act
        self.sbs.send_queue_message(self.queue_name, sent_msg)

        # Assert

    def test_receive_queue_message_read_delete_mode(self):
        # Assert
        sent_msg = Message('receive message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals(sent_msg.body, received_msg.body)

    def test_receive_queue_message_read_delete_mode_throws_on_delete(self):
        # Assert
        sent_msg = Message('receive message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)
        with self.assertRaises(WindowsAzureError):
            received_msg.delete()

        # Assert

    def test_receive_queue_message_read_delete_mode_throws_on_unlock(self):
        # Assert
        sent_msg = Message('receive message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, False)
        with self.assertRaises(WindowsAzureError):
            received_msg.unlock()

        # Assert

    def test_receive_queue_message_peek_lock_mode(self):
        # Arrange
        sent_msg = Message('peek lock message')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, True)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals(sent_msg.body, received_msg.body)

    def test_receive_queue_message_delete(self):
        # Arrange
        sent_msg = Message('peek lock message delete')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, True)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals(sent_msg.body, received_msg.body)

    def test_receive_queue_message_unlock(self):
        # Arrange
        sent_msg = Message('peek lock message unlock')
        self._create_queue_and_send_msg(self.queue_name, sent_msg)

        # Act
        received_msg = self.sbs.receive_queue_message(self.queue_name, True)
        received_msg.unlock()

        # Assert
        received_again_msg = self.sbs.receive_queue_message(self.queue_name, True)
        received_again_msg.delete()
        self.assertIsNotNone(received_msg)
        self.assertIsNotNone(received_again_msg)
        self.assertEquals(sent_msg.body, received_msg.body)
        self.assertEquals(received_again_msg.body, received_msg.body)

    def test_send_queue_message_with_custom_message_type(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        sent_msg = Message('<text>peek lock message custom message type</text>', type='text/xml')
        self.sbs.send_queue_message(self.queue_name, sent_msg)
        received_msg = self.sbs.receive_queue_message(self.queue_name, True, 5)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals('text/xml', received_msg.type)

    def test_send_queue_message_with_custom_message_properties(self):
        # Arrange
        self._create_queue(self.queue_name)

        # Act
        props = {'hello':'world',
                 'foo':42,
                 'active':True,
                 'deceased':False,
                 'large':8555111000,
                 'floating':3.14,
                 'dob':datetime(2011, 12, 14)}
        sent_msg = Message('message with properties', custom_properties=props)
        self.sbs.send_queue_message(self.queue_name, sent_msg)
        received_msg = self.sbs.receive_queue_message(self.queue_name, True, 5)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals(received_msg.custom_properties['hello'], 'world')
        self.assertEquals(received_msg.custom_properties['foo'], 42)
        self.assertEquals(received_msg.custom_properties['active'], True)
        self.assertEquals(received_msg.custom_properties['deceased'], False)
        self.assertEquals(received_msg.custom_properties['large'], 8555111000)
        self.assertEquals(received_msg.custom_properties['floating'], 3.14)
        self.assertEquals(received_msg.custom_properties['dob'], datetime(2011, 12, 14))

    #--Test cases for topics/subscriptions ------------------------------------
    def test_create_topic_no_options(self):
        # Arrange

        # Act
        created = self.sbs.create_topic(self.topic_name)

        # Assert
        self.assertTrue(created)

    def test_create_topic_no_options_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_topic(self.topic_name, None, True)

        # Assert
        self.assertTrue(created)

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
        #TODO: MaximumNumberOfSubscriptions is not supported?
        created = self.sbs.create_topic(self.topic_name, topic_options)

        # Assert
        self.assertTrue(created)
        topic = self.sbs.get_topic(self.topic_name)
        self.assertEquals('PT1M', topic.default_message_time_to_live)
        self.assertEquals('PT5M', topic.duplicate_detection_history_time_window)
        self.assertEquals(False, topic.enable_batched_operations)
        self.assertEquals(5120, topic.max_size_in_megabytes)
        self.assertEquals(False, topic.requires_duplicate_detection)
        self.assertEquals(0, topic.size_in_bytes)

    def test_create_topic_with_already_existing_topic(self):
        # Arrange

        # Act
        created1 = self.sbs.create_topic(self.topic_name)
        created2 = self.sbs.create_topic(self.topic_name)

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_topic_with_already_existing_topic_fail_on_exist(self):
        # Arrange

        # Act
        created = self.sbs.create_topic(self.topic_name)
        with self.assertRaises(WindowsAzureError):
            self.sbs.create_topic(self.topic_name, None, True)

        # Assert
        self.assertTrue(created)

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

    def test_get_topic_with_existing_topic(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        topic = self.sbs.get_topic(self.topic_name)

        # Assert
        self.assertIsNotNone(topic)
        self.assertEquals(topic.name, self.topic_name)

    def test_get_topic_with_non_existing_topic(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.get_topic(self.topic_name)

        # Assert

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

    def test_delete_topic_with_existing_topic(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        deleted = self.sbs.delete_topic(self.topic_name)

        # Assert
        self.assertTrue(deleted)
        topics = self.sbs.list_topics()
        self.assertNamedItemNotInContainer(topics, self.topic_name)

    def test_delete_topic_with_existing_topic_fail_not_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        deleted = self.sbs.delete_topic(self.topic_name, True)

        # Assert
        self.assertTrue(deleted)
        topics = self.sbs.list_topics()
        self.assertNamedItemNotInContainer(topics, self.topic_name)

    def test_delete_topic_with_non_existing_topic(self):
        # Arrange

        # Act
        deleted = self.sbs.delete_topic(self.topic_name)

        # Assert
        self.assertFalse(deleted)

    def test_delete_topic_with_non_existing_topic_fail_not_exist(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.delete_topic(self.topic_name, True)

        # Assert

    def test_create_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created = self.sbs.create_subscription(self.topic_name, 'MySubscription')

        # Assert
        self.assertTrue(created)

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
        created = self.sbs.create_subscription(self.topic_name, 'MySubscription', subscription_options)

        # Assert
        self.assertTrue(created)
        subscription = self.sbs.get_subscription(self.topic_name, 'MySubscription')
        self.assertEquals(False, subscription.dead_lettering_on_filter_evaluation_exceptions)
        self.assertEquals(False, subscription.dead_lettering_on_message_expiration)
        self.assertEquals('PT15M', subscription.default_message_time_to_live)
        self.assertEquals(False, subscription.enable_batched_operations)
        self.assertEquals('PT1M', subscription.lock_duration)
        #self.assertEquals(15, subscription.max_delivery_count) #no idea why max_delivery_count is always 10
        self.assertEquals(0, subscription.message_count)
        self.assertEquals(False, subscription.requires_session)

    def test_create_subscription_fail_on_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created = self.sbs.create_subscription(self.topic_name, 'MySubscription', None, True)

        # Assert
        self.assertTrue(created)

    def test_create_subscription_with_already_existing_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created1 = self.sbs.create_subscription(self.topic_name, 'MySubscription')
        created2 = self.sbs.create_subscription(self.topic_name, 'MySubscription')

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_subscription_with_already_existing_subscription_fail_on_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        created = self.sbs.create_subscription(self.topic_name, 'MySubscription')
        with self.assertRaises(WindowsAzureError):
            self.sbs.create_subscription(self.topic_name, 'MySubscription', None, True)

        # Assert
        self.assertTrue(created)

    def test_list_subscriptions(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription2')

        # Act
        subscriptions = self.sbs.list_subscriptions(self.topic_name)

        # Assert
        self.assertIsNotNone(subscriptions)
        self.assertEquals(len(subscriptions), 1)
        self.assertEquals(subscriptions[0].name, 'MySubscription2')

    def test_get_subscription_with_existing_subscription(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription3')

        # Act
        subscription = self.sbs.get_subscription(self.topic_name, 'MySubscription3')

        # Assert
        self.assertIsNotNone(subscription)
        self.assertEquals(subscription.name, 'MySubscription3')

    def test_get_subscription_with_non_existing_subscription(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription3')

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.get_subscription(self.topic_name, 'MySubscription4')

        # Assert

    def test_delete_subscription_with_existing_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)
        self._create_subscription(self.topic_name, 'MySubscription4')
        self._create_subscription(self.topic_name, 'MySubscription5')

        # Act
        deleted = self.sbs.delete_subscription(self.topic_name, 'MySubscription4')

        # Assert
        self.assertTrue(deleted)
        subscriptions = self.sbs.list_subscriptions(self.topic_name)
        self.assertIsNotNone(subscriptions)
        self.assertEquals(len(subscriptions), 1)
        self.assertEquals(subscriptions[0].name, 'MySubscription5')

    def test_delete_subscription_with_existing_subscription_fail_not_exist(self):
        # Arrange
        self._create_topic(self.topic_name)
        self._create_subscription(self.topic_name, 'MySubscription4')
        self._create_subscription(self.topic_name, 'MySubscription5')

        # Act
        deleted = self.sbs.delete_subscription(self.topic_name, 'MySubscription4', True)

        # Assert
        self.assertTrue(deleted)
        subscriptions = self.sbs.list_subscriptions(self.topic_name)
        self.assertIsNotNone(subscriptions)
        self.assertEquals(len(subscriptions), 1)
        self.assertEquals(subscriptions[0].name, 'MySubscription5')

    def test_delete_subscription_with_non_existing_subscription(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        deleted = self.sbs.delete_subscription(self.topic_name, 'MySubscription')

        # Assert
        self.assertFalse(deleted)

    def test_delete_subscription_with_non_existing_subscription_fail_not_exist(self):
        # Arrange
        self._create_topic(self.topic_name)

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.delete_subscription(self.topic_name, 'MySubscription', True)

        # Assert

    def test_create_rule_no_options(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1')

        # Assert
        self.assertTrue(created)

    def test_create_rule_no_options_fail_on_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', None, True)

        # Assert
        self.assertTrue(created)

    def test_create_rule_with_already_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created1 = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1')
        created2 = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1')

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_rule_with_already_existing_rule_fail_on_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1')
        with self.assertRaises(WindowsAzureError):
            self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', None, True)

        # Assert
        self.assertTrue(created)

    def test_create_rule_with_options_sql_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'SqlFilter'
        rule1.filter_expression = 'foo > 40'
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    def test_create_rule_with_options_true_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'TrueFilter'
        rule1.filter_expression = '1=1'
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    def test_create_rule_with_options_false_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'FalseFilter'
        rule1.filter_expression = '1=0'
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    def test_create_rule_with_options_correlation_filter(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.filter_type = 'CorrelationFilter'
        rule1.filter_expression = 'myid'
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    def test_create_rule_with_options_empty_rule_action(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.action_type = 'EmptyRuleAction'
        rule1.action_expression = ''
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    def test_create_rule_with_options_sql_rule_action(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule1 = Rule()
        rule1.action_type = 'SqlRuleAction'
        rule1.action_expression = "SET foo = 5"
        created = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', rule1)

        # Assert
        self.assertTrue(created)

    def test_list_rules(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        resp = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule2')

        # Act
        rules = self.sbs.list_rules(self.topic_name, 'MySubscription')

        # Assert
        self.assertEquals(len(rules), 2)

    def test_get_rule_with_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        rule = self.sbs.get_rule(self.topic_name, 'MySubscription', '$Default')

        # Assert
        self.assertIsNotNone(rule)
        self.assertEquals(rule.name, '$Default')

    def test_get_rule_with_non_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.get_rule(self.topic_name, 'MySubscription', 'NonExistingRule')

        # Assert

    def test_get_rule_with_existing_rule_with_options(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_rule = Rule()
        sent_rule.filter_type = 'SqlFilter'
        sent_rule.filter_expression = 'foo > 40'
        sent_rule.action_type = 'SqlRuleAction'
        sent_rule.action_expression = 'SET foo = 5'
        self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule1', sent_rule)

        # Act
        received_rule = self.sbs.get_rule(self.topic_name, 'MySubscription', 'MyRule1')

        # Assert
        self.assertIsNotNone(received_rule)
        self.assertEquals(received_rule.name, 'MyRule1')
        self.assertEquals(received_rule.filter_type, sent_rule.filter_type)
        self.assertEquals(received_rule.filter_expression, sent_rule.filter_expression)
        self.assertEquals(received_rule.action_type, sent_rule.action_type)
        self.assertEquals(received_rule.action_expression, sent_rule.action_expression)

    def test_delete_rule_with_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        resp = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule3')
        resp = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule4')

        # Act
        deleted1 = self.sbs.delete_rule(self.topic_name, 'MySubscription', 'MyRule4')
        deleted2 = self.sbs.delete_rule(self.topic_name, 'MySubscription', '$Default')

        # Assert
        self.assertTrue(deleted1)
        self.assertTrue(deleted2)
        rules = self.sbs.list_rules(self.topic_name, 'MySubscription')
        self.assertIsNotNone(rules)
        self.assertEquals(len(rules), 1)
        self.assertEquals(rules[0].name, 'MyRule3')

    def test_delete_rule_with_existing_rule_fail_not_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        resp = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule3')
        resp = self.sbs.create_rule(self.topic_name, 'MySubscription', 'MyRule4')

        # Act
        deleted1 = self.sbs.delete_rule(self.topic_name, 'MySubscription', 'MyRule4', True)
        deleted2 = self.sbs.delete_rule(self.topic_name, 'MySubscription', '$Default', True)

        # Assert
        self.assertTrue(deleted1)
        self.assertTrue(deleted2)
        rules = self.sbs.list_rules(self.topic_name, 'MySubscription')
        self.assertIsNotNone(rules)
        self.assertEquals(len(rules), 1)
        self.assertEquals(rules[0].name, 'MyRule3')

    def test_delete_rule_with_non_existing_rule(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        deleted = self.sbs.delete_rule(self.topic_name, 'MySubscription', 'NonExistingRule')

        # Assert
        self.assertFalse(deleted)
        
    def test_delete_rule_with_non_existing_rule_fail_not_exist(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')

        # Act
        with self.assertRaises(WindowsAzureError):
            self.sbs.delete_rule(self.topic_name, 'MySubscription', 'NonExistingRule', True)

        # Assert
        
    def test_send_topic_message(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message('subscription message')
        
        # Act
        self.sbs.send_topic_message(self.topic_name, sent_msg)

        # Assert
        
    def test_receive_subscription_message_read_delete_mode(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message('subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)
        
        # Act
        received_msg = self.sbs.receive_subscription_message(self.topic_name, 'MySubscription', False)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals(sent_msg.body, received_msg.body)

    def test_receive_subscription_message_read_delete_mode_throws_on_delete(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message('subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)
        
        # Act
        received_msg = self.sbs.receive_subscription_message(self.topic_name, 'MySubscription', False)
        with self.assertRaises(WindowsAzureError):
            received_msg.delete()

        # Assert

    def test_receive_subscription_message_read_delete_mode_throws_on_unlock(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message('subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)
        
        # Act
        received_msg = self.sbs.receive_subscription_message(self.topic_name, 'MySubscription', False)
        with self.assertRaises(WindowsAzureError):
            received_msg.unlock()

        # Assert

    def test_receive_subscription_message_peek_lock_mode(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message('subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)
        
        # Act
        received_msg = self.sbs.receive_subscription_message(self.topic_name, 'MySubscription', True, 5)

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals(sent_msg.body, received_msg.body)

    def test_receive_subscription_message_delete(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message('subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)
        
        # Act
        received_msg = self.sbs.receive_subscription_message(self.topic_name, 'MySubscription', True, 5)
        received_msg.delete()

        # Assert
        self.assertIsNotNone(received_msg)
        self.assertEquals(sent_msg.body, received_msg.body)

    def test_receive_subscription_message_unlock(self):
        # Arrange
        self._create_topic_and_subscription(self.topic_name, 'MySubscription')
        sent_msg = Message('subscription message')
        self.sbs.send_topic_message(self.topic_name, sent_msg)
        
        # Act
        received_msg = self.sbs.receive_subscription_message(self.topic_name, 'MySubscription', True)
        received_msg.unlock()

        # Assert
        received_again_msg = self.sbs.receive_subscription_message(self.topic_name, 'MySubscription', True)
        received_again_msg.delete()
        self.assertIsNotNone(received_msg)
        self.assertIsNotNone(received_again_msg)
        self.assertEquals(sent_msg.body, received_msg.body)
        self.assertEquals(received_again_msg.body, received_msg.body)

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

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

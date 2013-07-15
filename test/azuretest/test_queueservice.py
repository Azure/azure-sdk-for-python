﻿#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
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
import unittest

from azure import WindowsAzureError
from azure.storage.queueservice import QueueService
from azuretest.util import (AzureTestCase,
                            credentials,
                            getUniqueTestRunID,
                            getUniqueNameBasedOnCurrentTime,
                            )

#------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'mytestqueue'
#------------------------------------------------------------------------------
class QueueServiceTest(AzureTestCase):

    def setUp(self):
        self.queue_client = QueueService(account_name=credentials.getStorageServicesName(), 
                                                account_key=credentials.getStorageServicesKey())

        proxy_host = credentials.getProxyHost()
        proxy_port = credentials.getProxyPort()
        if proxy_host:
            self.queue_client.set_proxy(proxy_host, proxy_port)

        __uid = getUniqueTestRunID()

        queue_base_name = u'%s' % (__uid)
        self.test_queues = []
        self.creatable_queues = []
        for i in range(10):
            self.test_queues.append(TEST_QUEUE_PREFIX + str(i) + getUniqueNameBasedOnCurrentTime(queue_base_name))
        for i in range(4):
            self.creatable_queues.append('mycreatablequeue' + str(i) + getUniqueNameBasedOnCurrentTime(queue_base_name))
        for queue_name in self.test_queues:
            self.queue_client.create_queue(queue_name)

    def tearDown(self):
        self.cleanup()
        return super(QueueServiceTest, self).tearDown()
    
    def cleanup(self):
        for queue_name in self.test_queues:
            try:
                self.queue_client.delete_queue(queue_name)
            except:
                pass
        for queue_name in self.creatable_queues:
            try:
                self.queue_client.delete_queue(queue_name)
            except:
                pass

    def test_get_service_properties(self):
        #This api doesn't apply to local storage
        if self.queue_client.use_local_storage:
            return

        #Action
        properties = self.queue_client.get_queue_service_properties()

        #Asserts
        self.assertIsNotNone(properties)
        self.assertIsNotNone(properties.logging)
        self.assertIsNotNone(properties.logging.retention_policy)
        self.assertIsNotNone(properties.logging.version)
        self.assertIsNotNone(properties.metrics)
        self.assertIsNotNone(properties.metrics.retention_policy)
        self.assertIsNotNone(properties.metrics.version)

    def test_set_service_properties(self):
        #This api doesn't apply to local storage
        if self.queue_client.use_local_storage:
            return

        #Action
        queue_properties = self.queue_client.get_queue_service_properties()
        queue_properties.logging.read=True
        self.queue_client.set_queue_service_properties(queue_properties)
        properties = self.queue_client.get_queue_service_properties()

        #Asserts
        self.assertIsNotNone(properties)
        self.assertIsNotNone(properties.logging)
        self.assertIsNotNone(properties.logging.retention_policy)
        self.assertIsNotNone(properties.logging.version)
        self.assertIsNotNone(properties.metrics)
        self.assertIsNotNone(properties.metrics.retention_policy)
        self.assertIsNotNone(properties.metrics.version)
        self.assertTrue(properties.logging.read)

    def test_create_queue(self):
        #Action
        self.queue_client.create_queue(self.creatable_queues[0])
        result = self.queue_client.get_queue_metadata(self.creatable_queues[0])
        self.queue_client.delete_queue(self.creatable_queues[0])

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(result['x-ms-approximate-messages-count'], '0')

    def test_create_queue_already_exist(self):
        #Action
        created1 = self.queue_client.create_queue(self.creatable_queues[0])
        created2 = self.queue_client.create_queue(self.creatable_queues[0])

        #Asserts
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_queue_fail_on_exist(self):
        #Action
        created = self.queue_client.create_queue(self.creatable_queues[0], None, True)
        with self.assertRaises(WindowsAzureError):
            self.queue_client.create_queue(self.creatable_queues[0], None, True)

        #Asserts
        self.assertTrue(created)

    def test_create_queue_with_options(self):
        #Action
        self.queue_client.create_queue(self.creatable_queues[1], x_ms_meta_name_values = {'foo':'test', 'bar':'blah'})
        result = self.queue_client.get_queue_metadata(self.creatable_queues[1])

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))
        self.assertEqual(result['x-ms-approximate-messages-count'], '0')
        self.assertEqual('test', result['x-ms-meta-foo'])
        self.assertEqual('blah', result['x-ms-meta-bar'])

    def test_delete_queue_not_exist(self):
        #Action
        deleted = self.queue_client.delete_queue(self.creatable_queues[0])

        #Asserts
        self.assertFalse(deleted)

    def test_delete_queue_fail_not_exist_not_exist(self):
        #Action
        with self.assertRaises(WindowsAzureError):
            self.queue_client.delete_queue(self.creatable_queues[0], True)

        #Asserts

    def test_delete_queue_fail_not_exist_already_exist(self):
        #Action
        created = self.queue_client.create_queue(self.creatable_queues[0])
        deleted = self.queue_client.delete_queue(self.creatable_queues[0], True)

        #Asserts
        self.assertTrue(created)
        self.assertTrue(deleted)

    def test_list_queues(self):
        #Action
        queues = self.queue_client.list_queues()
        for queue in queues:
            pass

        #Asserts
        self.assertIsNotNone(queues)
        self.assertEqual('', queues.marker)
        self.assertEqual(0, queues.max_results)
        self.assertTrue(len(self.test_queues) <= len(queues))

    def test_list_queues_with_options(self):
        #Action
        queues_1 = self.queue_client.list_queues(prefix=TEST_QUEUE_PREFIX, maxresults=3)
        queues_2 = self.queue_client.list_queues(prefix=TEST_QUEUE_PREFIX, marker=queues_1.next_marker, include='metadata')

        #Asserts
        self.assertIsNotNone(queues_1)
        self.assertEqual(3, len(queues_1))
        self.assertEqual(3, queues_1.max_results)
        self.assertEqual('', queues_1.marker)
        self.assertIsNotNone(queues_1[0])
        self.assertIsNone(queues_1[0].metadata)
        self.assertNotEqual('', queues_1[0].name)
        self.assertNotEqual('', queues_1[0].url) 
        #Asserts
        self.assertIsNotNone(queues_2)
        self.assertTrue(len(self.test_queues) -3 <= len(queues_2))
        self.assertEqual(0, queues_2.max_results)
        self.assertEqual(queues_1.next_marker, queues_2.marker)
        self.assertIsNotNone(queues_2[0])
        self.assertIsNotNone(queues_2[0].metadata)
        self.assertNotEqual('', queues_2[0].name)
        self.assertNotEqual('', queues_2[0].url) 

    def test_set_queue_metadata(self):
        #Action
        self.queue_client.create_queue(self.creatable_queues[2])
        self.queue_client.set_queue_metadata(self.creatable_queues[2], x_ms_meta_name_values={'foo':'test', 'bar':'blah'})
        result = self.queue_client.get_queue_metadata(self.creatable_queues[2])
        self.queue_client.delete_queue(self.creatable_queues[2])

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))
        self.assertEqual('0', result['x-ms-approximate-messages-count'])
        self.assertEqual('test', result['x-ms-meta-foo'])
        self.assertEqual('blah', result['x-ms-meta-bar'])

    def test_put_message(self):
        #Action.  No exception means pass. No asserts needed.
        self.queue_client.put_message(self.test_queues[0], 'message1')
        self.queue_client.put_message(self.test_queues[0], 'message2')
        self.queue_client.put_message(self.test_queues[0], 'message3')
        self.queue_client.put_message(self.test_queues[0], 'message4')
    
    def test_get_messages(self):
        #Action
        self.queue_client.put_message(self.test_queues[1], 'message1')
        self.queue_client.put_message(self.test_queues[1], 'message2')
        self.queue_client.put_message(self.test_queues[1], 'message3')
        self.queue_client.put_message(self.test_queues[1], 'message4')
        result = self.queue_client.get_messages(self.test_queues[1])

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertEqual('message1', message.message_text)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual('1', message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertNotEqual('', message.time_next_visible)

    def test_get_messages_with_options(self):
        #Action
        self.queue_client.put_message(self.test_queues[2], 'message1')
        self.queue_client.put_message(self.test_queues[2], 'message2')
        self.queue_client.put_message(self.test_queues[2], 'message3')
        self.queue_client.put_message(self.test_queues[2], 'message4')
        result = self.queue_client.get_messages(self.test_queues[2], numofmessages=4, visibilitytimeout=20)

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(4, len(result))

        for message in result:
            self.assertIsNotNone(message)
            self.assertNotEqual('', message.message_id)
            self.assertNotEqual('', message.message_text)
            self.assertNotEqual('', message.pop_receipt)
            self.assertEqual('1', message.dequeue_count)
            self.assertNotEqual('', message.insertion_time)
            self.assertNotEqual('', message.expiration_time)
            self.assertNotEqual('', message.time_next_visible)

    def test_peek_messages(self):
        #Action
        self.queue_client.put_message(self.test_queues[3], 'message1')
        self.queue_client.put_message(self.test_queues[3], 'message2')
        self.queue_client.put_message(self.test_queues[3], 'message3')
        self.queue_client.put_message(self.test_queues[3], 'message4')
        result = self.queue_client.peek_messages(self.test_queues[3])

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertNotEqual('', message.message_text)
        self.assertEqual('', message.pop_receipt)
        self.assertEqual('0', message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertEqual('', message.time_next_visible)

    def test_peek_messages_with_options(self):
        #Action
        self.queue_client.put_message(self.test_queues[4], 'message1')
        self.queue_client.put_message(self.test_queues[4], 'message2')
        self.queue_client.put_message(self.test_queues[4], 'message3')
        self.queue_client.put_message(self.test_queues[4], 'message4')
        result = self.queue_client.peek_messages(self.test_queues[4], numofmessages=4)

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(4, len(result))
        for message in result:
            self.assertIsNotNone(message)
            self.assertNotEqual('', message.message_id)
            self.assertNotEqual('', message.message_text)
            self.assertEqual('', message.pop_receipt)
            self.assertEqual('0', message.dequeue_count)
            self.assertNotEqual('', message.insertion_time)
            self.assertNotEqual('', message.expiration_time)
            self.assertEqual('', message.time_next_visible)

    def test_clear_messages(self):
        #Action
        self.queue_client.put_message(self.test_queues[5], 'message1')
        self.queue_client.put_message(self.test_queues[5], 'message2')
        self.queue_client.put_message(self.test_queues[5], 'message3')
        self.queue_client.put_message(self.test_queues[5], 'message4')
        self.queue_client.clear_messages(self.test_queues[5])
        result = self.queue_client.peek_messages(self.test_queues[5])

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))

    def test_delete_message(self):
        #Action
        self.queue_client.put_message(self.test_queues[6], 'message1')
        self.queue_client.put_message(self.test_queues[6], 'message2')
        self.queue_client.put_message(self.test_queues[6], 'message3')
        self.queue_client.put_message(self.test_queues[6], 'message4')
        result = self.queue_client.get_messages(self.test_queues[6])
        self.queue_client.delete_message(self.test_queues[6], result[0].message_id, result[0].pop_receipt)
        result2 = self.queue_client.get_messages(self.test_queues[6], numofmessages=32)
        
        #Asserts
        self.assertIsNotNone(result2)
        self.assertEqual(3, len(result2))

    def test_update_message(self):
        #Action
        self.queue_client.put_message(self.test_queues[7], 'message1')
        list_result1 = self.queue_client.get_messages(self.test_queues[7])
        self.queue_client.update_message(self.test_queues[7], list_result1[0].message_id, 'new text', list_result1[0].pop_receipt, visibilitytimeout=0)
        list_result2 = self.queue_client.get_messages(self.test_queues[7])

        #Asserts
        self.assertIsNotNone(list_result2)
        message = list_result2[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertEqual('new text', message.message_text)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual('2', message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertNotEqual('', message.time_next_visible)

    def test_with_filter(self):
        # Single filter
        called = []
        def my_filter(request, next):
            called.append(True)
            return next(request)
        qc = self.queue_client.with_filter(my_filter)
        qc.put_message(self.test_queues[7], 'message1')

        self.assertTrue(called)

        del called[:]        
        
        # Chained filters
        def filter_a(request, next):
            called.append('a')
            return next(request)
        
        def filter_b(request, next):
            called.append('b')
            return next(request)

        qc = self.queue_client.with_filter(filter_a).with_filter(filter_b)
        qc.put_message(self.test_queues[7], 'message1')

        self.assertEqual(called, ['b', 'a'])

    def test_unicode_create_queue_unicode_name(self):
        #Action
        self.creatable_queues[0] = u'啊齄丂狛狜'

        with self.assertRaises(WindowsAzureError):
            # not supported - queue name must be alphanumeric, lowercase
            self.queue_client.create_queue(self.creatable_queues[0])

        #Asserts

    def test_unicode_get_messages_unicode_data(self):
        #Action
        self.queue_client.put_message(self.test_queues[1], u'message1㚈')
        result = self.queue_client.get_messages(self.test_queues[1])

        #Asserts
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertEqual(u'message1㚈', message.message_text)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual('1', message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertNotEqual('', message.time_next_visible)

    def test_unicode_update_message_unicode_data(self):
        #Action
        self.queue_client.put_message(self.test_queues[7], 'message1')
        list_result1 = self.queue_client.get_messages(self.test_queues[7])
        self.queue_client.update_message(self.test_queues[7], list_result1[0].message_id, u'啊齄丂狛狜', list_result1[0].pop_receipt, visibilitytimeout=0)
        list_result2 = self.queue_client.get_messages(self.test_queues[7])

        #Asserts
        self.assertIsNotNone(list_result2)
        message = list_result2[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertEqual(u'啊齄丂狛狜', message.message_text)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual('2', message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertNotEqual('', message.time_next_visible)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

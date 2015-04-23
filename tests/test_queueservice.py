# coding: utf-8

#-------------------------------------------------------------------------
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
import datetime
import unittest

from azure import WindowsAzureError
from azure.storage import (
    AccessPolicy,
    SignedIdentifier,
    SignedIdentifiers,
    QueueSharedAccessPermissions,
)
from azure.storage.queueservice import QueueService
from azure.storage.sharedaccesssignature import SharedAccessPolicy
from util import (
    AzureTestCase,
    credentials,
    getUniqueName,
    set_service_options,
)

#------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'mytestqueue'
#------------------------------------------------------------------------------


class QueueServiceTest(AzureTestCase):

    def setUp(self):
        self.qs = QueueService(credentials.getStorageServicesName(),
                               credentials.getStorageServicesKey())
        set_service_options(self.qs)

        self.test_queues = []
        self.creatable_queues = []
        for i in range(10):
            self.test_queues.append(getUniqueName(TEST_QUEUE_PREFIX + str(i)))
        for i in range(4):
            self.creatable_queues.append(
                getUniqueName('mycreatablequeue' + str(i)))
        for queue_name in self.test_queues:
            self.qs.create_queue(queue_name)

    def tearDown(self):
        self.cleanup()
        return super(QueueServiceTest, self).tearDown()

    def cleanup(self):
        for queue_name in self.test_queues:
            try:
                self.qs.delete_queue(queue_name)
            except:
                pass
        for queue_name in self.creatable_queues:
            try:
                self.qs.delete_queue(queue_name)
            except:
                pass

    def _get_shared_access_policy(self, permission):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        start = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        expiry = start + datetime.timedelta(hours=1)
        return SharedAccessPolicy(
            AccessPolicy(
                start.strftime(date_format),
                expiry.strftime(date_format),
                permission
            )
        )

    def test_get_service_properties(self):
        # This api doesn't apply to local storage
        if self.qs.use_local_storage:
            return

        # Action
        properties = self.qs.get_queue_service_properties()

        # Asserts
        self.assertIsNotNone(properties)
        self.assertIsNotNone(properties.logging)
        self.assertIsNotNone(properties.logging.retention_policy)
        self.assertIsNotNone(properties.logging.version)
        self.assertIsNotNone(properties.hour_metrics)
        self.assertIsNotNone(properties.hour_metrics.retention_policy)
        self.assertIsNotNone(properties.hour_metrics.version)
        self.assertIsNotNone(properties.minute_metrics)
        self.assertIsNotNone(properties.minute_metrics.retention_policy)
        self.assertIsNotNone(properties.minute_metrics.version)

    def test_set_service_properties(self):
        # This api doesn't apply to local storage
        if self.qs.use_local_storage:
            return

        # Action
        queue_properties = self.qs.get_queue_service_properties()
        queue_properties.logging.read = True
        self.qs.set_queue_service_properties(queue_properties)
        properties = self.qs.get_queue_service_properties()

        # Asserts
        self.assertIsNotNone(properties)
        self.assertIsNotNone(properties.logging)
        self.assertIsNotNone(properties.logging.retention_policy)
        self.assertIsNotNone(properties.logging.version)
        self.assertIsNotNone(properties.hour_metrics)
        self.assertIsNotNone(properties.hour_metrics.retention_policy)
        self.assertIsNotNone(properties.hour_metrics.version)
        self.assertIsNotNone(properties.minute_metrics)
        self.assertIsNotNone(properties.minute_metrics.retention_policy)
        self.assertIsNotNone(properties.minute_metrics.version)
        self.assertTrue(properties.logging.read)

    def test_create_queue(self):
        # Action
        self.qs.create_queue(self.creatable_queues[0])
        result = self.qs.get_queue_metadata(self.creatable_queues[0])
        self.qs.delete_queue(self.creatable_queues[0])

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(result['x-ms-approximate-messages-count'], '0')

    def test_create_queue_already_exist(self):
        # Action
        created1 = self.qs.create_queue(self.creatable_queues[0])
        created2 = self.qs.create_queue(self.creatable_queues[0])

        # Asserts
        self.assertTrue(created1)
        self.assertFalse(created2)

    def test_create_queue_fail_on_exist(self):
        # Action
        created = self.qs.create_queue(self.creatable_queues[0], None, True)
        with self.assertRaises(WindowsAzureError):
            self.qs.create_queue(self.creatable_queues[0], None, True)

        # Asserts
        self.assertTrue(created)

    def test_create_queue_with_options(self):
        # Action
        self.qs.create_queue(
            self.creatable_queues[1],
            x_ms_meta_name_values={'val1': 'test', 'val2': 'blah'})
        result = self.qs.get_queue_metadata(self.creatable_queues[1])

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))
        self.assertEqual(result['x-ms-approximate-messages-count'], '0')
        self.assertEqual('test', result['x-ms-meta-val1'])
        self.assertEqual('blah', result['x-ms-meta-val2'])

    def test_delete_queue_not_exist(self):
        # Action
        deleted = self.qs.delete_queue(self.creatable_queues[0])

        # Asserts
        self.assertFalse(deleted)

    def test_delete_queue_fail_not_exist_not_exist(self):
        # Action
        with self.assertRaises(WindowsAzureError):
            self.qs.delete_queue(self.creatable_queues[0], True)

        # Asserts

    def test_delete_queue_fail_not_exist_already_exist(self):
        # Action
        created = self.qs.create_queue(self.creatable_queues[0])
        deleted = self.qs.delete_queue(self.creatable_queues[0], True)

        # Asserts
        self.assertTrue(created)
        self.assertTrue(deleted)

    def test_list_queues(self):
        # Action
        queues = self.qs.list_queues()
        for queue in queues:
            pass

        # Asserts
        self.assertIsNotNone(queues)
        self.assertEqual('', queues.marker)
        self.assertEqual(0, queues.max_results)
        self.assertTrue(len(self.test_queues) <= len(queues))

    def test_list_queues_with_options(self):
        # Action
        queues_1 = self.qs.list_queues(prefix=TEST_QUEUE_PREFIX, maxresults=3)
        queues_2 = self.qs.list_queues(
            prefix=TEST_QUEUE_PREFIX,
            marker=queues_1.next_marker,
            include='metadata')

        # Asserts
        self.assertIsNotNone(queues_1)
        self.assertEqual(3, len(queues_1))
        self.assertEqual(3, queues_1.max_results)
        self.assertEqual('', queues_1.marker)
        self.assertIsNotNone(queues_1[0])
        self.assertIsNone(queues_1[0].metadata)
        self.assertNotEqual('', queues_1[0].name)
        # Asserts
        self.assertIsNotNone(queues_2)
        self.assertTrue(len(self.test_queues) - 3 <= len(queues_2))
        self.assertEqual(0, queues_2.max_results)
        self.assertEqual(queues_1.next_marker, queues_2.marker)
        self.assertIsNotNone(queues_2[0])
        self.assertIsNotNone(queues_2[0].metadata)
        self.assertNotEqual('', queues_2[0].name)

    def test_set_queue_metadata(self):
        # Action
        self.qs.create_queue(self.creatable_queues[2])
        self.qs.set_queue_metadata(
            self.creatable_queues[2],
            x_ms_meta_name_values={'val1': 'test', 'val2': 'blah'})
        result = self.qs.get_queue_metadata(self.creatable_queues[2])
        self.qs.delete_queue(self.creatable_queues[2])

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(3, len(result))
        self.assertEqual('0', result['x-ms-approximate-messages-count'])
        self.assertEqual('test', result['x-ms-meta-val1'])
        self.assertEqual('blah', result['x-ms-meta-val2'])

    def test_put_message(self):
        # Action.  No exception means pass. No asserts needed.
        self.qs.put_message(self.test_queues[0], 'message1')
        self.qs.put_message(self.test_queues[0], 'message2')
        self.qs.put_message(self.test_queues[0], 'message3')
        self.qs.put_message(self.test_queues[0], 'message4')

    def test_get_messages(self):
        # Action
        self.qs.put_message(self.test_queues[1], 'message1')
        self.qs.put_message(self.test_queues[1], 'message2')
        self.qs.put_message(self.test_queues[1], 'message3')
        self.qs.put_message(self.test_queues[1], 'message4')
        result = self.qs.get_messages(self.test_queues[1])

        # Asserts
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
        # Action
        self.qs.put_message(self.test_queues[2], 'message1')
        self.qs.put_message(self.test_queues[2], 'message2')
        self.qs.put_message(self.test_queues[2], 'message3')
        self.qs.put_message(self.test_queues[2], 'message4')
        result = self.qs.get_messages(
            self.test_queues[2], numofmessages=4, visibilitytimeout=20)

        # Asserts
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
        # Action
        self.qs.put_message(self.test_queues[3], 'message1')
        self.qs.put_message(self.test_queues[3], 'message2')
        self.qs.put_message(self.test_queues[3], 'message3')
        self.qs.put_message(self.test_queues[3], 'message4')
        result = self.qs.peek_messages(self.test_queues[3])

        # Asserts
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
        # Action
        self.qs.put_message(self.test_queues[4], 'message1')
        self.qs.put_message(self.test_queues[4], 'message2')
        self.qs.put_message(self.test_queues[4], 'message3')
        self.qs.put_message(self.test_queues[4], 'message4')
        result = self.qs.peek_messages(self.test_queues[4], numofmessages=4)

        # Asserts
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
        # Action
        self.qs.put_message(self.test_queues[5], 'message1')
        self.qs.put_message(self.test_queues[5], 'message2')
        self.qs.put_message(self.test_queues[5], 'message3')
        self.qs.put_message(self.test_queues[5], 'message4')
        self.qs.clear_messages(self.test_queues[5])
        result = self.qs.peek_messages(self.test_queues[5])

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))

    def test_delete_message(self):
        # Action
        self.qs.put_message(self.test_queues[6], 'message1')
        self.qs.put_message(self.test_queues[6], 'message2')
        self.qs.put_message(self.test_queues[6], 'message3')
        self.qs.put_message(self.test_queues[6], 'message4')
        result = self.qs.get_messages(self.test_queues[6])
        self.qs.delete_message(
            self.test_queues[6], result[0].message_id, result[0].pop_receipt)
        result2 = self.qs.get_messages(self.test_queues[6], numofmessages=32)

        # Asserts
        self.assertIsNotNone(result2)
        self.assertEqual(3, len(result2))

    def test_update_message(self):
        # Action
        self.qs.put_message(self.test_queues[7], 'message1')
        list_result1 = self.qs.get_messages(self.test_queues[7])
        self.qs.update_message(self.test_queues[7],
                               list_result1[0].message_id,
                               'new text',
                               list_result1[0].pop_receipt,
                               visibilitytimeout=0)
        list_result2 = self.qs.get_messages(self.test_queues[7])

        # Asserts
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

    def test_sas_read(self):
        # Arrange
        self.qs.put_message(self.test_queues[0], 'message1')
        token = self.qs.generate_shared_access_signature(
            self.test_queues[0],
            self._get_shared_access_policy(QueueSharedAccessPermissions.READ),
        )

        # Act
        service = QueueService(credentials.getStorageServicesName(), sas_token=token)
        set_service_options(service)
        result = service.peek_messages(self.test_queues[0])

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertEqual('message1', message.message_text)

    def test_sas_add(self):
        # Arrange
        token = self.qs.generate_shared_access_signature(
            self.test_queues[0],
            self._get_shared_access_policy(QueueSharedAccessPermissions.ADD),
        )

        # Act
        service = QueueService(credentials.getStorageServicesName(), sas_token=token)
        set_service_options(service)
        result = service.put_message(self.test_queues[0], 'addedmessage')

        # Assert
        result = self.qs.get_messages(self.test_queues[0])
        self.assertEqual('addedmessage', result[0].message_text)

    def test_sas_update(self):
        # Arrange
        self.qs.put_message(self.test_queues[0], 'message1')
        token = self.qs.generate_shared_access_signature(
            self.test_queues[0],
            self._get_shared_access_policy(QueueSharedAccessPermissions.UPDATE),
        )
        result = self.qs.get_messages(self.test_queues[0])

        # Act
        service = QueueService(credentials.getStorageServicesName(), sas_token=token)
        set_service_options(service)
        service.update_message(
            self.test_queues[0],
            result[0].message_id,
            'updatedmessage1',
            result[0].pop_receipt,
            visibilitytimeout=0,
        )

        # Assert
        result = self.qs.get_messages(self.test_queues[0])
        self.assertEqual('updatedmessage1', result[0].message_text)

    def test_sas_process(self):
        # Arrange
        self.qs.put_message(self.test_queues[0], 'message1')
        token = self.qs.generate_shared_access_signature(
            self.test_queues[0],
            self._get_shared_access_policy(QueueSharedAccessPermissions.PROCESS),
        )

        # Act
        service = QueueService(credentials.getStorageServicesName(), sas_token=token)
        set_service_options(service)
        result = service.get_messages(self.test_queues[0])

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertEqual('message1', message.message_text)

    def test_sas_signed_identifier(self):
        # Arrange
        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2018-10-12'
        si.access_policy.permission = QueueSharedAccessPermissions.READ
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.qs.set_queue_acl(self.test_queues[0], identifiers)

        self.qs.put_message(self.test_queues[0], 'message1')

        token = self.qs.generate_shared_access_signature(
            self.test_queues[0],
            SharedAccessPolicy(signed_identifier=si.id),
        )

        # Act
        service = QueueService(credentials.getStorageServicesName(), sas_token=token)
        set_service_options(service)
        result = service.peek_messages(self.test_queues[0])

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.message_id)
        self.assertEqual('message1', message.message_text)

    def test_get_queue_acl(self):
        # Arrange

        # Act
        acl = self.qs.get_queue_acl(self.test_queues[0])

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_get_queue_acl_iter(self):
        # Arrange

        # Act
        acl = self.qs.get_queue_acl(self.test_queues[0])
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)
        self.assertEqual(len(acl), 0)

    def test_get_queue_acl_with_non_existing_queue(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.qs.get_queue_acl(self.creatable_queues[0])

        # Assert

    def test_set_queue_acl(self):
        # Arrange

        # Act
        resp = self.qs.set_queue_acl(self.test_queues[0])

        # Assert
        self.assertIsNone(resp)
        acl = self.qs.get_queue_acl(self.test_queues[0])
        self.assertIsNotNone(acl)

    def test_set_queue_acl_with_empty_signed_identifiers(self):
        # Arrange

        # Act
        identifiers = SignedIdentifiers()

        resp = self.qs.set_queue_acl(self.test_queues[0], identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.qs.get_queue_acl(self.test_queues[0])
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 0)

    def test_set_queue_acl_with_signed_identifiers(self):
        # Arrange

        # Act
        si = SignedIdentifier()
        si.id = 'testid'
        si.access_policy.start = '2011-10-11'
        si.access_policy.expiry = '2011-10-12'
        si.access_policy.permission = QueueSharedAccessPermissions.READ
        identifiers = SignedIdentifiers()
        identifiers.signed_identifiers.append(si)

        resp = self.qs.set_queue_acl(self.test_queues[0], identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = self.qs.get_queue_acl(self.test_queues[0])
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.signed_identifiers), 1)
        self.assertEqual(len(acl), 1)
        self.assertEqual(acl.signed_identifiers[0].id, 'testid')
        self.assertEqual(acl[0].id, 'testid')

    def test_set_queue_acl_with_non_existing_queue(self):
        # Arrange

        # Act
        with self.assertRaises(WindowsAzureError):
            self.qs.set_queue_acl(self.creatable_queues[0])

        # Assert

    def test_with_filter(self):
        # Single filter
        called = []

        def my_filter(request, next):
            called.append(True)
            return next(request)
        qc = self.qs.with_filter(my_filter)
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

        qc = self.qs.with_filter(filter_a).with_filter(filter_b)
        qc.put_message(self.test_queues[7], 'message1')

        self.assertEqual(called, ['b', 'a'])

    def test_unicode_create_queue_unicode_name(self):
        # Action
        self.creatable_queues[0] = u'啊齄丂狛狜'

        with self.assertRaises(WindowsAzureError):
            # not supported - queue name must be alphanumeric, lowercase
            self.qs.create_queue(self.creatable_queues[0])

        # Asserts

    def test_unicode_get_messages_unicode_data(self):
        # Action
        self.qs.put_message(self.test_queues[1], u'message1㚈')
        result = self.qs.get_messages(self.test_queues[1])

        # Asserts
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
        # Action
        self.qs.put_message(self.test_queues[7], 'message1')
        list_result1 = self.qs.get_messages(self.test_queues[7])
        self.qs.update_message(self.test_queues[7],
                               list_result1[0].message_id,
                               u'啊齄丂狛狜',
                               list_result1[0].pop_receipt,
                               visibilitytimeout=0)
        list_result2 = self.qs.get_messages(self.test_queues[7])

        # Asserts
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

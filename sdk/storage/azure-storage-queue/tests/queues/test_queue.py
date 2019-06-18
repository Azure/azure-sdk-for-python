# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import (
    datetime,
    timedelta,
    date,
)

from azure.common import (
    AzureHttpError,
    AzureConflictHttpError,
    AzureMissingResourceHttpError,
    AzureException,
)
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.queue._generated.models import StorageErrorException
from azure.storage.queue.models import QueuePermissions
from dateutil.tz import tzutc

from azure.storage.common import (
    AccessPolicy,
    ResourceTypes,
    AccountPermissions,
    TokenCredential,
)
from azure.storage.queue.queue_client import QueueClient
from azure.storage.queue.queue_service_client import QueueServiceClient
from azure.storage.queue.authentication import SharedKeyCredentials
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
    LogCaptured,
)

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'pythonqueue'


# ------------------------------------------------------------------------------


class StorageQueueTest(StorageTestCase):
    def setUp(self):
        super(StorageQueueTest, self).setUp()

        queue_url = self._get_queue_url()
        self.queue_name = TEST_QUEUE_PREFIX
        self.config = QueueServiceClient.create_configuration()
        credentials = SharedKeyCredentials(*self._get_shared_key_credentials())
        self.qsc = QueueServiceClient(account_url=queue_url, credentials=credentials)
        self.qs = QueueClient(queue_url=queue_url, queue_name=self.queue_name, credentials=credentials, configuration=self.config)

        self.test_queues = []

    def tearDown(self):
        if not self.is_playback():
            for queue_name in self.test_queues:
                try:
                    queue_client.delete_queue(queue_name)
                except:
                    pass
        return super(StorageQueueTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.queue_name
        self.test_queues.append(queue_name)
        return queue_name

    def _create_queue(self, prefix=TEST_QUEUE_PREFIX):
        queue_client = self.qsc.get_queue_client(prefix)
        try:
            queue_client.create_queue()
        except:
            pass
        return queue_client

    # --Test cases for queues ----------------------------------------------
    @record
    def test_create_queue(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name=queue_name)
        created = queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @record
    def test_create_queue_already_exist(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        created1 = queue_client.create_queue()
        with self.assertRaises(StorageErrorException):
            queue_client.create_queue()

        # Asserts
        self.assertTrue(created1)

    @record
    def test_create_queue_fail_on_exist(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        created = queue_client.create_queue()
        with self.assertRaises(StorageErrorException):
            queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @record
    def test_create_queue_already_exist_different_metadata(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        created = queue_client.create_queue()
        created2 = queue_client.create_queue({"val": "value"})

        # Asserts
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_create_queue_fail_on_exist_different_metadata(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        created = queue_client.create_queue()
        with self.assertRaises(HttpResponseError):
            queue_client.create_queue({"val": "value"}, True)

        # Asserts
        self.assertTrue(created)

    @record
    def test_create_queue_with_options(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        queue_client.create_queue(
            metadata={'val1': 'test', 'val2': 'blah'})
        metadata = queue_client.get_queue_metadata()

        # Asserts
        self.assertEqual(0, metadata.approximate_message_count)
        self.assertEqual(2, len(metadata))
        self.assertEqual('test', metadata['val1'])
        self.assertEqual('blah', metadata['val2'])

    @record
    def test_delete_non_existing_queue(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name + "1")
        created = queue_client.create_queue()
        deleted = queue_client.delete_queue()
        # Asserts
        self.assertIsNone(deleted)

    @record
    def test_delete_non_existing_queue_fail_not_exist(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        with self.assertRaises(HttpResponseError):
            queue_client.delete_queue()

    @record
    def test_delete_existing_queue_fail_not_exist(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        created = queue_client.create_queue()
        deleted = queue_client.delete_queue()

        # Asserts
        self.assertIsNone(deleted)

    @record
    def test_list_queues(self):
        # Action
        queues = self.qsc.list_queues()

        # Asserts
        self.assertIsNotNone(queues)
         
    @record
    def test_list_queues_with_options(self):
        # Arrange
        prefix = 'listqueue'
        for i in range(0, 4):
            self._create_queue(prefix + str(i))

        # Action
        queues = self.qsc.list_queues(prefix=prefix)
        print(queues)

        # Asserts
        self.assertIsNotNone(queues)
        #self.assertEqual(4, len(queues.queue_items))
        self.assertIsNotNone(queues.queue_items)
        #self.assertIsNone(queues1[0].metadata)
        #self.assertNotEqual('', queues1[0].name)

    @record
    def test_list_queues_with_metadata(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        created = queue_client.create_queue()
        queue_client.set_queue_metadata(metadata={'val1': 'test', 'val2': 'blah'})

        queue = self.qsc.list_queues(include_metadata="True")
        print(queue)
        # Asserts
        self.assertIsNotNone(queue)
        self.assertEqual(queue_name, queue.name)
        self.assertIsNotNone(queue.metadata)
        self.assertEqual(len(queue.metadata), 2)
        self.assertEqual(queue.metadata['val1'], 'test')

    @record
    def test_set_queue_metadata(self):
        # Action
        metadata = {'hello': 'world', 'number': '43'}
        queue = self._create_queue()

        # Act
        queue.set_queue_metadata(metadata)
        metadata_from_response = queue.get_queue_metadata().metadata
        # Assert
        self.assertDictEqual(metadata_from_response, metadata)

    @record
    def test_get_queue_metadata_message_count(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        metadata = queue_client.get_queue_metadata(queue_name)

        # Asserts
        self.assertTrue(metadata.approximate_message_count >= 1)
        self.assertEqual(0, len(metadata))

    @record
    def test_put_message(self):
        # Action.  No exception means pass. No asserts needed.
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        message = queue_client.enqueue_message(u'message4')

        # Asserts
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertIsInstance(message.insertion_time, datetime)
        self.assertIsInstance(message.expiration_time, datetime)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(u'message4', message.content)

    @record
    def test_put_message_large_time_to_live(self):
        # Arrange
        queue_client = self._create_queue()
        # There should be no upper bound on a queue message's time to live
        queue_client.enqueue_message(u'message1', time_to_live=1024*1024*1024)

        # Act
        messages = queue_client.peek_messages()

        # Assert
        self.assertGreaterEqual(messages[0].expiration_time,
                                messages[0].insertion_time + timedelta(seconds=1024 * 1024 * 1024 - 3600))

    @record
    def test_put_message_infinite_time_to_live(self):
        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1', time_to_live=-1)

        # Act
        messages = queue_client.peek_messages()

        # Assert
        self.assertEqual(messages[0].expiration_time.year, date.max.year)

    @record
    def test_get_messages(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        queue_client.enqueue_message(u'message4')
        result = queue_client.get_messages()

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(1, message.dequeue_count)

        self.assertIsInstance(message.insertion_time, datetime)
        self.assertIsInstance(message.expiration_time, datetime)
        self.assertIsInstance(message.time_next_visible, datetime)

    @record
    def test_get_messages_with_options(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        queue_client.enqueue_message(u'message4')
        result = queue_client.get_messages(num_messages=4, visibility_timeout=20)

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(4, len(result))

        for message in result:
            self.assertIsNotNone(message)
            self.assertNotEqual('', message.id)
            self.assertNotEqual('', message.content)
            self.assertNotEqual('', message.pop_receipt)
            self.assertEqual(1, message.dequeue_count)
            self.assertNotEqual('', message.insertion_time)
            self.assertNotEqual('', message.expiration_time)
            self.assertNotEqual('', message.time_next_visible)

    @record
    def test_peek_messages(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        queue_client.enqueue_message(u'message4')
        result = queue_client.peek_messages()

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertNotEqual('', message.content)
        self.assertIsNone(message.pop_receipt)
        self.assertEqual(0, message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertIsNone(message.time_next_visible)

    @record
    def test_peek_messages_with_options(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        queue_client.enqueue_message(u'message4')
        result = queue_client.peek_messages(num_messages=4)

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(4, len(result))
        for message in result:
            self.assertIsNotNone(message)
            self.assertNotEqual('', message.id)
            self.assertNotEqual('', message.content)
            self.assertIsNone(message.pop_receipt)
            self.assertEqual(0, message.dequeue_count)
            self.assertNotEqual('', message.insertion_time)
            self.assertNotEqual('', message.expiration_time)
            self.assertIsNone(message.time_next_visible)

    @record
    def test_clear_messages(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        queue_client.enqueue_message(u'message4')
        queue_client.clear_messages()
        result = queue_client.peek_messages()

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))

    @record
    def test_delete_message(self):
        # Action
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name)
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        queue_client.enqueue_message(u'message4')
        result = queue_client.dequeue_messages()
        queue_client.delete_message(result[0].id, result[0].pop_receipt)
        result2 = queue_client.get_messages(num_messages=32)

        # Asserts
        self.assertIsNotNone(result2)
        self.assertEqual(3, len(result2))

    @record
    def test_update_message(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        list_result1 = queue_client.get_messages()
        message = queue_client.update_message(list_result1[0].id,
                                              list_result1[0].pop_receipt,
                                              0)
        list_result2 = queue_client.get_messages()

        # Asserts
        # Update response
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.time_next_visible)
        self.assertIsInstance(message.time_next_visible, datetime)

        # Get response
        self.assertIsNotNone(list_result2)
        message = list_result2[0]
        self.assertIsNotNone(message)
        self.assertEqual(list_result1[0].id, message.id)
        self.assertEqual(u'message1', message.content)
        self.assertEqual(2, message.dequeue_count)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.insertion_time)
        self.assertIsNotNone(message.expiration_time)
        self.assertIsNotNone(message.time_next_visible)

    @record
    def test_update_message_content(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        list_result1 = queue_client.get_messages()
        message = queue_client.update_message(list_result1[0].id,
                                              list_result1[0].pop_receipt,
                                              0,
                                              content=u'new text', )
        list_result2 = queue_client.get_messages()

        # Asserts
        # Update response
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.time_next_visible)
        self.assertIsInstance(message.time_next_visible, datetime)

        # Get response
        self.assertIsNotNone(list_result2)
        message = list_result2[0]
        self.assertIsNotNone(message)
        self.assertEqual(list_result1[0].id, message.id)
        self.assertEqual(u'new text', message.content)
        self.assertEqual(2, message.dequeue_count)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.insertion_time)
        self.assertIsNotNone(message.expiration_time)
        self.assertIsNotNone(message.time_next_visible)

    def test_account_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        token = queue_client.generate_account_shared_access_signature(
            ResourceTypes.OBJECT,
            AccountPermissions.READ,
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() - timedelta(minutes=5)
        )

        # Act
        service = QueueService(
            account_name=self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
        )
        self._set_test_proxy(service, self.settings)
        result = service.peek_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    @record
    def test_token_credential(self):
        token_credential = TokenCredential(self.generate_oauth_token())

        # Action 1: make sure token works
        service = QueueService(self.settings.OAUTH_STORAGE_ACCOUNT_NAME, token_credential=token_credential)
        queues = list(service.list_queues())
        self.assertIsNotNone(queues)

        # Action 2: change token value to make request fail
        token_credential.token = "YOU SHALL NOT PASS"
        with self.assertRaises(AzureException):
            queues = list(service.list_queues())
            self.assertIsNone(queues)

        # Action 3: update token to make it working again
        token_credential.token = self.generate_oauth_token()
        queues = list(service.list_queues())
        self.assertIsNotNone(queues)

    def test_sas_read(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        token = queue_client.generate_queue_shared_access_signature(
            QueuePermissions.READ,
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() - timedelta(minutes=5)
        )

        # Act
        service = QueueService(
            account_name=self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
        )
        self._set_test_proxy(service, self.settings)
        result = service.peek_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    def test_sas_add(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        token = queue_client.generate_queue_shared_access_signature(
            QueuePermissions.ADD,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueService(
            account_name=self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
        )
        self._set_test_proxy(service, self.settings)
        result = service.put_message(u'addedmessage')

        # Assert
        result = queue_client.get_messages()
        self.assertEqual(u'addedmessage', result[0].content)

    def test_sas_update(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        token = queue_client.generate_queue_shared_access_signature(
            QueuePermissions.UPDATE,
            datetime.utcnow() + timedelta(hours=1),
        )
        result = queue_client.get_messages()

        # Act
        service = QueueService(
            account_name=self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
        )
        self._set_test_proxy(service, self.settings)
        service.update_message(
            result[0].id,
            result[0].pop_receipt,
            visibility_timeout=0,
            content=u'updatedmessage1',
        )

        # Assert
        result = queue_client.get_messages()
        self.assertEqual(u'updatedmessage1', result[0].content)

    def test_sas_process(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        token = queue_client.generate_queue_shared_access_signature(
            QueuePermissions.PROCESS,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueService(
            account_name=self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
        )
        self._set_test_proxy(service, self.settings)
        result = service.get_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    def test_sas_signed_identifier(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = QueuePermissions.READ

        identifiers = {'testid': access_policy}

        queue_client = self._create_queue()
        resp = queue_client.set_queue_acl(identifiers)

        queue_client.enqueue_message(u'message1')

        token = queue_client.generate_queue_shared_access_signature(
            id='testid'
        )

        # Act
        service = QueueService(
            account_name=self.settings.STORAGE_ACCOUNT_NAME,
            sas_token=token,
        )
        self._set_test_proxy(service, self.settings)
        result = service.peek_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    @record
    def test_get_queue_acl(self):
        # Arrange
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name=queue_name)
        created = queue_client.create_queue()

        # Act
        acl = queue_client.get_queue_acl()

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 0)

    @record
    def test_get_queue_acl_with_non_existing_queue(self):
        # Arrange
        queue_name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(queue_name=queue_name)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            queue_client.get_queue_acl()

            # Assert

    @record
    def test_set_queue_acl(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        resp = queue_client.set_queue_acl()

        # Assert
        self.assertIsNone(resp)
        acl = queue_client.get_queue_acl()
        self.assertIsNotNone(acl)

    @record
    def test_set_queue_acl_with_empty_signed_identifiers(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        queue_client.set_queue_acl(signed_identifiers=[])

        # Assert
        acl = queue_client.get_queue_acl()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @record
    def test_set_queue_acl_with_empty_signed_identifier(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        queue_client.set_queue_acl(signed_identifiers=[AccessPolicy()])

        # Assert
        acl = queue_client.get_queue_acl()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 1)
        self.assertIsNotNone(acl['empty'])
        self.assertIsNone(acl['empty'].permission)
        self.assertIsNone(acl['empty'].expiry)
        self.assertIsNone(acl['empty'].start)

    @record
    def test_set_queue_acl_with_signed_identifiers(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        access_policy = AccessPolicy(permission=QueuePermissions.READ,
                                     expiry='2011-10-12',
                                     start='2011-10-11')
        identifiers = [access_policy]

        resp = queue_client.set_queue_acl(signed_identifiers=identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = queue_client.get_queue_acl()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 1)
        self.assertTrue('testid' in acl)

    @record
    def test_set_queue_acl_too_many_ids(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        identifiers = dict()
        for i in range(0, 16):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaises(ValueError):
            queue_client.set_queue_acl(identifiers)

    @record
    def test_set_queue_acl_with_non_existing_queue(self):
        # Arrange
        name = self._get_queue_reference()
        queue_client = self.qsc.get_queue_client(name)

        # Act
        with self.assertRaises(HttpResponseError):
            queue_client.set_queue_acl()

            # Assert

    @record
    def test_unicode_create_queue_unicode_name(self):
        # Action
        queue_name = u'啊齄丂狛狜'

        with self.assertRaises(HttpResponseError):
            # not supported - queue name must be alphanumeric, lowercase
            client = self.qsc.get_queue_client(queue_name)
            client.create_queue()

            # Asserts

    @record
    def test_unicode_get_messages_unicode_data(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1㚈')
        result = queue_client.deque_message()

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1㚈', message.content)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(1, message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertNotEqual('', message.time_next_visible)

    @record
    def test_unicode_update_message_unicode_data(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        list_result1 = queue_client.get_messages()
        queue_client.update_message(list_result1[0].id,
                                    list_result1[0].pop_receipt,
                                    content=u'啊齄丂狛狜',
                                    visibility_timeout=0)
        list_result2 = queue_client.get_messages()

        # Asserts
        self.assertIsNotNone(list_result2)
        message = list_result2[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'啊齄丂狛狜', message.content)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(2, message.dequeue_count)
        self.assertNotEqual('', message.insertion_time)
        self.assertNotEqual('', message.expiration_time)
        self.assertNotEqual('', message.time_next_visible)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

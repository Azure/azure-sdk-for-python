# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
import pytest
import sys
from dateutil.tz import tzutc
from datetime import (
    datetime,
    timedelta,
    date,
)

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError)

from azure.storage.queue import (
    QueueServiceClient,
    QueueClient,
    QueuePermissions,
    AccessPolicy,
    ResourceTypes,
    AccountPermissions,
)

from queuetestcase import (
    QueueTestCase,
    TestMode,
    record,
    LogCaptured,
)

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'pythonqueue'


# ------------------------------------------------------------------------------


class StorageQueueTest(QueueTestCase):
    def setUp(self):
        super(StorageQueueTest, self).setUp()

        queue_url = self._get_queue_url()
        credentials = self._get_shared_key_credential()
        self.qsc = QueueServiceClient(account_url=queue_url, credential=credentials)
        self.test_queues = []

    def tearDown(self):
        if not self.is_playback():
            for queue in self.test_queues:
                try:
                    queue.delete_queue()
                except:
                    pass
        return super(StorageQueueTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = self.qsc.get_queue_client(queue_name)
        self.test_queues.append(queue)
        return queue

    def _create_queue(self, prefix=TEST_QUEUE_PREFIX):
        queue = self._get_queue_reference(prefix)
        created = queue.create_queue()
        return queue

    # --Test cases for queues ----------------------------------------------
    @record
    def test_create_queue(self):
        # Action
        queue_client = self._get_queue_reference()
        created = queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @record
    def test_create_queue_fail_on_exist(self):
        # Action
        queue_client = self._get_queue_reference()
        created = queue_client.create_queue()
        with self.assertRaises(ResourceExistsError):
            queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @record
    def test_create_queue_fail_on_exist_different_metadata(self):
        # Action
        queue_client = self._get_queue_reference()
        created = queue_client.create_queue()
        with self.assertRaises(ResourceExistsError):
            queue_client.create_queue(metadata={"val": "value"})

        # Asserts
        self.assertTrue(created)

    @record
    def test_create_queue_with_options(self):
        # Action
        queue_client = self._get_queue_reference()
        queue_client.create_queue(
            metadata={'val1': 'test', 'val2': 'blah'})
        props = queue_client.get_queue_properties()

        # Asserts
        self.assertEqual(0, props.approximate_message_count)
        self.assertEqual(2, len(props.metadata))
        self.assertEqual('test', props.metadata['val1'])
        self.assertEqual('blah', props.metadata['val2'])

    @record
    def test_delete_non_existing_queue(self):
        # Action
        queue_client = self._get_queue_reference()

        # Asserts
        with self.assertRaises(ResourceNotFoundError):
            queue_client.delete_queue()

    @record
    def test_delete_existing_queue_fail_not_exist(self):
        # Action
        queue_client = self._get_queue_reference()

        created = queue_client.create_queue()
        deleted = queue_client.delete_queue()

        # Asserts
        self.assertIsNone(deleted)

    @record
    def test_list_queues(self):
        # Action
        queues = list(self.qsc.list_queues())

        # Asserts
        self.assertIsNotNone(queues)
        self.assertTrue(len(self.test_queues) <= len(queues))

    @record
    def test_list_queues_with_options(self):
        # Arrange
        prefix = 'listqueue'
        for i in range(0, 4):
            self._create_queue(prefix + str(i))

        # Action
        generator1 = self.qsc.list_queues(
            name_starts_with=prefix,
            results_per_page=3).by_page()
        queues1 = list(next(generator1))

        generator2 = self.qsc.list_queues(
            name_starts_with=prefix,
            include_metadata=True).by_page(generator1.continuation_token)
        queues2 = list(next(generator2))

        # Asserts
        self.assertIsNotNone(queues1)
        self.assertEqual(3, len(queues1))
        self.assertIsNotNone(queues1[0])
        self.assertIsNone(queues1[0].metadata)
        self.assertNotEqual('', queues1[0].name)
        assert generator1.location_mode is not None
        # Asserts
        self.assertIsNotNone(queues2)
        self.assertTrue(len(self.test_queues) - 3 <= len(queues2))
        self.assertIsNotNone(queues2[0])
        self.assertNotEqual('', queues2[0].name)

    @record
    def test_list_queues_with_metadata(self):
        # Action
        queue = self._create_queue()
        queue.set_queue_metadata(metadata={'val1': 'test', 'val2': 'blah'})

        listed_queue = list(self.qsc.list_queues(
            name_starts_with=queue.queue_name,
            results_per_page=1,
            include_metadata=True))[0]

        # Asserts
        self.assertIsNotNone(listed_queue)
        self.assertEqual(queue.queue_name, listed_queue.name)
        self.assertIsNotNone(listed_queue.metadata)
        self.assertEqual(len(listed_queue.metadata), 2)
        self.assertEqual(listed_queue.metadata['val1'], 'test')

    @record
    def test_set_queue_metadata(self):
        # Action
        metadata = {'hello': 'world', 'number': '43'}
        queue = self._create_queue()

        # Act
        queue.set_queue_metadata(metadata)
        metadata_from_response = queue.get_queue_properties().metadata
        # Assert
        self.assertDictEqual(metadata_from_response, metadata)

    @record
    def test_get_queue_metadata_message_count(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        props = queue_client.get_queue_properties()

        # Asserts
        self.assertTrue(props.approximate_message_count >= 1)
        self.assertEqual(0, len(props.metadata))

    @record
    def test_queue_exists(self):
        # Arrange
        queue = self._create_queue()

        # Act
        exists = queue.get_queue_properties()

        # Assert
        self.assertTrue(exists)

    @record
    def test_queue_not_exists(self):
        # Arrange
        queue = self.qsc.get_queue_client(self.get_resource_name('missing'))
        # Act
        with self.assertRaises(ResourceNotFoundError):
            queue.get_queue_properties()

        # Assert

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
        self.assertGreaterEqual(
            messages[0].expiration_time,
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
        message = next(queue_client.receive_messages())

        # Asserts
        self.assertIsNotNone(message)
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
        pager = queue_client.receive_messages(messages_per_page=4, visibility_timeout=20)
        result = list(pager)

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
        result = queue_client.peek_messages(max_messages=4)

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
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        queue_client.enqueue_message(u'message2')
        queue_client.enqueue_message(u'message3')
        queue_client.enqueue_message(u'message4')
        message = next(queue_client.receive_messages())
        queue_client.delete_message(message)

        messages_pager = queue_client.receive_messages(messages_per_page=32)
        messages = list(messages_pager)

        # Asserts
        assert messages is not None
        assert len(messages) == 3

    @record
    def test_update_message(self):
        # Action
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        messages = queue_client.receive_messages()
        list_result1 = next(messages)
        message = queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0)
        list_result2 = next(messages)

        # Asserts
        # Update response
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.time_next_visible)
        self.assertIsInstance(message.time_next_visible, datetime)

        # Get response
        self.assertIsNotNone(list_result2)
        message = list_result2
        self.assertIsNotNone(message)
        self.assertEqual(list_result1.id, message.id)
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

        messages = queue_client.receive_messages()
        list_result1 = next(messages)
        message = queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0,
            content=u'new text')
        list_result2 = next(messages)

        # Asserts
        # Update response
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.time_next_visible)
        self.assertIsInstance(message.time_next_visible, datetime)

        # Get response
        self.assertIsNotNone(list_result2)
        message = list_result2
        self.assertIsNotNone(message)
        self.assertEqual(list_result1.id, message.id)
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
        token = self.qsc.generate_shared_access_signature(
            ResourceTypes.OBJECT,
            AccountPermissions.READ,
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() - timedelta(minutes=5)
        )

        # Act
        service = QueueServiceClient(
            account_url=self.qsc.url,
            credential=token,
        )
        new_queue_client = service.get_queue_client(queue_client.queue_name)
        result = new_queue_client.peek_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    @record
    def test_token_credential(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        token_credential = self.generate_oauth_token()

        # Action 1: make sure token works
        service = QueueServiceClient(self._get_oauth_queue_url(), credential=token_credential)
        queues = service.get_service_properties()
        self.assertIsNotNone(queues)

        # Action 2: change token value to make request fail
        fake_credential = self.generate_fake_token()
        service = QueueServiceClient(self._get_oauth_queue_url(), credential=fake_credential)
        with self.assertRaises(ClientAuthenticationError):
            list(service.list_queues())

        # Action 3: update token to make it working again
        service = QueueServiceClient(self._get_oauth_queue_url(), credential=token_credential)
        queues = list(service.list_queues())
        self.assertIsNotNone(queues)

    def test_sas_read(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        token = queue_client.generate_shared_access_signature(
            QueuePermissions.READ,
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() - timedelta(minutes=5)
        )

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
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
        token = queue_client.generate_shared_access_signature(
            QueuePermissions.ADD,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
        result = service.enqueue_message(u'addedmessage')

        # Assert
        result = next(queue_client.receive_messages())
        self.assertEqual(u'addedmessage', result.content)

    def test_sas_update(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        token = queue_client.generate_shared_access_signature(
            QueuePermissions.UPDATE,
            datetime.utcnow() + timedelta(hours=1),
        )
        messages = queue_client.receive_messages()
        result = next(messages)

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
        service.update_message(
            result.id,
            pop_receipt=result.pop_receipt,
            visibility_timeout=0,
            content=u'updatedmessage1',
        )

        # Assert
        result = next(messages)
        self.assertEqual(u'updatedmessage1', result.content)

    def test_sas_process(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        token = queue_client.generate_shared_access_signature(
            QueuePermissions.PROCESS,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
        message = next(service.receive_messages())

        # Assert
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
        resp = queue_client.set_queue_access_policy(identifiers)

        queue_client.enqueue_message(u'message1')

        token = queue_client.generate_shared_access_signature(
            policy_id='testid'
        )

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
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
        queue_client = self._create_queue()

        # Act
        acl = queue_client.get_queue_access_policy()

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @record
    def test_get_queue_acl_iter(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        acl = queue_client.get_queue_access_policy()
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @record
    def test_get_queue_acl_with_non_existing_queue(self):
        # Arrange
        queue_client = self._get_queue_reference()

        # Act
        with self.assertRaises(ResourceNotFoundError):
            queue_client.get_queue_access_policy()

            # Assert

    @record
    def test_set_queue_acl(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        resp = queue_client.set_queue_access_policy()

        # Assert
        self.assertIsNone(resp)
        acl = queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)

    @record
    def test_set_queue_acl_with_empty_signed_identifiers(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        queue_client.set_queue_access_policy(signed_identifiers={})

        # Assert
        acl = queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @record
    def test_set_queue_acl_with_empty_signed_identifier(self):
        # Arrange
        queue_client = self._create_queue()

        # Act
        queue_client.set_queue_access_policy(signed_identifiers={'empty': AccessPolicy()})

        # Assert
        acl = queue_client.get_queue_access_policy()
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
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow() - timedelta(minutes=5))
        identifiers = {'testid': access_policy}

        resp = queue_client.set_queue_access_policy(signed_identifiers=identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = queue_client.get_queue_access_policy()
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
            queue_client.set_queue_access_policy(identifiers)

    @record
    def test_set_queue_acl_with_non_existing_queue(self):
        # Arrange
        queue_client = self._get_queue_reference()

        # Act
        with self.assertRaises(ResourceNotFoundError):
            queue_client.set_queue_access_policy()

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
        pytest.skip("Uncomment after msrest fix")
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1㚈')
        message = next(queue_client.receive_messages())

        # Asserts
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1㚈', message.content)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(1, message.dequeue_count)
        self.assertIsInstance(message.insertion_time, datetime)
        self.assertIsInstance(message.expiration_time, datetime)
        self.assertIsInstance(message.time_next_visible, datetime)

    @record
    def test_unicode_update_message_unicode_data(self):
        # Action
        pytest.skip("Uncomment after msrest fix")
        queue_client = self._create_queue()
        queue_client.enqueue_message(u'message1')
        messages = queue_client.receive_messages()

        list_result1 = next(messages)
        list_result1.content = u'啊齄丂狛狜'
        queue_client.update_message(list_result1, visibility_timeout=0)

        # Asserts
        message = next(messages)
        self.assertIsNotNone(message)
        self.assertEqual(list_result1.id, message.id)
        self.assertEqual(u'啊齄丂狛狜', message.content)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(2, message.dequeue_count)
        self.assertIsInstance(message.insertion_time, datetime)
        self.assertIsInstance(message.expiration_time, datetime)
        self.assertIsInstance(message.time_next_visible, datetime)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

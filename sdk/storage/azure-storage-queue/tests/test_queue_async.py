# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import asyncio
from dateutil.tz import tzutc
from datetime import (
    datetime,
    timedelta,
    date,
)
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from multidict import CIMultiDict, CIMultiDictProxy
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError)

from azure.core.pipeline.transport import AioHttpTransport

from azure.storage.queue.aio import QueueServiceClient, QueueClient
from azure.storage.queue import (
    QueuePermissions,
    AccessPolicy,
    ResourceTypes,
    AccountPermissions,
)

from asyncqueuetestcase import (
    AsyncQueueTestCase
)

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'pythonqueue'

# ------------------------------------------------------------------------------


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageQueueTestAsync(AsyncQueueTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, qsc, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = qsc.get_queue_client(queue_name)
        return queue

    async def _create_queue(self, qsc, prefix=TEST_QUEUE_PREFIX, queue_list = None):
        queue = self._get_queue_reference(qsc, prefix)
        created = await queue.create_queue()
        if queue_list:
            queue_list.append(created)
        return queue

    # --Test cases for queues ----------------------------------------------
    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_create_queue(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_create_queue_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()
        with self.assertRaises(ResourceExistsError):
            await queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_create_queue_fail_on_exist_different_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()
        with self.assertRaises(ResourceExistsError):
            await queue_client.create_queue(metadata={"val": "value"})

        # Asserts
        self.assertTrue(created)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_create_queue_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue(
            metadata={'val1': 'test', 'val2': 'blah'})
        props = await queue_client.get_queue_properties()

        # Asserts
        self.assertEqual(0, props.approximate_message_count)
        self.assertEqual(2, len(props.metadata))
        self.assertEqual('test', props.metadata['val1'])
        self.assertEqual('blah', props.metadata['val2'])

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_delete_non_existing_queue(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)

        # Asserts
        with self.assertRaises(ResourceNotFoundError):
            await queue_client.delete_queue()

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_delete_existing_queue_fail_not_exist(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)

        created = await queue_client.create_queue()
        deleted = await queue_client.delete_queue()

        # Asserts
        self.assertIsNone(deleted)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_list_queues(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        queues = []
        async for q in qsc.list_queues():
            queues.append(q)

        # Asserts
        self.assertIsNotNone(queues)
        self.assertEqual(len(queues), 1)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_list_queues_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_list = []
        prefix = 'listqueue'
        for i in range(0, 4):
            await self._create_queue(qsc, prefix + str(i), queue_list)

        # Action
        generator1 =  qsc.list_queues(
            name_starts_with=prefix,
            results_per_page=3).by_page()
        queues1 = []
        async for el in await generator1.__anext__():
            queues1.append(el)

        generator2 = qsc.list_queues(
            name_starts_with=prefix,
            include_metadata=True).by_page(generator1.continuation_token)
        queues2 = []
        async for el in await generator2.__anext__():
            queues2.append(el)

        # Asserts
        self.assertIsNotNone(queues1)
        self.assertEqual(3, len(queues1))
        self.assertIsNotNone(queues1[0])
        self.assertIsNone(queues1[0].metadata)
        self.assertNotEqual('', queues1[0].name)
        # Asserts
        self.assertIsNotNone(queues2)
        self.assertTrue(len(queue_list) - 3 <= len(queues2))
        self.assertIsNotNone(queues2[0])
        self.assertNotEqual('', queues2[0].name)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_list_queues_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue = await self._create_queue(qsc)
        await queue.set_queue_metadata(metadata={'val1': 'test', 'val2': 'blah'})

        listed_queue = []
        async for q in qsc.list_queues(
            name_starts_with=queue.queue_name,
            results_per_page=1,
            include_metadata=True):
            listed_queue.append(q)
        listed_queue = listed_queue[0]

        # Asserts
        self.assertIsNotNone(listed_queue)
        self.assertEqual(queue.queue_name, listed_queue.name)
        self.assertIsNotNone(listed_queue.metadata)
        self.assertEqual(len(listed_queue.metadata), 2)
        self.assertEqual(listed_queue.metadata['val1'], 'test')

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_set_queue_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '43'}
        queue = await self._create_queue(qsc)

        # Act
        await queue.set_queue_metadata(metadata)
        metadata_from_response = await queue.get_queue_properties()
        md = metadata_from_response.metadata
        # Assert
        self.assertDictEqual(md, metadata)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_get_queue_metadata_message_count(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        props = await queue_client.get_queue_properties()

        # Asserts
        self.assertTrue(props.approximate_message_count >= 1)
        self.assertEqual(0, len(props.metadata))

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_queue_exists(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue = await self._create_queue(qsc)

        # Act
        exists = await queue.get_queue_properties()

        # Assert
        self.assertTrue(exists)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_queue_not_exists(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue = qsc.get_queue_client(self.get_resource_name('missing'))
        # Act
        with self.assertRaises(ResourceNotFoundError):
            await queue.get_queue_properties()

        # Assert

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_put_message(self, resource_group, location, storage_account, storage_account_key):
        # Action.  No exception means pass. No asserts needed.
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        await queue_client.enqueue_message(u'message2')
        await queue_client.enqueue_message(u'message3')
        message = await queue_client.enqueue_message(u'message4')

        # Asserts
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertIsInstance(message.insertion_time, datetime)
        self.assertIsInstance(message.expiration_time, datetime)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(u'message4', message.content)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_put_message_large_time_to_live(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        # There should be no upper bound on a queue message's time to live
        await queue_client.enqueue_message(u'message1', time_to_live=1024*1024*1024)

        # Act
        messages = await queue_client.peek_messages()

        # Assert
        self.assertGreaterEqual(
            messages[0].expiration_time,
            messages[0].insertion_time + timedelta(seconds=1024 * 1024 * 1024 - 3600))

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_put_message_infinite_time_to_live(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1', time_to_live=-1)

        # Act
        messages = await queue_client.peek_messages()

        # Assert
        self.assertEqual(messages[0].expiration_time.year, date.max.year)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_get_messages(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        await queue_client.enqueue_message(u'message2')
        await queue_client.enqueue_message(u'message3')
        await queue_client.enqueue_message(u'message4')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
            if len(messages):
                break
        message = messages[0]
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

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_get_messages_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        await queue_client.enqueue_message(u'message2')
        await queue_client.enqueue_message(u'message3')
        await queue_client.enqueue_message(u'message4')
        pager = queue_client.receive_messages(messages_per_page=4, visibility_timeout=20)
        result = []
        async for el in pager:
            result.append(el)

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

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_peek_messages(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        await queue_client.enqueue_message(u'message2')
        await queue_client.enqueue_message(u'message3')
        await queue_client.enqueue_message(u'message4')
        result = await queue_client.peek_messages()

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

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_peek_messages_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        await queue_client.enqueue_message(u'message2')
        await queue_client.enqueue_message(u'message3')
        await queue_client.enqueue_message(u'message4')
        result = await queue_client.peek_messages(max_messages=4)

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

    @ResourceGroupPreparer()    
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_clear_messages(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        await queue_client.enqueue_message(u'message2')
        await queue_client.enqueue_message(u'message3')
        await queue_client.enqueue_message(u'message4')
        await queue_client.clear_messages()
        result = await queue_client.peek_messages()

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_delete_message(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        await queue_client.enqueue_message(u'message2')
        await queue_client.enqueue_message(u'message3')
        await queue_client.enqueue_message(u'message4')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
            await queue_client.delete_message(m)
        async for m in queue_client.receive_messages():
            messages.append(m)
        # Asserts
        self.assertIsNotNone(messages)
        self.assertEqual(3, len(messages)-1)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_update_message(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result1 = messages[0]
        message = await queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0)
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

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

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_update_message_content(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')

        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result1 = messages[0]
        message = await queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0,
            content=u'new text')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

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

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        if self.is_playback():
            return

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        token = qsc.generate_shared_access_signature(
            ResourceTypes.OBJECT,
            AccountPermissions.READ,
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() - timedelta(minutes=5)
        )

        # Act
        service = QueueServiceClient(
            account_url=qsc.url,
            credential=token,
        )
        new_queue_client = service.get_queue_client(queue_client.queue_name)
        result = await new_queue_client.peek_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_token_credential(self, resource_group, location, storage_account, storage_account_key):
        pytest.skip("")
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        if self.is_playback():
            return
        token_credential = self.generate_oauth_token()

        # Action 1: make sure token works
        service = QueueServiceClient(self._account_url(storage_account.name), credential=token_credential)
        queues = await service.get_service_properties()
        self.assertIsNotNone(queues)

        # Action 2: change token value to make request fail
        fake_credential = self.generate_fake_token()
        service = QueueServiceClient(self._account_url(storage_account.name), credential=fake_credential)
        with self.assertRaises(ClientAuthenticationError):
            queue_li = service.list_queues()
            list(queue_li)

        # Action 3: update token to make it working again
        service = QueueServiceClient(self._account_url(storage_account.name), credential=token_credential)
        queue_li = await service.list_queues()
        queues = list(queue_li)
        self.assertIsNotNone(queues)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_sas_read(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only
        if self.is_playback():
            return

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
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
        result = await service.peek_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_sas_add(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only
        if self.is_playback():
            return

        # Arrange
        queue_client = await self._create_queue(qsc)
        token = queue_client.generate_shared_access_signature(
            QueuePermissions.ADD,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
        result = await service.enqueue_message(u'addedmessage')

        # Assert
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        result = messages[0]
        self.assertEqual(u'addedmessage', result.content)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_sas_update(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only
        if self.is_playback():
            return

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        token = queue_client.generate_shared_access_signature(
            QueuePermissions.UPDATE,
            datetime.utcnow() + timedelta(hours=1),
        )
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        result = messages[0]
 
        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
        await service.update_message(
            result.id,
            pop_receipt=result.pop_receipt,
            visibility_timeout=0,
            content=u'updatedmessage1',
        )

        # Assert
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        result = messages[0]
        self.assertEqual(u'updatedmessage1', result.content)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_sas_process(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only
        if self.is_playback():
            return

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        token = queue_client.generate_shared_access_signature(
            QueuePermissions.PROCESS,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        message = messages[0]

        # Assert
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_sas_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only
        if self.is_playback():
            return

        # Arrange
        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = QueuePermissions.READ

        identifiers = {'testid': access_policy}

        queue_client = await self._create_queue(qsc)
        resp = await queue_client.set_queue_access_policy(identifiers)

        await queue_client.enqueue_message(u'message1')

        token = queue_client.generate_shared_access_signature(
            policy_id='testid'
        )

        # Act
        service = QueueClient(
            queue_url=queue_client.url,
            credential=token,
        )
        result = await service.peek_messages()

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(1, len(result))
        message = result[0]
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1', message.content)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_get_queue_acl(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        acl = await queue_client.get_queue_access_policy()

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_get_queue_acl_iter(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        acl = await queue_client.get_queue_access_policy()
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_get_queue_acl_with_non_existing_queue(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = self._get_queue_reference(qsc)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await queue_client.get_queue_access_policy()

            # Assert

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_set_queue_acl(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        resp = await queue_client.set_queue_access_policy()

        # Assert
        self.assertIsNone(resp)
        acl = await queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_set_queue_acl_with_empty_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        await queue_client.set_queue_access_policy(signed_identifiers={})

        # Assert
        acl = await queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_set_queue_acl_with_empty_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        await queue_client.set_queue_access_policy(signed_identifiers={'empty': None})

        # Assert
        acl = await queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 1)
        self.assertIsNotNone(acl['empty'])
        self.assertIsNone(acl['empty'].permission)
        self.assertIsNone(acl['empty'].expiry)
        self.assertIsNone(acl['empty'].start)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_set_queue_acl_with_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)

        # Act
        access_policy = AccessPolicy(permission=QueuePermissions.READ,
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow() - timedelta(minutes=5))
        identifiers = {'testid': access_policy}

        resp = await queue_client.set_queue_access_policy(signed_identifiers=identifiers)

        # Assert
        self.assertIsNone(resp)
        acl = await queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 1)
        self.assertTrue('testid' in acl)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_set_queue_acl_too_many_ids(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)

        # Act
        identifiers = dict()
        for i in range(0, 16):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaises(ValueError):
            await queue_client.set_queue_access_policy(identifiers)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_set_queue_acl_with_non_existing_queue(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await queue_client.set_queue_access_policy()

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_unicode_create_queue_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_name = u'啊齄丂狛狜'

        with self.assertRaises(HttpResponseError):
            # not supported - queue name must be alphanumeric, lowercase
            client = qsc.get_queue_client(queue_name)
            await client.create_queue()

            # Asserts

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_unicode_get_messages_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1㚈')
        message = None
        async for m in queue_client.receive_messages():
            message = m
        # Asserts
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1㚈', message.content)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(1, message.dequeue_count)
        self.assertIsInstance(message.insertion_time, datetime)
        self.assertIsInstance(message.expiration_time, datetime)
        self.assertIsInstance(message.time_next_visible, datetime)

    @ResourceGroupPreparer()     
    @StorageAccountPreparer(name_prefix='pyacrstorage')
    @AsyncQueueTestCase.await_prepared_test
    async def test_unicode_update_message_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self._account_url(storage_account.name), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.enqueue_message(u'message1')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)

        list_result1 = messages[0]
        list_result1.content = u'啊齄丂狛狜'
        await queue_client.update_message(list_result1, visibility_timeout=0)
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        # Asserts
        message = messages[0]
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

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
from azure.core.pipeline.transport import AsyncioRequestsTransport
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError)

from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.queue import (
    QueueSasPermissions,
    AccessPolicy,
    ResourceTypes,
    AccountSasPermissions,
    generate_account_sas,
    generate_queue_sas
)
from azure.storage.queue.aio import QueueServiceClient, QueueClient


from _shared.asynctestcase import AsyncStorageTestCase
from _shared.testcase import GlobalStorageAccountPreparer

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'pyqueueasync'

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


class StorageQueueTestAsync(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, qsc, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = qsc.get_queue_client(queue_name)
        return queue

    async def _create_queue(self, qsc, prefix=TEST_QUEUE_PREFIX, queue_list=None):
        queue = self._get_queue_reference(qsc, prefix)
        created = await queue.create_queue()
        if queue_list:
            queue_list.append(created)
        return queue

    # --Test cases for queues ----------------------------------------------
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_queue(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_queue_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()
        with self.assertRaises(ResourceExistsError):
            await queue_client.create_queue()

        # Asserts
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_queue_fail_on_exist_different_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()
        with self.assertRaises(ResourceExistsError):
            await queue_client.create_queue(metadata={"val": "value"})

        # Asserts
        self.assertTrue(created)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_queue_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue(
            metadata={'val1': 'test', 'val2': 'blah'})
        props = await queue_client.get_queue_properties()

        # Asserts
        self.assertEqual(0, props.approximate_message_count)
        self.assertEqual(2, len(props.metadata))
        self.assertEqual('test', props.metadata['val1'])
        self.assertEqual('blah', props.metadata['val2'])

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_non_existing_queue(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)

        # Asserts
        with self.assertRaises(ResourceNotFoundError):
            await queue_client.delete_queue()

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_existing_queue_fail_not_exist(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)

        created = await queue_client.create_queue()
        deleted = await queue_client.delete_queue()

        # Asserts
        self.assertIsNone(deleted)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_queues(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        queues = []
        async for q in qsc.list_queues():
            queues.append(q)

        # Asserts
        self.assertIsNotNone(queues)
        assert len(queues) >= 1

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_queues_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_queues_with_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_queue_metadata(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        metadata = {'hello': 'world', 'number': '43'}
        queue = await self._create_queue(qsc)

        # Act
        await queue.set_queue_metadata(metadata)
        metadata_from_response = await queue.get_queue_properties()
        md = metadata_from_response.metadata
        # Assert
        self.assertDictEqual(md, metadata)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_queue_metadata_message_count(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        props = await queue_client.get_queue_properties()

        # Asserts
        self.assertTrue(props.approximate_message_count >= 1)
        self.assertEqual(0, len(props.metadata))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_queue_exists(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = await self._create_queue(qsc)

        # Act
        exists = await queue.get_queue_properties()

        # Assert
        self.assertTrue(exists)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_queue_not_exists(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue = qsc.get_queue_client(self.get_resource_name('missing'))
        # Act
        with self.assertRaises(ResourceNotFoundError):
            await queue.get_queue_properties()

        # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_message(self, resource_group, location, storage_account, storage_account_key):
        # Action.  No exception means pass. No asserts needed.
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')
        message = await queue_client.send_message(u'message4')

        # Asserts
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertIsInstance(message.inserted_on, datetime)
        self.assertIsInstance(message.expires_on, datetime)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(u'message4', message.content)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_message_large_time_to_live(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        # There should be no upper bound on a queue message's time to live
        await queue_client.send_message(u'message1', time_to_live=1024*1024*1024)

        # Act
        messages = await queue_client.peek_messages()

        # Assert
        self.assertGreaterEqual(
            messages[0].expires_on,
            messages[0].inserted_on + timedelta(seconds=1024 * 1024 * 1024 - 3600))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_put_message_infinite_time_to_live(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1', time_to_live=-1)

        # Act
        messages = await queue_client.peek_messages()

        # Assert
        self.assertEqual(messages[0].expires_on.year, date.max.year)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_messages(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')
        await queue_client.send_message(u'message4')
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

        self.assertIsInstance(message.inserted_on, datetime)
        self.assertIsInstance(message.expires_on, datetime)
        self.assertIsInstance(message.next_visible_on, datetime)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_receive_one_message(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        self.assertIsNone(await queue_client.receive_message())

        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')

        message1 = await queue_client.receive_message()
        message2 = await queue_client.receive_message()
        peeked_message3 = await queue_client.peek_messages()

        # Asserts
        self.assertIsNotNone(message1)
        self.assertNotEqual('', message1.id)
        self.assertEqual(u'message1', message1.content)
        self.assertNotEqual('', message1.pop_receipt)
        self.assertEqual(1, message1.dequeue_count)

        self.assertIsNotNone(message2)
        self.assertNotEqual('', message2.id)
        self.assertEqual(u'message2', message2.content)
        self.assertNotEqual('', message2.pop_receipt)
        self.assertEqual(1, message2.dequeue_count)

        self.assertEqual(u'message3', peeked_message3[0].content)
        self.assertEqual(0, peeked_message3[0].dequeue_count)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_messages_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')
        await queue_client.send_message(u'message4')
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
            self.assertNotEqual('', message.inserted_on)
            self.assertNotEqual('', message.expires_on)
            self.assertNotEqual('', message.next_visible_on)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_peek_messages(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')
        await queue_client.send_message(u'message4')
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
        self.assertNotEqual('', message.inserted_on)
        self.assertNotEqual('', message.expires_on)
        self.assertIsNone(message.next_visible_on)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_peek_messages_with_options(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')
        await queue_client.send_message(u'message4')
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
            self.assertNotEqual('', message.inserted_on)
            self.assertNotEqual('', message.expires_on)
            self.assertIsNone(message.next_visible_on)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_clear_messages(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')
        await queue_client.send_message(u'message4')
        await queue_client.clear_messages()
        result = await queue_client.peek_messages()

        # Asserts
        self.assertIsNotNone(result)
        self.assertEqual(0, len(result))

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_message(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        await queue_client.send_message(u'message2')
        await queue_client.send_message(u'message3')
        await queue_client.send_message(u'message4')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
            await queue_client.delete_message(m)
        async for m in queue_client.receive_messages():
            messages.append(m)
        # Asserts
        self.assertIsNotNone(messages)
        self.assertEqual(3, len(messages)-1)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_update_message(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
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
        self.assertIsNotNone(message.next_visible_on)
        self.assertIsInstance(message.next_visible_on, datetime)

        # Get response
        self.assertIsNotNone(list_result2)
        message = list_result2
        self.assertIsNotNone(message)
        self.assertEqual(list_result1.id, message.id)
        self.assertEqual(u'message1', message.content)
        self.assertEqual(2, message.dequeue_count)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.inserted_on)
        self.assertIsNotNone(message.expires_on)
        self.assertIsNotNone(message.next_visible_on)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_update_message_content(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')

        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result1 = messages[0]
        message = await queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0,
            content=u'new text')
        self.assertEqual(u'new text', message.content)

        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Asserts
        # Update response
        self.assertIsNotNone(message)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.next_visible_on)
        self.assertIsInstance(message.next_visible_on, datetime)

        # Get response
        self.assertIsNotNone(list_result2)
        message = list_result2
        self.assertIsNotNone(message)
        self.assertEqual(list_result1.id, message.id)
        self.assertEqual(u'new text', message.content)
        self.assertEqual(2, message.dequeue_count)
        self.assertIsNotNone(message.pop_receipt)
        self.assertIsNotNone(message.inserted_on)
        self.assertIsNotNone(message.expires_on)
        self.assertIsNotNone(message.next_visible_on)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        token = generate_account_sas(
            qsc.account_name,
            qsc.credential.account_key,
            ResourceTypes(object=True),
            AccountSasPermissions(read=True),
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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_token_credential(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        token_credential = self.generate_oauth_token()

        # Action 1: make sure token works
        service = QueueServiceClient(self.account_url(storage_account, "queue"), credential=token_credential)
        queues = await service.get_service_properties()
        self.assertIsNotNone(queues)

        # Action 2: change token value to make request fail
        fake_credential = self.generate_fake_token()
        service = QueueServiceClient(self.account_url(storage_account, "queue"), credential=fake_credential)
        with self.assertRaises(ClientAuthenticationError):
            await service.get_service_properties()

        # Action 3: update token to make it working again
        service = QueueServiceClient(self.account_url(storage_account, "queue"), credential=token_credential)
        queues = await service.get_service_properties()  # Not raise means success
        self.assertIsNotNone(queues)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_sas_read(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        token = generate_queue_sas(
            queue_client.account_name,
            queue_client.queue_name,
            queue_client.credential.account_key,
            QueueSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() - timedelta(minutes=5)
        )

        # Act
        service = QueueClient.from_queue_url(
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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_sas_add(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        queue_client = await self._create_queue(qsc)
        token = generate_queue_sas(
            queue_client.account_name,
            queue_client.queue_name,
            queue_client.credential.account_key,
            QueueSasPermissions(add=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueClient.from_queue_url(
            queue_url=queue_client.url,
            credential=token,
        )
        result = await service.send_message(u'addedmessage')
        self.assertEqual(u'addedmessage', result.content)

        # Assert
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        result = messages[0]
        self.assertEqual(u'addedmessage', result.content)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_sas_update(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        token = generate_queue_sas(
            queue_client.account_name,
            queue_client.queue_name,
            queue_client.credential.account_key,
            QueueSasPermissions(update=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        result = messages[0]

        # Act
        service = QueueClient.from_queue_url(
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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_sas_process(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
        token = generate_queue_sas(
            queue_client.account_name,
            queue_client.queue_name,
            queue_client.credential.account_key,
            QueueSasPermissions(process=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = QueueClient.from_queue_url(
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

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_sas_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        access_policy = AccessPolicy()
        access_policy.start = datetime.utcnow() - timedelta(hours=1)
        access_policy.expiry = datetime.utcnow() + timedelta(hours=1)
        access_policy.permission = QueueSasPermissions(read=True)

        identifiers = {'testid': access_policy}

        queue_client = await self._create_queue(qsc)
        resp = await queue_client.set_queue_access_policy(identifiers)

        await queue_client.send_message(u'message1')

        token = generate_queue_sas(
            queue_client.account_name,
            queue_client.queue_name,
            queue_client.credential.account_key,
            policy_id='testid'
        )

        # Act
        service = QueueClient.from_queue_url(
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_queue_acl(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        acl = await queue_client.get_queue_access_policy()

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_queue_acl_iter(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        acl = await queue_client.get_queue_access_policy()
        for signed_identifier in acl:
            pass

        # Assert
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_queue_acl_with_non_existing_queue(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = self._get_queue_reference(qsc)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await queue_client.get_queue_access_policy()

            # Assert

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_queue_acl(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        resp = await queue_client.set_queue_access_policy(signed_identifiers=dict())

        # Assert
        self.assertIsNone(resp)
        acl = await queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_queue_acl_with_empty_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        await queue_client.set_queue_access_policy(signed_identifiers={})

        # Assert
        acl = await queue_client.get_queue_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl), 0)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_queue_acl_with_empty_signed_identifier(self, resource_group, location, storage_account, storage_account_key):
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_queue_acl_with_signed_identifiers(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)

        # Act
        access_policy = AccessPolicy(permission=QueueSasPermissions(read=True),
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

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_queue_acl_too_many_ids(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)

        # Act
        identifiers = dict()
        for i in range(0, 16):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaises(ValueError):
            await queue_client.set_queue_access_policy(identifiers)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_queue_acl_with_non_existing_queue(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = self._get_queue_reference(qsc)

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await queue_client.set_queue_access_policy(signed_identifiers=dict())

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_unicode_create_queue_unicode_name(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_name = u'啊齄丂狛狜'

        with self.assertRaises(HttpResponseError):
            # not supported - queue name must be alphanumeric, lowercase
            client = qsc.get_queue_client(queue_name)
            await client.create_queue()

            # Asserts

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_unicode_get_messages_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1㚈')
        message = None
        async for m in queue_client.receive_messages():
            message = m
        # Asserts
        self.assertIsNotNone(message)
        self.assertNotEqual('', message.id)
        self.assertEqual(u'message1㚈', message.content)
        self.assertNotEqual('', message.pop_receipt)
        self.assertEqual(1, message.dequeue_count)
        self.assertIsInstance(message.inserted_on, datetime)
        self.assertIsInstance(message.expires_on, datetime)
        self.assertIsInstance(message.next_visible_on, datetime)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_unicode_update_message_unicode_data(self, resource_group, location, storage_account, storage_account_key):
        # Action
        qsc = QueueServiceClient(self.account_url(storage_account, "queue"), storage_account_key, transport=AiohttpTestTransport())
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message(u'message1')
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
        self.assertIsInstance(message.inserted_on, datetime)
        self.assertIsInstance(message.expires_on, datetime)
        self.assertIsInstance(message.next_visible_on, datetime)

    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_transport_closed_only_once_async(self, resource_group, location, storage_account, storage_account_key):
        transport = AioHttpTransport()
        prefix = TEST_QUEUE_PREFIX
        queue_name = self.get_resource_name(prefix)
        async with QueueServiceClient(self.account_url(storage_account, "queue"), credential=storage_account_key, transport=transport) as qsc:
            await qsc.get_service_properties()
            assert transport.session is not None
            async with qsc.get_queue_client(queue_name) as qc:
                assert transport.session is not None
            await qsc.get_service_properties()
            assert transport.session is not None

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from datetime import date, datetime, timedelta

import pytest
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError
)
from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.queue import (
    AccessPolicy,
    AccountSasPermissions,
    generate_account_sas,
    generate_queue_sas,
    QueueSasPermissions,
    ResourceTypes
)
from azure.storage.queue.aio import QueueClient, QueueServiceClient

from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import QueuePreparer

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'pyqueueasync'
# ------------------------------------------------------------------------------
# pylint: disable=locally-disabled, multiple-statements, fixme, too-many-lines


class TestAsyncStorageQueue(AsyncStorageRecordedTestCase):
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
    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_create_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()

        # Asserts
        assert created

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_create_queue_fail_on_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()
        with pytest.raises(ResourceExistsError):
            await queue_client.create_queue()

        # Asserts
        assert created

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_create_queue_fail_on_exist_different_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        created = await queue_client.create_queue()
        with pytest.raises(ResourceExistsError):
            await queue_client.create_queue(metadata={"val": "value"})

        # Asserts
        assert created

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_create_queue_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue(
            metadata={'val1': 'test', 'val2': 'blah'})
        props = await queue_client.get_queue_properties()

        # Asserts
        assert 0 == props.approximate_message_count
        assert 2 == len(props.metadata)
        assert 'test' == props.metadata['val1']
        assert 'blah' == props.metadata['val2']

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages_with_max_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        await queue_client.send_message('message5')
        await queue_client.send_message('message6')
        await queue_client.send_message('message7')
        await queue_client.send_message('message8')
        await queue_client.send_message('message9')
        await queue_client.send_message('message10')
        result = []
        async for m in queue_client.receive_messages(max_messages=5):
            result.append(m)

        # Asserts
        assert result is not None
        assert 5 == len(result)

        for message in result:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert '' != message.pop_receipt
            assert 1 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert '' != message.next_visible_on

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages_with_too_little_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        await queue_client.send_message('message5')
        result = []
        async for m in queue_client.receive_messages(max_messages=10):
            result.append(m)

        # Asserts
        assert result is not None
        assert 5 == len(result)

        for message in result:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert '' != message.pop_receipt
            assert 1 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert '' != message.next_visible_on

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages_with_page_bigger_than_max(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        await queue_client.send_message('message5')

        # Asserts
        with pytest.raises(ValueError):
            queue_client.receive_messages(messages_per_page=5, max_messages=2)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages_with_remainder(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        await queue_client.send_message('message5')
        await queue_client.send_message('message6')
        await queue_client.send_message('message7')
        await queue_client.send_message('message8')
        await queue_client.send_message('message9')
        await queue_client.send_message('message10')
        await queue_client.send_message('message11')
        await queue_client.send_message('message12')

        result = []
        async for m in queue_client.receive_messages(messages_per_page=3, max_messages=10):
            result.append(m)

        remainder = []
        async for m in queue_client.receive_messages():
            remainder.append(m)

        # Asserts
        assert result is not None
        assert 10 == len(result)

        assert remainder is not None
        assert 2 == len(remainder)

        for message in result:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert '' != message.pop_receipt
            assert 1 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert '' != message.next_visible_on

        for message in remainder:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert '' != message.pop_receipt
            assert 1 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert '' != message.next_visible_on

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_delete_non_existing_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)

        # Asserts
        with pytest.raises(ResourceNotFoundError):
            await queue_client.delete_queue()

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_delete_existing_queue_fail_not_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)

        created = await queue_client.create_queue()
        deleted = await queue_client.delete_queue()

        # Asserts
        assert deleted is None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_list_queues(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        queues = []
        async for q in qsc.list_queues():
            queues.append(q)

        # Asserts
        assert queues is not None
        assert len(queues) >= 1

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_list_queues_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
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
        assert queues1 is not None
        assert 3 == len(queues1)
        assert queues1[0] is not None
        assert queues1[0].metadata is None
        assert '' != queues1[0].name
        # Asserts
        assert queues2 is not None
        assert len(queue_list) - 3 <= len(queues2)
        assert queues2[0] is not None
        assert '' != queues2[0].name

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_list_queues_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
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
        assert listed_queue is not None
        assert queue.queue_name == listed_queue.name
        assert listed_queue.metadata is not None
        assert len(listed_queue.metadata) == 2
        assert listed_queue.metadata['val1'] == 'test'

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_list_queues_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        sas_token = self.generate_sas(
            generate_account_sas,
            storage_account_name,
            storage_account_key,
            ResourceTypes(service=True),
            AccountSasPermissions(list=True),
            datetime.utcnow() + timedelta(hours=1)
        )

        # Act
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=sas_token)
        queues = []
        async for q in qsc.list_queues():
            queues.append(q)

        # Assert
        assert queues is not None
        assert len(queues) >= 1

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_set_queue_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        metadata = {'hello': 'world', 'number': '43'}
        queue = await self._create_queue(qsc)

        # Act
        await queue.set_queue_metadata(metadata)
        metadata_from_response = await queue.get_queue_properties()
        md = metadata_from_response.metadata
        # Assert
        assert md == metadata

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_queue_metadata_message_count(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        props = await queue_client.get_queue_properties()

        # Asserts
        assert props.approximate_message_count >= 1
        assert 0 == len(props.metadata)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_queue_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = await self._create_queue(qsc)

        # Act
        exists = await queue.get_queue_properties()

        # Assert
        assert exists

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_queue_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = qsc.get_queue_client(self.get_resource_name('missing'))
        # Act
        with pytest.raises(ResourceNotFoundError):
            await queue.get_queue_properties()

        # Assert

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_put_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action.  No exception means pass. No asserts needed.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        message = await queue_client.send_message('message4')

        # Asserts
        assert message is not None
        assert '' != message.id
        assert isinstance(message.inserted_on, datetime)
        assert isinstance(message.expires_on, datetime)
        assert '' != message.pop_receipt
        assert 'message4' == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_put_message_large_time_to_live(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        # There should be no upper bound on a queue message's time to live
        await queue_client.send_message('message1', time_to_live=1024*1024*1024)

        # Act
        messages = await queue_client.peek_messages()

        # Assert
        assert messages[0].expires_on >= (messages[0].inserted_on + timedelta(seconds=1024 * 1024 * 1024 - 3600))

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_put_message_infinite_time_to_live(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1', time_to_live=-1)

        # Act
        messages = await queue_client.peek_messages()

        # Assert
        assert messages[0].expires_on.year == date.max.year

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
            if len(messages):
                break
        message = messages[0]
        # Asserts
        assert message is not None
        assert message is not None
        assert '' != message.id
        assert 'message1' == message.content
        assert '' != message.pop_receipt
        assert 1 == message.dequeue_count

        assert isinstance(message.inserted_on, datetime)
        assert isinstance(message.expires_on, datetime)
        assert isinstance(message.next_visible_on, datetime)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_receive_one_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        assert await queue_client.receive_message() is None

        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')

        message1 = await queue_client.receive_message()
        message2 = await queue_client.receive_message()
        peeked_message3 = await queue_client.peek_messages()

        # Asserts
        assert message1 is not None
        assert '' != message1.id
        assert 'message1' == message1.content
        assert '' != message1.pop_receipt
        assert 1 == message1.dequeue_count

        assert message2 is not None
        assert '' != message2.id
        assert 'message2' == message2.content
        assert '' != message2.pop_receipt
        assert 1 == message2.dequeue_count

        assert 'message3' == peeked_message3[0].content
        assert 0 == peeked_message3[0].dequeue_count

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_messages_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        pager = queue_client.receive_messages(messages_per_page=4, visibility_timeout=20)
        result = []
        async for el in pager:
            result.append(el)

        # Asserts
        assert result is not None
        assert 4 == len(result)

        for message in result:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert '' != message.pop_receipt
            assert 1 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert '' != message.next_visible_on

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_peek_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        result = await queue_client.peek_messages()

        # Asserts
        assert result is not None
        assert 1 == len(result)
        message = result[0]
        assert message is not None
        assert '' != message.id
        assert '' != message.content
        assert message.pop_receipt is None
        assert 0 == message.dequeue_count
        assert '' != message.inserted_on
        assert '' != message.expires_on
        assert message.next_visible_on is None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_peek_messages_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        result = await queue_client.peek_messages(max_messages=4)

        # Asserts
        assert result is not None
        assert 4 == len(result)
        for message in result:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert message.pop_receipt is None
            assert 0 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert message.next_visible_on is None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_clear_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        await queue_client.clear_messages()
        result = await queue_client.peek_messages()

        # Asserts
        assert result is not None
        assert 0 == len(result)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_delete_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        await queue_client.send_message('message2')
        await queue_client.send_message('message3')
        await queue_client.send_message('message4')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
            await queue_client.delete_message(m)
        async for m in queue_client.receive_messages():
            messages.append(m)
        # Asserts
        assert messages is not None
        assert 3 == len(messages)-1

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
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
        assert message is not None
        assert message.pop_receipt is not None
        assert message.next_visible_on is not None
        assert isinstance(message.next_visible_on, datetime)

        # Get response
        assert list_result2 is not None
        message = list_result2
        assert message is not None
        assert list_result1.id == message.id
        assert 'message1' == message.content
        assert 2 == message.dequeue_count
        assert message.pop_receipt is not None
        assert message.inserted_on is not None
        assert message.expires_on is not None
        assert message.next_visible_on is not None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_update_message_content(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')

        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result1 = messages[0]
        message = await queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0,
            content='new text')
        assert 'new text' == message.content

        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        list_result2 = messages[0]

        # Asserts
        # Update response
        assert message is not None
        assert message.pop_receipt is not None
        assert message.next_visible_on is not None
        assert isinstance(message.next_visible_on, datetime)

        # Get response
        assert list_result2 is not None
        message = list_result2
        assert message is not None
        assert list_result1.id == message.id
        assert 'new text' == message.content
        assert 2 == message.dequeue_count
        assert message.pop_receipt is not None
        assert message.inserted_on is not None
        assert message.expires_on is not None
        assert message.next_visible_on is not None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        token = self.generate_sas(
            generate_account_sas,
            qsc.account_name,
            qsc.credential.account_key,
            ResourceTypes(object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() - timedelta(minutes=5)
        )

        # Act
        for credential in [token, AzureSasCredential(token)]:
            service = QueueServiceClient(
                account_url=qsc.url,
                credential=credential,
            )
            new_queue_client = service.get_queue_client(queue_client.queue_name)
            result = await new_queue_client.peek_messages()

            # Assert
            assert result is not None
            assert 1 == len(result)
            message = result[0]
            assert message is not None
            assert '' != message.id
            assert 'message1' == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_azure_named_key_credential_access(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        # Arrange
        named_key = AzureNamedKeyCredential(storage_account_name, storage_account_key)
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"), named_key)
        queue_client = self._get_queue_reference(qsc)
        await queue_client.create_queue()
        await queue_client.send_message('message1')

        # Act
        result = await queue_client.peek_messages()

        # Assert
        assert result is not None

    @QueuePreparer()
    async def test_account_sas_raises_if_sas_already_in_uri(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        with pytest.raises(ValueError):
            QueueServiceClient(
                self.account_url(storage_account_name, "queue") + "?sig=foo",
                credential=AzureSasCredential("?foo=bar"))

    @pytest.mark.live_test_only
    @QueuePreparer()
    async def test_token_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        token_credential = self.get_credential(QueueServiceClient, is_async=True)

        # Action 1: make sure token works
        service = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            credential=token_credential)
        queues = await service.get_service_properties()
        assert queues is not None

        # Action 2: change token value to make request fail
        fake_credential = AsyncFakeCredential()
        service = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            credential=fake_credential)
        with pytest.raises(ClientAuthenticationError):
            await service.get_service_properties()

        # Action 3: update token to make it working again
        service = QueueServiceClient(
            self.account_url(storage_account_name, "queue"),
            credential=token_credential)
        queues = await service.get_service_properties()  # Not raise means success
        assert queues is not None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_sas_read(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        token = self.generate_sas(
            generate_queue_sas,
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
        assert result is not None
        assert 1 == len(result)
        message = result[0]
        assert message is not None
        assert '' != message.id
        assert 'message1' == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_sas_add(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)

        # Arrange
        queue_client = await self._create_queue(qsc)
        token = self.generate_sas(
            generate_queue_sas,
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
        result = await service.send_message('addedmessage')
        assert 'addedmessage' == result.content

        # Assert
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        result = messages[0]
        assert 'addedmessage' == result.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_sas_update(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        token = self.generate_sas(
            generate_queue_sas,
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
            content='updatedmessage1',
        )

        # Assert
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        result = messages[0]
        assert 'updatedmessage1' == result.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_sas_process(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)

        # Arrange
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        token = self.generate_sas(
            generate_queue_sas,
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
        assert message is not None
        assert '' != message.id
        assert 'message1' == message.content

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_sas_signed_identifier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop('variables', {})

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)

        # Arrange
        access_policy = AccessPolicy()
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow() - timedelta(hours=1))
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        access_policy.start = start_time
        access_policy.expiry = expiry_time
        access_policy.permission = QueueSasPermissions(read=True)

        identifiers = {'testid': access_policy}

        queue_client = await self._create_queue(qsc)
        resp = await queue_client.set_queue_access_policy(identifiers)

        await queue_client.send_message('message1')

        token = self.generate_sas(
            generate_queue_sas,
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
        assert result is not None
        assert 1 == len(result)
        message = result[0]
        assert message is not None
        assert '' != message.id
        assert 'message1' == message.content

        return variables

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_queue_acl(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        acl = await queue_client.get_queue_access_policy()

        # Assert
        assert acl is not None
        assert len(acl) == 0

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_queue_acl_iter(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        acl = await queue_client.get_queue_access_policy()
        for signed_identifier in acl:
            pass

        # Assert
        assert acl is not None
        assert len(acl) == 0

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_get_queue_acl_with_non_existing_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue_client = self._get_queue_reference(qsc)

        # Act
        with pytest.raises(ResourceNotFoundError):
            await queue_client.get_queue_access_policy()

            # Assert

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_set_queue_acl(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        resp = await queue_client.set_queue_access_policy(signed_identifiers=dict())

        # Assert
        assert resp is None
        acl = await queue_client.get_queue_access_policy()
        assert acl is not None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_set_queue_acl_with_empty_signed_identifiers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        await queue_client.set_queue_access_policy(signed_identifiers={})

        # Assert
        acl = await queue_client.get_queue_access_policy()
        assert acl is not None
        assert len(acl) == 0

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_set_queue_acl_with_empty_signed_identifier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Arrange
        queue_client = await self._create_queue(qsc)

        # Act
        await queue_client.set_queue_access_policy(signed_identifiers={'empty': None})

        # Assert
        acl = await queue_client.get_queue_access_policy()
        assert acl is not None
        assert len(acl) == 1
        assert acl['empty'] is not None
        assert acl['empty'].permission is None
        assert acl['empty'].expiry is None
        assert acl['empty'].start is None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_set_queue_acl_with_signed_identifiers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop('variables', {})

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)

        # Act
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow() - timedelta(minutes=5))
        access_policy = AccessPolicy(permission=QueueSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        identifiers = {'testid': access_policy}

        resp = await queue_client.set_queue_access_policy(signed_identifiers=identifiers)

        # Assert
        assert resp is None
        acl = await queue_client.get_queue_access_policy()
        assert acl is not None
        assert len(acl) == 1
        assert 'testid' in acl

        return variables

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_set_queue_acl_too_many_ids(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)

        # Act
        identifiers = dict()
        for i in range(0, 16):
            identifiers[f'id{i}'] = AccessPolicy()

        # Assert
        with pytest.raises(ValueError):
            await queue_client.set_queue_access_policy(identifiers)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_set_queue_acl_with_non_existing_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)

        # Act
        with pytest.raises(ResourceNotFoundError):
            await queue_client.set_queue_access_policy(signed_identifiers=dict())

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_unicode_create_queue_unicode_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_name = '啊齄丂狛狜'

        with pytest.raises(HttpResponseError):
            # not supported - queue name must be alphanumeric, lowercase
            client = qsc.get_queue_client(queue_name)
            await client.create_queue()

            # Asserts

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_unicode_get_messages_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1㚈')
        message = None
        async for m in queue_client.receive_messages():
            message = m
        # Asserts
        assert message is not None
        assert '' != message.id
        assert 'message1㚈' == message.content
        assert '' != message.pop_receipt
        assert 1 == message.dequeue_count
        assert isinstance(message.inserted_on, datetime)
        assert isinstance(message.expires_on, datetime)
        assert isinstance(message.next_visible_on, datetime)

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_unicode_update_message_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = await self._create_queue(qsc)
        await queue_client.send_message('message1')
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)

        list_result1 = messages[0]
        list_result1.content = '啊齄丂狛狜'
        await queue_client.update_message(list_result1, visibility_timeout=0)
        messages = []
        async for m in queue_client.receive_messages():
            messages.append(m)
        # Asserts
        message = messages[0]
        assert message is not None
        assert list_result1.id == message.id
        assert '啊齄丂狛狜' == message.content
        assert '' != message.pop_receipt
        assert 2 == message.dequeue_count
        assert isinstance(message.inserted_on, datetime)
        assert isinstance(message.expires_on, datetime)
        assert isinstance(message.next_visible_on, datetime)

    @pytest.mark.live_test_only
    @QueuePreparer()
    async def test_transport_closed_only_once(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = AioHttpTransport()
        prefix = TEST_QUEUE_PREFIX
        queue_name = self.get_resource_name(prefix)
        async with QueueServiceClient(
                self.account_url(storage_account_name, "queue"),
                credential=storage_account_key, transport=transport) as qsc:
            await qsc.get_service_properties()
            assert transport.session is not None
            async with qsc.get_queue_client(queue_name) as qc:
                assert transport.session is not None
            await qsc.get_service_properties()
            assert transport.session is not None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_storage_account_audience_queue_service_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        await qsc.get_service_properties()

        # Act
        token_credential = self.get_credential(QueueServiceClient, is_async=True)
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"), credential=token_credential,
            audience=f'https://{storage_account_name}.queue.core.windows.net'
        )

        # Assert
        response = await qsc.get_service_properties()
        assert response is not None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_bad_audience_queue_service_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        await qsc.get_service_properties()

        # Act
        token_credential = self.get_credential(QueueServiceClient, is_async=True)
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"), credential=token_credential,
            audience=f'https://badaudience.queue.core.windows.net'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        await qsc.get_service_properties()

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_storage_account_audience_queue_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        queue_name = self.get_resource_name(TEST_QUEUE_PREFIX)
        queue = QueueClient(self.account_url(storage_account_name, "queue"), queue_name, storage_account_key)
        await queue.create_queue()

        # Act
        token_credential = self.get_credential(QueueServiceClient, is_async=True)
        queue = QueueClient(
            self.account_url(storage_account_name, "queue"), queue_name, credential=token_credential,
            audience=f'https://{storage_account_name}.queue.core.windows.net'
        )

        # Assert
        response = await queue.get_queue_properties()
        assert response is not None

    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_bad_audience_queue_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        queue_name = self.get_resource_name(TEST_QUEUE_PREFIX)
        queue = QueueClient(self.account_url(storage_account_name, "queue"), queue_name, storage_account_key)
        await queue.create_queue()

        # Act
        token_credential = self.get_credential(QueueServiceClient, is_async=True)
        queue = QueueClient(
            self.account_url(storage_account_name, "queue"), queue_name, credential=token_credential,
            audience=f'https://badaudience.queue.core.windows.net'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        await queue.get_queue_properties()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

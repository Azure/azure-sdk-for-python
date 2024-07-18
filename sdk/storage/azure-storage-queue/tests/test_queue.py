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
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.queue import (
    AccessPolicy,
    AccountSasPermissions,
    generate_account_sas,
    generate_queue_sas,
    QueueClient,
    QueueSasPermissions,
    QueueServiceClient,
    ResourceTypes
)

from devtools_testutils import FakeTokenCredential, recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import QueuePreparer

# ------------------------------------------------------------------------------
TEST_QUEUE_PREFIX = 'pyqueuesync'


# ------------------------------------------------------------------------------

# pylint: disable=locally-disabled, multiple-statements, fixme, too-many-lines
class TestStorageQueue(StorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_queue_reference(self, qsc, prefix=TEST_QUEUE_PREFIX):
        queue_name = self.get_resource_name(prefix)
        queue = qsc.get_queue_client(queue_name)
        return queue

    def _create_queue(self, qsc, prefix=TEST_QUEUE_PREFIX, queue_list=None):
        queue = self._get_queue_reference(qsc, prefix)
        created = queue.create_queue()
        if queue_list is not None:
            queue_list.append(created)
        return queue

    # --Test cases for queues ----------------------------------------------
    @QueuePreparer()
    @recorded_by_proxy
    def test_create_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        created = queue_client.create_queue()

        # Asserts
        assert created

    @QueuePreparer()
    @recorded_by_proxy
    def test_create_queue_fail_on_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        created = queue_client.create_queue()
        with pytest.raises(ResourceExistsError):
            queue_client.create_queue()

        # Asserts
        assert created

    @QueuePreparer()
    @recorded_by_proxy
    def test_create_queue_fail_on_exist_different_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        url = self.account_url(storage_account_name, "queue")
        qsc = QueueServiceClient(url, storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        created = queue_client.create_queue()
        with pytest.raises(ResourceExistsError):
            queue_client.create_queue(metadata={"val": "value"})

        # Asserts
        assert created

    @QueuePreparer()
    @recorded_by_proxy
    def test_create_queue_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        url = self.account_url(storage_account_name, "queue")
        qsc = QueueServiceClient(url, storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue(
            metadata={'val1': 'test', 'val2': 'blah'})
        props = queue_client.get_queue_properties()

        # Asserts
        assert 0 == props.approximate_message_count
        assert 2 == len(props.metadata)
        assert 'test' == props.metadata['val1']
        assert 'blah' == props.metadata['val2']

    @QueuePreparer()
    @recorded_by_proxy
    def test_delete_non_existing_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)

        # Asserts
        with pytest.raises(ResourceNotFoundError):
            queue_client.delete_queue()

    @QueuePreparer()
    @recorded_by_proxy
    def test_delete_existing_queue_fail_not_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)

        created = queue_client.create_queue()
        deleted = queue_client.delete_queue()

        # Asserts
        assert deleted is None

    @QueuePreparer()
    @recorded_by_proxy
    def test_list_queues(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queues = list(qsc.list_queues())

        # Asserts
        assert queues is not None
        assert len(queues) >= 1

    @QueuePreparer()
    @recorded_by_proxy
    def test_list_queues_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        prefix = 'listqueue'
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_list = []
        for i in range(0, 4):
            self._create_queue(qsc, prefix + str(i), queue_list)

        # Action
        generator1 = qsc.list_queues(
            name_starts_with=prefix,
            results_per_page=3).by_page()
        queues1 = list(next(generator1))

        generator2 = qsc.list_queues(
            name_starts_with=prefix,
            include_metadata=True).by_page(generator1.continuation_token)
        queues2 = list(next(generator2))

        # Asserts
        assert queues1 is not None
        assert 3 == len(queues1)
        assert queues1[0] is not None
        assert queues1[0].metadata is None
        assert '' != queues1[0].name
        assert generator1.location_mode is not None
        # Asserts
        assert queues2 is not None
        assert len(queue_list) - 3 <= len(queues2)
        assert queues2[0] is not None
        assert '' != queues2[0].name

    @QueuePreparer()
    @recorded_by_proxy
    def test_list_queues_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._get_queue_reference(qsc)
        queue.create_queue()
        queue.set_queue_metadata(metadata={'val1': 'test', 'val2': 'blah'})

        listed_queue = list(qsc.list_queues(
            name_starts_with=queue.queue_name,
            results_per_page=1,
            include_metadata=True))[0]

        # Asserts
        assert listed_queue is not None
        assert queue.queue_name == listed_queue.name
        assert listed_queue.metadata is not None
        assert len(listed_queue.metadata) == 2
        assert listed_queue.metadata['val1'] == 'test'

    @QueuePreparer()
    @recorded_by_proxy
    def test_list_queues_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
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
        queues = list(qsc.list_queues())

        # Assert
        assert queues is not None
        assert len(queues) >= 1

    @QueuePreparer()
    @recorded_by_proxy
    def test_set_queue_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._get_queue_reference(qsc)
        metadata = {'hello': 'world', 'number': '43'}
        queue.create_queue()

        # Act
        queue.set_queue_metadata(metadata)
        metadata_from_response = queue.get_queue_properties().metadata
        # Assert
        assert metadata_from_response == metadata

    @QueuePreparer()
    @recorded_by_proxy
    def test_get_queue_metadata_message_count(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        sent_message = queue_client.send_message('message1')
        props = queue_client.get_queue_properties()

        # Asserts
        assert 'message1' == sent_message.content
        assert props.approximate_message_count >= 1
        assert 0 == len(props.metadata)

    @QueuePreparer()
    @recorded_by_proxy
    def test_queue_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = self._get_queue_reference(qsc)
        queue.create_queue()

        # Act
        exists = queue.get_queue_properties()

        # Assert
        assert exists

    @QueuePreparer()
    @recorded_by_proxy
    def test_queue_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue = qsc.get_queue_client(self.get_resource_name('missing'))
        # Act
        with pytest.raises(ResourceNotFoundError):
            queue.get_queue_properties()

        # Assert

    @QueuePreparer()
    @recorded_by_proxy
    def test_put_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action.  No exception means pass. No asserts needed.
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        message = queue_client.send_message('message4')

        # Asserts
        assert message is not None
        assert '' != message.id
        assert isinstance(message.inserted_on, datetime)
        assert isinstance(message.expires_on, datetime)
        assert '' != message.pop_receipt
        assert 'message4' == message.content

    @QueuePreparer()
    @recorded_by_proxy
    def test_put_message_large_time_to_live(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        # There should be no upper bound on a queue message's time to live
        queue_client.send_message('message1', time_to_live=1024 * 1024 * 1024)

        # Act
        messages = queue_client.peek_messages()

        # Assert
        assert messages[0].expires_on >= (messages[0].inserted_on + timedelta(seconds=1024 * 1024 * 1024 - 3600))

    @QueuePreparer()
    @recorded_by_proxy
    def test_put_message_infinite_time_to_live(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1', time_to_live=-1)

        # Act
        messages = queue_client.peek_messages()

        # Assert
        assert messages[0].expires_on.year == date.max.year

    @QueuePreparer()
    @recorded_by_proxy
    def test_get_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        message = next(queue_client.receive_messages())

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
    @recorded_by_proxy
    def test_receive_one_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        assert queue_client.receive_message() is None

        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')

        message1 = queue_client.receive_message()
        message2 = queue_client.receive_message()
        peeked_message3 = queue_client.peek_messages()[0]

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

        assert 'message3' == peeked_message3.content
        assert 0 == peeked_message3.dequeue_count

    @QueuePreparer()
    @recorded_by_proxy
    def test_get_messages_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        pager = queue_client.receive_messages(messages_per_page=4, visibility_timeout=20)
        result = list(pager)

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
    @recorded_by_proxy
    def test_get_messages_with_max_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        queue_client.send_message('message5')
        queue_client.send_message('message6')
        queue_client.send_message('message7')
        queue_client.send_message('message8')
        queue_client.send_message('message9')
        queue_client.send_message('message10')
        pager = queue_client.receive_messages(max_messages=5)
        result = list(pager)

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
    @recorded_by_proxy
    def test_get_messages_with_too_little_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        queue_client.send_message('message5')
        pager = queue_client.receive_messages(max_messages=10)
        result = list(pager)

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
    @recorded_by_proxy
    def test_get_messages_with_page_bigger_than_max(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        queue_client.send_message('message5')

        # Asserts
        with pytest.raises(ValueError):
            queue_client.receive_messages(messages_per_page=5, max_messages=2)

    @QueuePreparer()
    @recorded_by_proxy
    def test_get_messages_with_remainder(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        queue_client.send_message('message5')
        queue_client.send_message('message6')
        queue_client.send_message('message7')
        queue_client.send_message('message8')
        queue_client.send_message('message9')
        queue_client.send_message('message10')
        queue_client.send_message('message11')
        queue_client.send_message('message12')

        pager = queue_client.receive_messages(messages_per_page=3, max_messages=10)
        result = list(pager)

        remainder = queue_client.receive_messages()
        remainder_list = list(remainder)

        # Asserts
        assert result is not None
        assert 10 == len(result)

        assert remainder_list is not None
        assert 2 == len(remainder_list)

        for message in result:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert '' != message.pop_receipt
            assert 1 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert '' != message.next_visible_on

        for message in remainder_list:
            assert message is not None
            assert '' != message.id
            assert '' != message.content
            assert '' != message.pop_receipt
            assert 1 == message.dequeue_count
            assert '' != message.inserted_on
            assert '' != message.expires_on
            assert '' != message.next_visible_on

    @QueuePreparer()
    @recorded_by_proxy
    def test_peek_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        result = queue_client.peek_messages()

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
    @recorded_by_proxy
    def test_peek_messages_with_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        result = queue_client.peek_messages(max_messages=4)

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
    @recorded_by_proxy
    def test_clear_messages(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        queue_client.clear_messages()
        result = queue_client.peek_messages()

        # Asserts
        assert result is not None
        assert 0 == len(result)

    @QueuePreparer()
    @recorded_by_proxy
    def test_delete_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        queue_client.send_message('message2')
        queue_client.send_message('message3')
        queue_client.send_message('message4')
        message = next(queue_client.receive_messages())
        queue_client.delete_message(message)

        messages_pager = queue_client.receive_messages(messages_per_page=32)
        messages = list(messages_pager)

        # Asserts
        assert messages is not None
        assert len(messages) == 3

    @QueuePreparer()
    @recorded_by_proxy
    def test_update_message(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        messages = queue_client.receive_messages()
        list_result1 = next(messages)
        message = queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0)
        list_result2 = next(messages)

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
    @recorded_by_proxy
    def test_update_message_content(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')

        messages = queue_client.receive_messages()
        list_result1 = next(messages)
        message = queue_client.update_message(
            list_result1.id,
            pop_receipt=list_result1.pop_receipt,
            visibility_timeout=0,
            content='new text')
        list_result2 = next(messages)

        # Asserts
        # Update response
        assert message is not None
        assert message.pop_receipt is not None
        assert message.next_visible_on is not None
        assert isinstance(message.next_visible_on, datetime)
        assert 'new text' == message.content

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
    @recorded_by_proxy
    def test_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
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
            result = new_queue_client.peek_messages()

            # Assert
            assert result is not None
            assert 1 == len(result)
            message = result[0]
            assert message is not None
            assert '' != message.id
            assert 'message1' == message.content

    @QueuePreparer()
    @recorded_by_proxy
    def test_azure_named_key_credential_access(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        named_key = AzureNamedKeyCredential(storage_account_name, storage_account_key)
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), named_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')

        # Act
        result = queue_client.peek_messages()

        # Assert
        assert result is not None

    @QueuePreparer()
    def test_account_sas_raises_if_sas_already_in_uri(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        with pytest.raises(ValueError):
            QueueServiceClient(
                self.account_url(storage_account_name, "queue") + "?sig=foo",
                credential=AzureSasCredential("?foo=bar"))

    @pytest.mark.live_test_only
    @QueuePreparer()
    def test_token_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        token_credential = self.get_credential(QueueServiceClient)

        # Action 1: make sure token works
        service = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=token_credential)
        queues = service.get_service_properties()
        assert queues is not None

        # Action 2: change token value to make request fail
        fake_credential = FakeTokenCredential()
        service = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=fake_credential)
        with pytest.raises(ClientAuthenticationError):
            list(service.list_queues())

        # Action 3: update token to make it working again
        service = QueueServiceClient(self.account_url(storage_account_name, "queue"), credential=token_credential)
        queues = list(service.list_queues())
        assert queues is not None

    @QueuePreparer()
    @recorded_by_proxy
    def test_sas_read(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
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
        result = service.peek_messages()

        # Assert
        assert result is not None
        assert 1 == len(result)
        message = result[0]
        assert message is not None
        assert '' != message.id
        assert 'message1' == message.content

    @QueuePreparer()
    @recorded_by_proxy
    def test_sas_add(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
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
        result = service.send_message('addedmessage')

        # Assert
        result = next(queue_client.receive_messages())
        assert 'addedmessage' == result.content

    @QueuePreparer()
    @recorded_by_proxy
    def test_sas_update(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        token = self.generate_sas(
            generate_queue_sas,
            queue_client.account_name,
            queue_client.queue_name,
            queue_client.credential.account_key,
            QueueSasPermissions(update=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        messages = queue_client.receive_messages()
        result = next(messages)

        # Act
        service = QueueClient.from_queue_url(
            queue_url=queue_client.url,
            credential=token,
        )
        service.update_message(
            result.id,
            pop_receipt=result.pop_receipt,
            visibility_timeout=0,
            content='updatedmessage1',
        )

        # Assert
        result = next(messages)
        assert 'updatedmessage1' == result.content

    @QueuePreparer()
    @recorded_by_proxy
    def test_sas_process(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
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
        message = next(service.receive_messages())

        # Assert
        assert message is not None
        assert '' != message.id
        assert 'message1' == message.content

    @QueuePreparer()
    @recorded_by_proxy
    def test_sas_signed_identifier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop('variables', {})

        # Arrange
        access_policy = AccessPolicy()
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow() - timedelta(hours=1))
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        access_policy.start = start_time
        access_policy.expiry = expiry_time
        access_policy.permission = QueueSasPermissions(read=True)

        identifiers = {'testid': access_policy}

        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        resp = queue_client.set_queue_access_policy(identifiers)

        queue_client.send_message('message1')

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
        result = service.peek_messages()

        # Assert
        assert result is not None
        assert 1 == len(result)
        message = result[0]
        assert message is not None
        assert '' != message.id
        assert 'message1' == message.content

        return variables

    @QueuePreparer()
    @recorded_by_proxy
    def test_get_queue_acl(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()

        # Act
        acl = queue_client.get_queue_access_policy()

        # Assert
        assert acl is not None
        assert len(acl) == 0

    @QueuePreparer()
    @recorded_by_proxy
    def test_get_queue_acl_iter(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()

        # Act
        acl = queue_client.get_queue_access_policy()
        for signed_identifier in acl:
            pass

        # Assert
        assert acl is not None
        assert len(acl) == 0

    @QueuePreparer()
    @recorded_by_proxy
    def test_get_queue_acl_with_non_existing_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)

        # Act
        with pytest.raises(ResourceNotFoundError):
            queue_client.get_queue_access_policy()

            # Assert

    @QueuePreparer()
    @recorded_by_proxy
    def test_set_queue_acl(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()

        # Act
        resp = queue_client.set_queue_access_policy(signed_identifiers=dict())

        # Assert
        assert resp is None
        acl = queue_client.get_queue_access_policy()
        assert acl is not None

    @QueuePreparer()
    @recorded_by_proxy
    def test_set_queue_acl_with_empty_signed_identifiers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()

        # Act
        queue_client.set_queue_access_policy(signed_identifiers={})

        # Assert
        acl = queue_client.get_queue_access_policy()
        assert acl is not None
        assert len(acl) == 0

    @QueuePreparer()
    @recorded_by_proxy
    def test_set_queue_acl_with_empty_signed_identifier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()

        # Act
        queue_client.set_queue_access_policy(signed_identifiers={'empty': None})

        # Assert
        acl = queue_client.get_queue_access_policy()
        assert acl is not None
        assert len(acl) == 1
        assert acl['empty'] is not None
        assert acl['empty'].permission is None
        assert acl['empty'].expiry is None
        assert acl['empty'].start is None

    @QueuePreparer()
    @recorded_by_proxy
    def test_set_queue_acl_with_signed_identifiers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop('variables', {})

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()

        # Act
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow() - timedelta(minutes=5))
        access_policy = AccessPolicy(permission=QueueSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        identifiers = {'testid': access_policy}

        resp = queue_client.set_queue_access_policy(signed_identifiers=identifiers)

        # Assert
        assert resp is None
        acl = queue_client.get_queue_access_policy()
        assert acl is not None
        assert len(acl) == 1
        assert 'testid' in acl

        return variables

    @QueuePreparer()
    @recorded_by_proxy
    def test_set_queue_acl_too_many_ids(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()

        # Act
        identifiers = dict()
        for i in range(0, 16):
            identifiers[f'id{i}'] = AccessPolicy()

        # Assert
        with pytest.raises(ValueError):
            queue_client.set_queue_access_policy(identifiers)

    @QueuePreparer()
    @recorded_by_proxy
    def test_set_queue_acl_with_non_existing_queue(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)

        # Act
        with pytest.raises(ResourceNotFoundError):
            queue_client.set_queue_access_policy(signed_identifiers=dict())

            # Assert

    @QueuePreparer()
    @recorded_by_proxy
    def test_unicode_create_queue_unicode_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_name = '啊齄丂狛狜'

        with pytest.raises(HttpResponseError):
            # not supported - queue name must be alphanumeric, lowercase
            client = qsc.get_queue_client(queue_name)
            client.create_queue()

            # Asserts

    @QueuePreparer()
    @recorded_by_proxy
    def test_unicode_get_messages_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1㚈')
        message = next(queue_client.receive_messages())

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
    @recorded_by_proxy
    def test_unicode_update_message_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Action
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        queue_client = self._get_queue_reference(qsc)
        queue_client.create_queue()
        queue_client.send_message('message1')
        messages = queue_client.receive_messages()

        list_result1 = next(messages)
        list_result1.content = '啊齄丂狛狜'
        queue_client.update_message(list_result1, visibility_timeout=0)

        # Asserts
        message = next(messages)
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
    def test_transport_closed_only_once(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = RequestsTransport()
        prefix = TEST_QUEUE_PREFIX
        queue_name = self.get_resource_name(prefix)
        with QueueServiceClient(
                self.account_url(storage_account_name, "queue"),
                credential=storage_account_key, transport=transport) as qsc:
            qsc.get_service_properties()
            assert transport.session is not None
            with qsc.get_queue_client(queue_name) as qc:
                assert transport.session is not None
            qsc.get_service_properties()
            assert transport.session is not None

    @QueuePreparer()
    @recorded_by_proxy
    def test_storage_account_audience_queue_service_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.get_service_properties()

        # Act
        token_credential = self.get_credential(QueueServiceClient)
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"), credential=token_credential,
            audience=f'https://{storage_account_name}.queue.core.windows.net'
        )

        # Assert
        response = qsc.get_service_properties()
        assert response is not None

    @QueuePreparer()
    @recorded_by_proxy
    def test_bad_audience_queue_service_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        qsc.get_service_properties()

        # Act
        token_credential = self.get_credential(QueueServiceClient)
        qsc = QueueServiceClient(
            self.account_url(storage_account_name, "queue"), credential=token_credential,
            audience=f'https://badaudience.queue.core.windows.net'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        qsc.get_service_properties()

    @QueuePreparer()
    @recorded_by_proxy
    def test_storage_account_audience_queue_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        queue = QueueClient(self.account_url(storage_account_name, "queue"), 'testqueue1', storage_account_key)
        queue.create_queue()

        # Act
        token_credential = self.get_credential(QueueServiceClient)
        queue = QueueClient(
            self.account_url(storage_account_name, "queue"), 'testqueue1', credential=token_credential,
            audience=f'https://{storage_account_name}.queue.core.windows.net'
        )

        # Assert
        response = queue.get_queue_properties()
        assert response is not None

    @QueuePreparer()
    @recorded_by_proxy
    def test_bad_audience_queue_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        queue = QueueClient(self.account_url(storage_account_name, "queue"), 'testqueue2', storage_account_key)
        queue.create_queue()

        # Act
        token_credential = self.get_credential(QueueServiceClient)
        queue = QueueClient(
            self.account_url(storage_account_name, "queue"), 'testqueue2', credential=token_credential,
            audience=f'https://badaudience.queue.core.windows.net'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        queue.get_queue_properties()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

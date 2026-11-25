# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from unittest.mock import AsyncMock, Mock

import pytest

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub._constants import ALL_PARTITIONS, MAX_MESSAGE_LENGTH_BYTES

MB = 1024 * 1024


# shadows conftest's autouse amqpproxy, which skips without a live Event Hub
@pytest.fixture(autouse=True)
def amqpproxy():
    yield


def _client_with_remote_max_message_size(remote):
    client = EventHubProducerClient("fake.host.com", "fake_eh", None)
    inner = client._producers[ALL_PARTITIONS]
    inner._open_with_retry = AsyncMock()
    inner._handler = Mock()
    inner._handler._link.remote_max_message_size = remote
    return client


@pytest.mark.asyncio
async def test_create_batch_uses_remote_max_message_size_async():
    client = _client_with_remote_max_message_size(20 * MB)

    batch = await client.create_batch()
    assert batch.max_size_in_bytes == 20 * MB
    batch.add(EventData(b"a" * (2 * MB)))
    assert batch.size_in_bytes > MB

    assert (await client.create_batch(max_size_in_bytes=5 * MB)).max_size_in_bytes == 5 * MB
    await client.create_batch(max_size_in_bytes=20 * MB)
    with pytest.raises(ValueError):
        await client.create_batch(max_size_in_bytes=20 * MB + 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("remote", [None, 0])
async def test_create_batch_falls_back_to_1mb_async(remote):
    client = _client_with_remote_max_message_size(remote)

    assert (await client.create_batch()).max_size_in_bytes == MAX_MESSAGE_LENGTH_BYTES
    with pytest.raises(ValueError):
        await client.create_batch(max_size_in_bytes=MB + 1)

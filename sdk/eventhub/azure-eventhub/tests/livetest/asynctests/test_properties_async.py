# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import pytest

from azure.eventhub.aio import (
    EventHubConsumerClient,
    EventHubSharedKeyCredential,
)
from azure.eventhub.exceptions import AuthenticationError, ConnectError


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_get_properties(auth_credentials_async, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials_async
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    async with client:
        properties = await client.get_eventhub_properties()
        assert properties["eventhub_name"] == eventhub_name and properties["partition_ids"] == ["0", "1"]


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_get_properties_with_auth_error_async(auth_credentials_async, live_eventhub, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, _ = auth_credentials_async
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=EventHubSharedKeyCredential(live_eventhub["key_name"], "AaBbCcDdEeFf="),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    async with client:
        with pytest.raises(AuthenticationError) as e:
            await client.get_eventhub_properties()

    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=EventHubSharedKeyCredential("invalid", live_eventhub["access_key"]),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    async with client:
        with pytest.raises(AuthenticationError) as e:
            await client.get_eventhub_properties()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_get_properties_with_connect_error(auth_credentials_async, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials_async
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name="invalid",
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    async with client:
        with pytest.raises(ConnectError) as e:
            await client.get_eventhub_properties()

    client = EventHubConsumerClient(
        fully_qualified_namespace="invalid.servicebus.windows.net",
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    async with client:
        with pytest.raises(ConnectError) as e:
            await client.get_eventhub_properties()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_get_partition_ids(auth_credentials_async, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials_async
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    async with client:
        partition_ids = await client.get_partition_ids()
        assert partition_ids == ["0", "1"]


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_get_partition_properties(auth_credentials_async, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials_async
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    async with client:
        properties = await client.get_partition_properties("0")
        assert (
            properties["eventhub_name"] == eventhub_name
            and properties["id"] == "0"
            and "beginning_sequence_number" in properties
            and "last_enqueued_sequence_number" in properties
            and "last_enqueued_offset" in properties
            and "last_enqueued_time_utc" in properties
            and "is_empty" in properties
        )

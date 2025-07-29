# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import pytest

from azure.eventhub import EventHubSharedKeyCredential
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.exceptions import (
    AuthenticationError,
    ConnectError,
)


@pytest.mark.liveTest
def test_get_properties(auth_credentials, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    with client:
        properties = client.get_eventhub_properties()
        assert properties["eventhub_name"] == eventhub_name and properties["partition_ids"] == ["0", "1"]


@pytest.mark.liveTest
def test_get_properties_with_auth_error_sync(auth_credentials, live_eventhub, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, _ = auth_credentials
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=EventHubSharedKeyCredential(live_eventhub["key_name"], "AaBbCcDdEeFf="),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    with client:
        with pytest.raises(AuthenticationError) as e:
            client.get_eventhub_properties()

    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=EventHubSharedKeyCredential("invalid", live_eventhub["access_key"]),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    with client:
        with pytest.raises(AuthenticationError) as e:
            client.get_eventhub_properties()


@pytest.mark.liveTest
def test_get_properties_with_connect_error(auth_credentials, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name="invalid",
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    with client:
        with pytest.raises(ConnectError) as e:
            client.get_eventhub_properties()

    client = EventHubConsumerClient(
        fully_qualified_namespace="invalid.servicebus.windows.net",
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    with client:
        with pytest.raises(ConnectError) as e:
            client.get_eventhub_properties()


@pytest.mark.liveTest
def test_get_partition_ids(auth_credentials, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        **client_args,
    )
    with client:
        partition_ids = client.get_partition_ids()
        assert partition_ids == ["0", "1"]


@pytest.mark.liveTest
def test_get_partition_properties(auth_credentials, uamqp_transport, client_args):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group="$default",
        credential=credential(),
        uamqp_transport=uamqp_transport,
        client_args=client_args,
    )
    with client:
        properties = client.get_partition_properties("0")
        assert (
            properties["eventhub_name"] == eventhub_name
            and properties["id"] == "0"
            and "beginning_sequence_number" in properties
            and "last_enqueued_sequence_number" in properties
            and "last_enqueued_offset" in properties
            and "last_enqueued_time_utc" in properties
            and "is_empty" in properties
        )

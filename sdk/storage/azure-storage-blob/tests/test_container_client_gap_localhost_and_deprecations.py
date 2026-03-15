# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from unittest.mock import Mock, patch

from azure.storage.blob import BlobProperties, BlobType, ContainerClient, StandardBlobTier


LOCALHOST_CONNECTION_STRING = "UseDevelopmentStorage=true;"


def _create_container_client():
    return ContainerClient(
        "https://fakename.blob.core.windows.net",
        "container",
        credential="fake_key"
    )


def _create_localhost_container_client():
    return ContainerClient.from_connection_string(
        LOCALHOST_CONNECTION_STRING,
        container_name="container"
    )


def test_upload_blob_when_name_is_blob_properties_warns_and_uploads():
    container = _create_container_client()
    blob_properties = BlobProperties()
    blob_client = Mock()

    with patch.object(container, "get_blob_client", return_value=blob_client) as get_blob_client:
        with pytest.warns(DeprecationWarning) as warning:
            returned = container.upload_blob(blob_properties, b"hello", overwrite=True)

    assert str(warning[0].message) == (
        "The use of a 'BlobProperties' instance for param name is deprecated. "
        "Please use 'BlobProperties.name' or any other str input type instead."
    )
    assert returned is blob_client
    get_blob_client.assert_called_once_with(blob_properties)
    assert blob_client.upload_blob.call_count == 1
    assert blob_client.upload_blob.call_args.args == (b"hello",)
    assert blob_client.upload_blob.call_args.kwargs["blob_type"] == BlobType.BLOCKBLOB
    assert blob_client.upload_blob.call_args.kwargs["length"] is None
    assert blob_client.upload_blob.call_args.kwargs["metadata"] is None
    assert blob_client.upload_blob.call_args.kwargs["timeout"] is None
    assert blob_client.upload_blob.call_args.kwargs["encoding"] == "UTF-8"
    assert blob_client.upload_blob.call_args.kwargs["overwrite"] is True
    assert blob_client.upload_blob.call_args.kwargs["merge_span"] is True


def test_delete_blob_when_blob_is_blob_properties_warns_and_deletes_blob():
    container = _create_container_client()
    blob_properties = BlobProperties()
    blob_client = Mock()

    with patch.object(container, "get_blob_client", return_value=blob_client) as get_blob_client:
        with pytest.warns(DeprecationWarning) as warning:
            result = container.delete_blob(blob_properties, delete_snapshots="include", lease="lease-id")

    assert str(warning[0].message) == (
        "The use of a 'BlobProperties' instance for param blob is deprecated. "
        "Please use 'BlobProperties.name' or any other str input type instead."
    )
    assert result is None
    get_blob_client.assert_called_once_with(blob_properties)
    blob_client.delete_blob.assert_called_once_with(
        delete_snapshots="include",
        timeout=None,
        lease="lease-id",
        merge_span=True
    )


def test_delete_blobs_when_client_is_localhost_passes_url_prepend_to_helper():
    container = _create_localhost_container_client()

    with patch(
        "azure.storage.blob._container_client._generate_delete_blobs_options",
        return_value=(["request"], {"marker": "value"})
    ) as generate_delete_options, patch.object(
        container,
        "_batch_send",
        return_value=iter(["deleted"])
    ) as batch_send:
        responses = list(container.delete_blobs("blob1"))

    assert container._is_localhost is True
    assert responses == ["deleted"]
    assert generate_delete_options.call_args.args[0] == container._query_str
    assert generate_delete_options.call_args.args[1] == container.container_name
    assert generate_delete_options.call_args.args[3] == "blob1"
    assert generate_delete_options.call_args.kwargs["url_prepend"] == container.account_name
    batch_send.assert_called_once_with("request", marker="value")


def test_set_standard_blob_tier_blobs_when_client_is_localhost_passes_url_prepend_to_helper():
    container = _create_localhost_container_client()

    with patch(
        "azure.storage.blob._container_client._generate_set_tiers_options",
        return_value=(["request"], {"marker": "value"})
    ) as generate_set_tiers_options, patch.object(
        container,
        "_batch_send",
        return_value=iter(["tiered"])
    ) as batch_send:
        responses = list(container.set_standard_blob_tier_blobs(StandardBlobTier.HOT, "blob1"))

    assert container._is_localhost is True
    assert responses == ["tiered"]
    assert generate_set_tiers_options.call_args.args[0] == container._query_str
    assert generate_set_tiers_options.call_args.args[1] == container.container_name
    assert generate_set_tiers_options.call_args.args[2] == StandardBlobTier.HOT
    assert generate_set_tiers_options.call_args.args[4] == "blob1"
    assert generate_set_tiers_options.call_args.kwargs["url_prepend"] == container.account_name
    batch_send.assert_called_once_with("request", marker="value")


def test_set_standard_blob_tier_blobs_when_batch_send_returns_iterator_returns_batch_send_results():
    container = _create_container_client()

    with patch(
        "azure.storage.blob._container_client._generate_set_tiers_options",
        return_value=(["request1", "request2"], {"raise_on_any_failure": False, "marker": "value"})
    ) as generate_set_tiers_options, patch.object(
        container,
        "_batch_send",
        return_value=iter(["response1", "response2"])
    ) as batch_send:
        responses = list(container.set_standard_blob_tier_blobs(StandardBlobTier.COOL, "blob1", "blob2"))

    assert container._is_localhost is False
    assert responses == ["response1", "response2"]
    assert generate_set_tiers_options.call_args.args[0] == container._query_str
    assert generate_set_tiers_options.call_args.args[1] == container.container_name
    assert generate_set_tiers_options.call_args.args[2] == StandardBlobTier.COOL
    assert generate_set_tiers_options.call_args.args[4:] == ("blob1", "blob2")
    assert "url_prepend" not in generate_set_tiers_options.call_args.kwargs
    batch_send.assert_called_once_with(
        "request1",
        "request2",
        raise_on_any_failure=False,
        marker="value"
    )

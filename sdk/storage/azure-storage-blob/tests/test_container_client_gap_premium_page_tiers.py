# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest.mock import patch

from azure.storage.blob import ContainerClient, PremiumPageBlobTier
from azure.storage.blob._shared.parser import DEVSTORE_ACCOUNT_NAME


def test_set_premium_page_blob_tier_blobs_when_client_is_localhost_passes_url_prepend_to_helper():
    client = ContainerClient.from_connection_string("UseDevelopmentStorage=true;", container_name="container")
    assert client._is_localhost is True

    with patch("azure.storage.blob._container_client._generate_set_tiers_options") as generate_options, \
            patch.object(client, "_batch_send", return_value=iter(["response"])) as batch_send:
        generate_options.return_value = (["request"], {"raise_on_any_failure": True})

        result = client.set_premium_page_blob_tier_blobs(PremiumPageBlobTier.P4, "blob1")

    assert list(result) == ["response"]
    generate_options.assert_called_once()
    args, kwargs = generate_options.call_args
    assert args[0] == client._query_str
    assert args[1] == client.container_name
    assert args[2] == PremiumPageBlobTier.P4
    assert args[3] is client._client
    assert args[4] == "blob1"
    assert kwargs["url_prepend"] == DEVSTORE_ACCOUNT_NAME
    batch_send.assert_called_once_with("request", raise_on_any_failure=True)


def test_set_premium_page_blob_tier_blobs_when_batch_send_returns_iterator_returns_batch_send_results():
    client = ContainerClient("https://storagename.blob.core.windows.net", "container")
    assert client._is_localhost is False

    with patch(
        "azure.storage.blob._container_client._generate_set_tiers_options",
        return_value=(["request1", "request2"], {"timeout": 7, "raise_on_any_failure": False})
    ) as generate_options, patch.object(
        client,
        "_batch_send",
        return_value=iter(["response1", "response2"])
    ) as batch_send:
        result = client.set_premium_page_blob_tier_blobs(PremiumPageBlobTier.P6, "blob1", "blob2")

    assert list(result) == ["response1", "response2"]
    generate_options.assert_called_once_with(
        client._query_str,
        client.container_name,
        PremiumPageBlobTier.P6,
        client._client,
        "blob1",
        "blob2"
    )
    batch_send.assert_called_once_with("request1", "request2", timeout=7, raise_on_any_failure=False)

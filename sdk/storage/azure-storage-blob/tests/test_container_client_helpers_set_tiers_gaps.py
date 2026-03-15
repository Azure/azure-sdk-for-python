# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from urllib.parse import parse_qs, urlparse

from azure.storage.blob import ContainerClient, RehydratePriority, StandardBlobTier
from azure.storage.blob._container_client_helpers import _generate_set_tiers_options



def _get_generated_client():
    container_client = ContainerClient(
        "https://fakename.blob.core.windows.net",
        "container",
        credential="fake_key"
    )
    return container_client._client



def test_generate_set_tiers_options_when_top_level_rehydrate_priority_provided_adds_header_for_string_blob():
    client = _get_generated_client()

    reqs, _ = _generate_set_tiers_options(
        "?sig=abc",
        "container",
        StandardBlobTier.Archive,
        client,
        "blob",
        rehydrate_priority=RehydratePriority.high
    )

    assert len(reqs) == 1
    assert reqs[0].headers["x-ms-access-tier"] == StandardBlobTier.Archive
    assert reqs[0].headers["x-ms-rehydrate-priority"] == RehydratePriority.high



def test_generate_set_tiers_options_when_top_level_if_tags_match_condition_provided_adds_tags_header_for_string_blob():
    client = _get_generated_client()
    if_tags_match_condition = '"tag1"=\'value1\''

    reqs, _ = _generate_set_tiers_options(
        "?sig=abc",
        "container",
        StandardBlobTier.Cool,
        client,
        "blob",
        if_tags_match_condition=if_tags_match_condition
    )

    assert len(reqs) == 1
    assert reqs[0].headers["x-ms-access-tier"] == StandardBlobTier.Cool
    assert reqs[0].headers["x-ms-if-tags"] == if_tags_match_condition



def test_generate_set_tiers_options_when_url_prepend_provided_prefixes_request_url():
    client = _get_generated_client()

    reqs, _ = _generate_set_tiers_options(
        "?sig=abc",
        "container",
        StandardBlobTier.Hot,
        client,
        "blob",
        url_prepend="batchprefix"
    )

    parsed_url = urlparse(reqs[0].url)

    assert parsed_url.path == "/batchprefix/container/blob"
    assert parse_qs(parsed_url.query) == {"sig": ["abc"], "comp": ["tier"]}



def test_generate_set_tiers_options_when_timeout_provided_updates_batch_options_with_defaults():
    client = _get_generated_client()

    reqs, batch_options = _generate_set_tiers_options(
        "?sig=abc",
        "container",
        StandardBlobTier.Cool,
        client,
        "blob",
        timeout=12,
        custom_option="value"
    )

    assert len(reqs) == 1
    assert batch_options == {
        "custom_option": "value",
        "raise_on_any_failure": True,
        "sas": "&sig=abc",
        "timeout": "&timeout=12",
        "path": "container",
        "restype": "restype=container&"
    }



def test_generate_set_tiers_options_when_multiple_blobs_provided_returns_put_requests_in_order():
    client = _get_generated_client()

    reqs, _ = _generate_set_tiers_options(
        "?sig=abc",
        "container",
        StandardBlobTier.Hot,
        client,
        "first-blob",
        {"name": "second-blob"}
    )

    first_url = urlparse(reqs[0].url)
    second_url = urlparse(reqs[1].url)

    assert len(reqs) == 2
    assert [req.method for req in reqs] == ["PUT", "PUT"]
    assert first_url.path == "/container/first-blob"
    assert second_url.path == "/container/second-blob"
    assert parse_qs(first_url.query) == {"sig": ["abc"], "comp": ["tier"]}
    assert parse_qs(second_url.query) == {"sig": ["abc"], "comp": ["tier"]}

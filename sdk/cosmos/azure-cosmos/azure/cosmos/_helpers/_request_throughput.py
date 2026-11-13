# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure account-level offer request builders shared by sync and async callers."""

from __future__ import annotations

from typing import Any, Mapping

from .._backend.partition_key_input import BindingPartitionKey
from .._backend.contracts import PreparedRequest
from .._backend.operations import OP_GET_THROUGHPUT, OP_REPLACE_THROUGHPUT
from .._base import GetResourceIdOrFullNameFromLink, TrimBeginningAndEndingSlashes
from ._wire_encoding import serialize_body_to_bytes
from ._request_settings import prepare_service_request_settings


def build_get_throughput_request(
    *,
    resource_link: str,
    offer_query: Mapping[str, Any],
    request_options: Mapping[str, Any],
    default_headers: Mapping[str, Any],
) -> PreparedRequest:
    """Build a prepared request to find the offer; do not execute its query."""
    headers, settings = prepare_service_request_settings(
        request_options, default_headers, resource_type="offers"
    )
    return PreparedRequest(
        op=OP_GET_THROUGHPUT,
        container_link=TrimBeginningAndEndingSlashes(resource_link),
        body_bytes=serialize_body_to_bytes(dict(offer_query)),
        partition_key=BindingPartitionKey("cross_partition"),
        headers=headers,
        settings=settings,
    )


def build_replace_throughput_request(
    *,
    resource_link: str,
    offer_body: Mapping[str, Any],
    request_options: Mapping[str, Any],
    default_headers: Mapping[str, Any],
) -> PreparedRequest:
    """Build a replacement request targeting the offer id parsed from its self-link."""
    offer_id = GetResourceIdOrFullNameFromLink(offer_body["_self"])
    headers, settings = prepare_service_request_settings(
        request_options, default_headers, resource_type="offers"
    )
    return PreparedRequest(
        op=OP_REPLACE_THROUGHPUT,
        container_link=TrimBeginningAndEndingSlashes(resource_link),
        item_id=offer_id,
        body_bytes=serialize_body_to_bytes(dict(offer_body)),
        partition_key=BindingPartitionKey("cross_partition"),
        headers=headers,
        settings=settings,
    )

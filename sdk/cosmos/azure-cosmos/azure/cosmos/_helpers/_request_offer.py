# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Pure account-level offer request builders shared by sync and async callers."""

from __future__ import annotations

from .._backend.partition_key import PartitionKeyInput

from typing import Any, Mapping

from .._backend.contracts import PreparedRequest
from .._backend.operations import OP_READ_OFFER, OP_REPLACE_OFFER
from .._base import GetResourceIdOrFullNameFromLink, TrimBeginningAndEndingSlashes
from ._wire_encoding import serialize_body_to_bytes
from ._request_settings import prepare_service_request_settings


def build_read_offer_request(
    *,
    resource_link: str,
    offer_query: Mapping[str, Any],
    request_options: Mapping[str, Any],
    default_headers: Mapping[str, Any],
) -> PreparedRequest:
    """Find the database/container offer using its existing normalized query."""
    headers, settings = prepare_service_request_settings(request_options, default_headers, resource_type="offers")
    return PreparedRequest(
        op=OP_READ_OFFER,
        container_link=TrimBeginningAndEndingSlashes(resource_link),
        body_bytes=serialize_body_to_bytes(dict(offer_query)),
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
    )


def build_replace_offer_request(
    *,
    resource_link: str,
    offer_body: Mapping[str, Any],
    request_options: Mapping[str, Any],
    default_headers: Mapping[str, Any],
) -> PreparedRequest:
    """Replace the offer RID from its self-link, not the owning resource RID."""
    offer_id = GetResourceIdOrFullNameFromLink(offer_body["_self"])
    headers, settings = prepare_service_request_settings(request_options, default_headers, resource_type="offers")
    return PreparedRequest(
        op=OP_REPLACE_OFFER,
        container_link=TrimBeginningAndEndingSlashes(resource_link),
        item_id=offer_id,
        body_bytes=serialize_body_to_bytes(dict(offer_body)),
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
    )

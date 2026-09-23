# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared item requests from body bytes, partition keys, and request options.

These builders do not send requests. For a read, "order-42" and "customer-17"
become the item id and typed partition-key input on PreparedRequest. For a
write without an explicit partition key, the record asks the binding to
extract the key from the body.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, Mapping, Optional

from .._backend.contracts import PreparedRequest
from .._backend.operations import (
    OP_CREATE_ITEM, OP_DELETE_ITEM, OP_PATCH_ITEM, OP_READ_ITEM,
    OP_REPLACE_ITEM, OP_UPSERT_ITEM,
)
from .._backend.partition_key_input import BindingPartitionKey
from .._backend.request_settings import RequestSettings
from ._request_settings import (
    stamp_container_rid,
    apply_no_response_on_write_default,
    build_request_headers_and_settings,
)
from ._document import SerializedDocument
from ._partition_key import normalize_partition_key


def _build_item_headers_and_settings(
    request_options: Mapping[str, Any],
    container_rid: Optional[str],
    no_response_on_write_default: bool = False,
) -> tuple[Dict[str, str], RequestSettings]:
    options = dict(request_options)
    apply_no_response_on_write_default(options, no_response_on_write_default)
    if container_rid is not None:
        stamp_container_rid(options, container_rid)
    headers, settings = build_request_headers_and_settings(options)
    if container_rid is not None:
        # The resolved container id wins over a customer-supplied header value.
        headers.pop("x-ms-cosmos-intended-collection-rid", None)
        settings = replace(settings, resource=replace(settings.resource, container_rid=container_rid))
    return headers, settings


def build_create_item_request(
    *,
    container_link: str,
    document: SerializedDocument,
    partition_key_value: Any,
    container_rid: Optional[str],
    request_options: Mapping[str, Any],
    indexing_directive: Optional[Any] = None,
    no_response_on_write_default: bool = False,
    extract_partition_key: bool = False,
) -> PreparedRequest:
    """Build a prepared request with an explicit key or a binding extraction instruction."""
    options = dict(request_options)
    if indexing_directive is not None:
        options["indexingDirective"] = indexing_directive
    return _build_write_prepared(
        op=OP_CREATE_ITEM,
        container_link=container_link,
        body_bytes=document.body_bytes,
        item_id=document.body_id,
        partition_key_value=partition_key_value,
        container_rid=container_rid,
        request_options=options,
        no_response_on_write_default=no_response_on_write_default,
        extract_partition_key=extract_partition_key,
    )


def build_delete_item_request(
    *,
    container_link: str,
    item_id: str,
    partition_key_value: Any,
    container_rid: Optional[str],
    request_options: Mapping[str, Any],
) -> PreparedRequest:
    """Build a delete using normalized options and resolved target/key metadata."""
    headers, settings = _build_item_headers_and_settings(request_options, container_rid)
    return PreparedRequest(
        op=OP_DELETE_ITEM,
        container_link=container_link,
        body_bytes=b"",
        partition_key=normalize_partition_key(partition_key_value),
        headers=headers,
        settings=settings,
        item_id=item_id,
    )


def build_read_item_request(
    *,
    container_link: str,
    item_id: str,
    partition_key_value: Any,
    container_rid: Optional[str],
    request_options: Mapping[str, Any],
) -> PreparedRequest:
    """Build a read, preserving conditions and cache staleness."""
    headers, settings = _build_item_headers_and_settings(request_options, container_rid)
    return PreparedRequest(
        op=OP_READ_ITEM,
        container_link=container_link,
        body_bytes=b"",
        partition_key=normalize_partition_key(partition_key_value),
        headers=headers,
        settings=settings,
        item_id=item_id,
    )


def _build_write_prepared(
    *,
    op: str,
    container_link: str,
    body_bytes: bytes,
    partition_key_value: Any,
    container_rid: Optional[str],
    request_options: Mapping[str, Any],
    item_id: Optional[str] = None,
    no_response_on_write_default: bool = False,
    extract_partition_key: bool = False,
) -> PreparedRequest:
    """Package a write without inspecting or reserializing its body bytes."""
    headers, settings = _build_item_headers_and_settings(
        request_options, container_rid, no_response_on_write_default
    )
    return PreparedRequest(
        op=op,
        container_link=container_link,
        body_bytes=body_bytes,
        partition_key=BindingPartitionKey("extract") if extract_partition_key else normalize_partition_key(partition_key_value),
        headers=headers,
        settings=settings,
        item_id=item_id,
    )


def build_upsert_item_request(
    *,
    container_link: str,
    document: SerializedDocument,
    partition_key_value: Any,
    container_rid: Optional[str],
    request_options: Mapping[str, Any],
    no_response_on_write_default: bool = False,
    extract_partition_key: bool = False,
) -> PreparedRequest:
    """Build an upsert; the already-present body id identifies the target."""
    return _build_write_prepared(
        op=OP_UPSERT_ITEM, container_link=container_link,
        body_bytes=document.body_bytes, item_id=document.body_id,
        partition_key_value=partition_key_value, container_rid=container_rid,
        request_options=request_options,
        no_response_on_write_default=no_response_on_write_default,
        extract_partition_key=extract_partition_key,
    )


def build_replace_item_request(
    *,
    container_link: str,
    document: SerializedDocument,
    item_id: str,
    partition_key_value: Any,
    container_rid: Optional[str],
    request_options: Mapping[str, Any],
    no_response_on_write_default: bool = False,
    extract_partition_key: bool = False,
    item_self_link: Optional[str] = None,
) -> PreparedRequest:
    """Preserve a returned resource address; otherwise use the explicit target ID."""
    prepared = _build_write_prepared(
        op=OP_REPLACE_ITEM, container_link=container_link, body_bytes=document.body_bytes, item_id=item_id,
        partition_key_value=partition_key_value, container_rid=container_rid,
        request_options=request_options,
        no_response_on_write_default=no_response_on_write_default,
        extract_partition_key=extract_partition_key,
    )
    return replace(prepared, item_self_link=item_self_link)


def build_patch_item_request(
    *,
    container_link: str,
    item_id: str,
    body_bytes: bytes,
    partition_key_value: Any,
    container_rid: Optional[str],
    request_options: Mapping[str, Any],
    no_response_on_write_default: bool = False,
) -> PreparedRequest:
    """Build a patch with a caller If-Match guard."""
    return _build_write_prepared(
        op=OP_PATCH_ITEM,
        container_link=container_link,
        body_bytes=body_bytes,
        partition_key_value=partition_key_value,
        container_rid=container_rid,
        request_options=request_options,
        no_response_on_write_default=no_response_on_write_default,
        item_id=item_id,
    )

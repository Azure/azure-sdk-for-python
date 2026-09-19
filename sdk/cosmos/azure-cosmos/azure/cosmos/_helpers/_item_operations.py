# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Turning item calls into requests, and replies back into results.

This file covers the six single-item operations: create, read, replace,
upsert, patch, and delete. Everything here is local work. Nothing in this
file opens a connection or waits on a reply; sending is the backend's job.

A call moves through four steps, in this order:

1. Tidy up the caller's keyword arguments and split them into the values a
   request needs and the options that shape it.
2. Reject anything the Rust path cannot honor, naming what to remove.
3. Build the request object for this particular operation.
4. Hand it to the backend, then turn the reply into the caller's result.

Which path a client uses was settled earlier, up in the container class.
By the time this helper exists the choice is made, so nothing here inspects
it, and there is no route back to the legacy Python code from this file.

The async version in azure/cosmos/aio/_helpers/_item_operations.py makes the
same decisions in the same order, and imports steps 1 to 3 from here rather
than repeating them.
"""
from __future__ import annotations

import warnings
from copy import deepcopy
from typing import Any, Dict, Optional

from .._backend.cosmos_backend import CosmosBackend
from .._backend.contracts import BackendResponse, PreparedRequest
from ..partition_key import (
    _Empty, NonePartitionKeyValue, NullPartitionKeyValue,
    _return_undefined_or_empty_partition_key,
)
from . import _request_item
from ._item_context import ItemClientDefaults, ClientLastResponseHeaders
from ._request_settings import compose_item_options, _timeout_is_representable, overrides_driver_owned_header
from ._item_prep import (
    prepare_patch_item_kwargs,
    serialize_patch_body,
    apply_patch_item_options,
)
from ._document import build_create_document, serialize_document
from ._response_parse import complete_item_response, process_backend_response


def normalize_item_arguments(
    op: str, arguments: Dict[str, Any], *, compact_utf8: bool = False,
    deadline: Optional[float] = None,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Split the caller's keyword arguments into request values and options.

    Reads only what the caller passed in, so a container that has never been
    used costs nothing here. Two things a reader might expect are left
    undone on purpose: the container's internal id, and, for writes, the
    partition key read out of the document. Both are worked out later during
    the send, because both need information only the driver holds.
    """
    kwargs = dict(arguments)
    # _item_self_link addresses an item the old way. The Rust path has no use
    # for it, so drop it here rather than carry it further down.
    kwargs.pop("_item_self_link", None)
    if op == "patch_item":
        prepare_patch_item_kwargs(kwargs)
    body = kwargs.pop("body", None)
    patch_operations = kwargs.pop("patch_operations", None)
    generate_id = kwargs.pop("enable_automatic_id_generation", False)
    inherited_deadline = kwargs.pop("_item_operation_deadline", deadline)
    args = {
        "container_link": kwargs.pop("container_link"),
        "item_id": kwargs.pop("item_id", None),
        "filter_predicate": kwargs.pop("filter_predicate", None),
        "indexing_directive": kwargs.pop("indexing_directive", None),
        "deadline": deadline if op == "create_item" else inherited_deadline,
    }
    if op in ("create_item", "upsert_item", "replace_item"):
        if op == "create_item":
            body = build_create_document(body, generate_id=generate_id)
        elif isinstance(body, dict):
            body = dict(body)
        args["document"] = serialize_document(
            body, operation=op, compact_utf8=compact_utf8,
        )
    populate_query_metrics = kwargs.pop("populate_query_metrics", None)
    options = compose_item_options(kwargs)
    if (op == "create_item" and populate_query_metrics) or (
        op in ("upsert_item", "replace_item") and populate_query_metrics is not None
    ):
        warnings.warn(
            "the populate_query_metrics flag does not apply to this method "
            "and will be removed in the future",
            DeprecationWarning,
        )
        options["populateQueryMetrics"] = populate_query_metrics
    if op == "patch_item" and args["filter_predicate"] is not None:
        options["filterPredicate"] = args["filter_predicate"]
    if op == "patch_item":
        options = deepcopy(options)
        args["body_bytes"] = serialize_patch_body(
            patch_operations, compact_utf8=compact_utf8
        )
        apply_patch_item_options(options)
    args["kwargs"] = kwargs
    return args, options


def validate_rust_item_options(args: Dict[str, Any], options: Dict[str, Any]) -> None:
    """Reject options this path cannot honor, before anything is sent.

    Failing here is the point. The alternatives would be to send the request
    with the option silently dropped, or to divert to the legacy Python code,
    and both leave the caller believing something happened that did not. The
    error names the option so it can be removed.
    """
    for key in ("read_timeout", "connection_timeout", "retry_write", "raw_request_hook", "raw_response_hook"):
        if args["kwargs"].get(key) is not None or options.get(key) is not None:
            raise NotImplementedError(f"The Rust item backend does not support per-call {key}")
    if not _timeout_is_representable(args["kwargs"]):
        raise NotImplementedError("The Rust item backend cannot honor this timeout value")
    if overrides_driver_owned_header(options):
        raise NotImplementedError("The Rust item backend cannot override driver-owned initial headers")


def normalize_item_partition_key(value: Any, system_key: bool) -> Any:
    """Turn the two stand-in partition-key values into what the wire expects.

    A caller can pass NonePartitionKeyValue or NullPartitionKeyValue in place
    of a real key. What the first of those should become depends on whether
    the container uses a system key, so that answer has to be handed in by
    whoever already knows the container's definition.
    """
    if value == NonePartitionKeyValue:
        return _return_undefined_or_empty_partition_key(system_key)
    if value == NullPartitionKeyValue:
        return None
    return value


def build_item_request(
    op: str, args: Dict[str, Any], options: Dict[str, Any],
    defaults: ItemClientDefaults,
) -> PreparedRequest:
    """Build the request object for one item operation.

    Picks the builder that matches the operation and gives it what that
    operation needs: a read needs an id, a create needs a document. Returns
    the finished request and nothing else. No lookups, no sending.

    Both the sync and async paths call this and get identical results.
    """
    # Nothing here knows whether the container uses a system key, and finding
    # out would mean a lookup before the request is even built. Pass False and
    # keep the long-standing behaviour for the explicit stand-in values.
    partition_key = normalize_item_partition_key(options.get("partitionKey", _Empty()), False)
    common = dict(
        container_link=args["container_link"],
        partition_key_value=partition_key,
        container_rid=None,
        request_options=options,
    )
    if op in ("create_item", "upsert_item", "replace_item"):
        common["extract_partition_key"] = "partitionKey" not in options
    if op == "create_item":
        return _request_item.build_create_item_request(
            document=args["document"],
            indexing_directive=args["indexing_directive"],
            no_response_on_write_default=defaults.no_response_on_write,
            **common,
        )
    if op in ("upsert_item", "replace_item"):
        if op == "replace_item":
            common["item_id"] = args["item_id"]
        builder = (
            _request_item.build_upsert_item_request if op == "upsert_item"
            else _request_item.build_replace_item_request
        )
        return builder(
            document=args["document"],
            no_response_on_write_default=defaults.no_response_on_write, **common,
        )
    if op == "patch_item":
        return _request_item.build_patch_item_request(
            item_id=args["item_id"],
            body_bytes=args["body_bytes"],
            no_response_on_write_default=defaults.no_response_on_write, **common,
        )
    if op == "read_item":
        return _request_item.build_read_item_request(item_id=args["item_id"], **common)
    return _request_item.build_delete_item_request(item_id=args["item_id"], **common)


class ItemHelper:
    """Runs one item operation, from caller arguments to finished result.

    Holds three things and nothing else: a backend to send through, the
    client-wide defaults, and somewhere to record the headers from the most
    recent reply. It does not hold the legacy Python connection, which is why
    there is no way to reach the legacy path from here.
    """

    def __init__(
        self, backend: CosmosBackend, defaults: Optional[ItemClientDefaults] = None,
        response_state: Optional[ClientLastResponseHeaders] = None,
    ) -> None:
        if defaults is not None and not isinstance(defaults, ItemClientDefaults):
            raise TypeError("defaults must be ItemClientDefaults, not a client connection")
        if response_state is not None and not isinstance(response_state, ClientLastResponseHeaders):
            raise TypeError("response_state must be ClientLastResponseHeaders")
        self._backend = backend
        self._defaults = defaults if defaults is not None else ItemClientDefaults()
        self._response_state = response_state

    def _process_response(
        self, response: BackendResponse, op: str, response_hook: Any, deadline: Optional[float] = None
    ) -> Any:
        """Turn a reply into the value the caller gets back.

        Patch is the odd one out. The other five operations leave the
        finishing work to the public method that called in, but patch
        finishes here. That is why the caller's response hook ends up being
        invoked from two different places depending on the operation.

        Delete parses its reply so the headers are recorded, then returns
        nothing.
        """
        if op == "patch_item":
            parsed = process_backend_response(response, response_state=self._response_state)
            return complete_item_response(parsed, response_hook, deadline)
        parsed = process_backend_response(response, response_state=self._response_state, response_hook=response_hook)
        return None if op == "delete_item" else parsed

    def _run(
        self, op: str, arguments: Dict[str, Any], *, deadline: Optional[float] = None
    ) -> Any:
        """Prepare, send, and interpret one operation."""
        args, options = normalize_item_arguments(
            op, arguments, compact_utf8=self._defaults.enable_compact_utf8_item_writes,
            deadline=deadline,
        )
        validate_rust_item_options(args, options)
        self._defaults.apply_to_options(options)
        prepared = build_item_request(op, args, options, self._defaults)
        response = self._backend.execute(prepared, deadline=args["deadline"])
        return self._process_response(
            response, op, args["kwargs"].get("response_hook"), args["deadline"]
        )

    def create_item(self, *, deadline: Optional[float], **kwargs: Any) -> Any:
        """Create an item, failing if the id already exists.

        The time limit arrives as its own argument because the public method
        started the clock before calling in, and that original start time is
        what the limit is measured against.
        """
        return self._run("create_item", kwargs, deadline=deadline)

    def read_item(self, **kwargs: Any) -> Any:
        """Read one item by its id and partition key."""
        return self._run("read_item", kwargs)

    def delete_item(self, **kwargs: Any) -> Any:
        """Delete an item. Returns nothing; the reply is read for its headers."""
        return self._run("delete_item", kwargs)

    def upsert_item(self, **kwargs: Any) -> Any:
        """Create an item, or replace it if one with that id is already there."""
        return self._run("upsert_item", kwargs)

    def replace_item(self, **kwargs: Any) -> Any:
        """Replace the item with this id, failing if it is not there."""
        return self._run("replace_item", kwargs)

    def patch_item(self, **kwargs: Any) -> Any:
        """Apply a list of changes to one item.

        Unlike the other five, this finishes the caller's result here rather
        than leaving it to the public method.
        """
        return self._run("patch_item", kwargs)

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare item operations, execute them through BindingAdapter, and parse responses.

This file covers the six single-item operations: create, read, replace,
upsert, patch, and delete. Preparation is local work. ItemHelper then calls
the synchronous Python backend and waits for its backend response; the binding
and Rust driver perform the service operation.

A call moves through four steps, in this order:

1. Tidy up the caller's keyword arguments and split them into the values a
   request needs and the options that shape it.
2. Reject anything the Rust path cannot honor, naming what to remove.
3. Build the request object for this particular operation.
4. Pass the prepared request to BindingAdapter, then parse its backend response.

Which path a client uses was settled earlier, up in the container class.
By the time this helper exists the choice is made, so nothing here inspects
it, and there is no fallback to the legacy path from this file.

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
from ._client_context import ClientOperationDefaults, ClientLastResponseHeaders
from ._request_settings import (
    compose_item_options, is_supported_operation_timeout,
    overrides_driver_owned_header,
)
from ._item_prep import (
    prepare_patch_item_kwargs,
    prepare_replace_item_kwargs,
    serialize_patch_body,
    apply_patch_item_options,
    validate_create_item_arguments,
)
from ._document import build_create_document, serialize_document
from ._resource_validation import validate_resource
from ._response_parse import complete_item_response, process_backend_response, process_delete_response
from .._operation_deadline import remaining_timeout


def normalize_item_arguments(
    op: str, arguments: Dict[str, Any], *, compact_utf8: bool = False,
    deadline: Optional[float] = None,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Split the caller's keyword arguments into request values and options.

    This does not fetch container metadata. The container's internal id and,
    when extraction is requested, a write's partition key are resolved on the
    Rust path after the prepared request reaches the binding.

    :param str op: Single-item operation identifier.
    :param dict[str, Any] arguments: Caller arguments copied before normalization.
    :keyword bool compact_utf8: Whether document and patch serialization emits non-ASCII UTF-8 directly.
    :keyword float or None deadline: Monotonic deadline to carry into execution.
    :return: Normalized request values and internal request options.
    :rtype: tuple[dict, dict]
    """
    if op == "create_item":
        validate_create_item_arguments(arguments)
    kwargs = dict(arguments)
    if (
        op in ("read_item", "replace_item", "patch_item", "delete_item")
        and "_item_self_link" in kwargs
        and not isinstance(kwargs["_item_self_link"], str)
    ):
        raise TypeError(f"{op} target _self must be a string.")
    item_self_link = kwargs.pop("_item_self_link", None)
    if op == "patch_item":
        prepare_patch_item_kwargs(kwargs)
    elif op == "replace_item":
        prepare_replace_item_kwargs(kwargs)
    body = kwargs.pop("body", None)
    patch_operations = kwargs.pop("patch_operations", None)
    generate_id = kwargs.pop("enable_automatic_id_generation", False)
    inherited_deadline = kwargs.pop("_item_operation_deadline", deadline)
    args = {
        "container_link": kwargs.pop("container_link"),
        "item_id": kwargs.pop("item_id", None),
        "item_self_link": item_self_link if op in ("read_item", "replace_item", "patch_item", "delete_item") else None,
        "filter_predicate": kwargs.pop("filter_predicate", None),
        "indexing_directive": kwargs.pop("indexing_directive", None),
        "deadline": deadline if op == "create_item" else inherited_deadline,
    }
    if op in ("create_item", "upsert_item", "replace_item"):
        if op == "create_item":
            body = build_create_document(body, generate_id=generate_id)
        elif isinstance(body, dict):
            body = dict(body)
            validate_resource(body)
        args["document"] = serialize_document(
            body, operation=op, compact_utf8=compact_utf8,
        )
    populate_query_metrics = kwargs.pop("populate_query_metrics", None)
    options = compose_item_options(kwargs)
    if op in ("upsert_item", "replace_item") and populate_query_metrics is not None:
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
            patch_operations, compact_utf8=compact_utf8,
            filter_predicate=options.pop("filterPredicate", None),
        )
        apply_patch_item_options(options)
    args["kwargs"] = kwargs
    return args, options


def validate_rust_item_options(
    args: Dict[str, Any], options: Dict[str, Any], *, operation: Optional[str] = None,
) -> None:
    """Reject options this path cannot honor, before anything is sent.

    Failing here is the point. The alternatives would be to send the request
    with the option silently dropped, or to divert to the legacy path,
    and both leave the caller believing something happened that did not. The
    error names the option so it can be removed.

    :param dict[str, Any] args: Normalized request values containing remaining call keywords.
    :param dict[str, Any] options: Internal request options checked for unsupported controls.
    :keyword str or None operation: Item operation whose unsupported-input contract applies.
    :return: None.
    :rtype: None
    """
    error_type = TypeError if operation == "create_item" else NotImplementedError
    for key in ("connection_timeout", "retry_write"):
        if args["kwargs"].get(key) is not None or options.get(key) is not None:
            raise error_type(f"The Rust item backend does not support per-call {key}")
    if operation == "create_item":
        for name in ("availabilityStrategy", "availability_strategy"):
            strategy = options.get(name)
            if strategy is not None and strategy is not False:
                raise TypeError(
                    "create_item() does not support write hedging through availability_strategy; "
                    "omit it or pass None or False."
                )
    timeout = args["kwargs"].get("timeout", options.get("timeout"))
    if not is_supported_operation_timeout(timeout):
        raise ValueError("Item timeout must be None or a finite number of seconds >= 1 and < 2**64.")
    if overrides_driver_owned_header(options):
        if operation == "create_item":
            raise TypeError("create_item() cannot override driver-owned initial_headers.")
        raise NotImplementedError("The Rust item backend cannot override driver-owned initial headers")


def normalize_item_partition_key(value: Any, system_key: bool) -> Any:
    """Normalize the public partition-key sentinels before request building.

    A caller can pass NonePartitionKeyValue or NullPartitionKeyValue in place
    of a real key. What the first of those should become depends on whether
    the container uses a system key, so that answer has to be handed in by
    whoever already knows the container's definition.

    :param Any value: Public partition key or sentinel.
    :param bool system_key: Whether the container uses a system partition key.
    :return: The original key or the corresponding undefined, empty, or null representation.
    :rtype: Any
    """
    if value == NonePartitionKeyValue:
        return _return_undefined_or_empty_partition_key(system_key)
    if value == NullPartitionKeyValue:
        return None
    return value


def build_item_request(
    op: str, args: Dict[str, Any], options: Dict[str, Any],
    defaults: ClientOperationDefaults,
) -> PreparedRequest:
    """Build the prepared request for one item operation.

    Picks the builder that matches the operation and gives it what that
    operation needs: a read needs an id or resource address, a create needs a document. Returns
    the finished request and nothing else. No lookups, no sending.

    Both the sync and async paths call this and get identical results.

    :param str op: Single-item operation identifier selecting the request builder.
    :param dict[str, Any] args: Normalized target, serialized body, and operation-specific values.
    :param dict[str, Any] options: Internal request options containing any explicit partition key.
    :param ClientOperationDefaults defaults: Client defaults for write response bodies.
    :return: The prepared item request without performing I/O.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
    # Nothing here knows whether the container uses a system key, and finding
    # out would mean a lookup before the request is even built. Pass False and
    # keep the long-standing behaviour for the explicit stand-in values.
    partition_key = normalize_item_partition_key(options.get("partitionKey", _Empty()), False)
    common = {
        "container_link": args["container_link"],
        "partition_key_value": partition_key,
        "container_rid": None,
        "request_options": options,
    }
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
            common["item_self_link"] = args["item_self_link"]
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
            item_self_link=args["item_self_link"],
            body_bytes=args["body_bytes"],
            no_response_on_write_default=defaults.no_response_on_write, **common,
        )
    if op == "read_item":
        return _request_item.build_read_item_request(
            item_id=args["item_id"], item_self_link=args["item_self_link"], **common
        )
    return _request_item.build_delete_item_request(
        item_id=args["item_id"], item_self_link=args["item_self_link"], **common
    )


class ItemHelper:
    """Runs one item operation, from caller arguments to finished result.

    Holds three things: the selected Python backend, the
    client-wide defaults, and somewhere to record the headers from the most
    recent backend response. It does not hold the legacy connection, which is why
    there is no way to reach the legacy path from here.
    """

    def __init__(
        self, backend: CosmosBackend, defaults: Optional[ClientOperationDefaults] = None,
        response_state: Optional[ClientLastResponseHeaders] = None,
    ) -> None:
        if defaults is not None and not isinstance(defaults, ClientOperationDefaults):
            raise TypeError("defaults must be ClientOperationDefaults, not a client connection")
        if response_state is not None and not isinstance(response_state, ClientLastResponseHeaders):
            raise TypeError("response_state must be ClientLastResponseHeaders")
        self._backend = backend
        self._defaults = defaults if defaults is not None else ClientOperationDefaults()
        self._response_state = response_state

    def _process_response(
        self, response: BackendResponse, op: str, response_hook: Any, deadline: Optional[float] = None
    ) -> Any:
        """Turn a backend response into the value the customer app receives.

        Create and read leave response-hook invocation to their public methods.
        Replace and upsert invoke the hook through process_backend_response here.
        Patch uses complete_item_response here to check the deadline and invoke
        the hook. Delete records headers, invokes the hook with a None body,
        and returns None.

        :param BackendResponse response: Backend response to validate and parse.
        :param str op: Operation identifier determining response completion.
        :param callable or None response_hook: Synchronous callback invoked by response processing when supplied.
        :param float or None deadline: Monotonic deadline checked for patch and replacement completion.
        :return: Parsed item properties, or None for deletion.
        :rtype: ~azure.cosmos.CosmosDict or None
        """
        if op == "patch_item":
            parsed = process_backend_response(response, response_state=self._response_state)
            return complete_item_response(parsed, response_hook, deadline)
        if op == "replace_item":
            remaining_timeout(deadline)
        if op == "delete_item":
            return process_delete_response(response, response_state=self._response_state, response_hook=response_hook)
        return process_backend_response(response, response_state=self._response_state, response_hook=response_hook)

    def _run(
        self, op: str, arguments: Dict[str, Any], *, deadline: Optional[float] = None
    ) -> Any:
        """Prepare, send, and interpret one operation.

        :param str op: Single-item operation identifier.
        :param dict[str, Any] arguments: Target, body, and caller request options to normalize.
        :keyword float or None deadline: Monotonic deadline passed through preparation and execution.
        :return: Parsed item properties, or None for deletion.
        :rtype: ~azure.cosmos.CosmosDict or None
        """
        args, options = normalize_item_arguments(
            op, arguments, compact_utf8=self._defaults.enable_compact_utf8_item_writes,
            deadline=deadline,
        )
        validate_rust_item_options(args, options, operation=op)
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

        ``kwargs`` contains the container link, document body, and creation options to normalize.

        :keyword float or None deadline: Monotonic creation deadline established by the public method.
        :return: Created item properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        return self._run("create_item", kwargs, deadline=deadline)

    def read_item(self, **kwargs: Any) -> Any:
        """Read one item by its id and partition key.

        ``kwargs`` contains the container link, item target, partition key, and read options.

        :return: Item properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        return self._run("read_item", kwargs)

    def delete_item(self, **kwargs: Any) -> Any:
        """Delete an item. Returns nothing; the reply is read for its headers.

        ``kwargs`` contains the container link, item target, partition key, and deletion options.

        :return: None.
        :rtype: None
        """
        return self._run("delete_item", kwargs)

    def upsert_item(self, **kwargs: Any) -> Any:
        """Create an item, or replace it if one with that id is already there.

        ``kwargs`` contains the container link, document body, and upsert options.

        :return: Upserted item properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        return self._run("upsert_item", kwargs)

    def replace_item(self, **kwargs: Any) -> Any:
        """Replace the item with this id, failing if it is not there.

        ``kwargs`` contains the container link, item target, replacement body, and request options.

        :return: Replaced item properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        return self._run("replace_item", kwargs)

    def patch_item(self, **kwargs: Any) -> Any:
        """Apply changes to one item and complete its response, including the hook.

        ``kwargs`` contains the container link, item target, patch operations, and request options.

        :return: Patched item properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        return self._run("patch_item", kwargs)

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Connection-free Rust point operations: options, metadata, build, execute, parse.

Legacy parity is selected before constructing this helper, in the container.
No legacy operation, connection cache, or transport callback enters this path.
"""
from __future__ import annotations

import warnings
from typing import Any, Dict, Optional

from .._backend.cosmos_backend import CosmosBackend
from .._backend.contracts import BackendResponse, PreparedRequest
from ..partition_key import (
    _Empty, NonePartitionKeyValue, NullPartitionKeyValue,
    _return_undefined_or_empty_partition_key,
)
from . import _request_item
from ._item_context import ItemClientDefaults, ResponseHeaderState
from ._options import compose_item_options
from ._metadata_provider import ContainerMetadataProvider
from ._response_parse import parse_backend_response
from ._request_headers import _timeout_is_representable, overrides_driver_owned_header


def prepare_item_arguments(op: str, arguments: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Normalize Rust arguments eagerly, without legacy option preparation.

    Only local mappings are consumed. Metadata and wire request construction
    remain lazy inside the backend's prepare_request callback.
    """
    kwargs = dict(arguments)
    args = {
        "container_link": kwargs.pop("container_link"),
        "document_link": kwargs.pop("document_link", None),
        "item_id": kwargs.pop("item_id", None),
        "body": kwargs.pop("body", None),
        "patch_operations": kwargs.pop("patch_operations", None),
        "filter_predicate": kwargs.pop("filter_predicate", None),
        "indexing_directive": kwargs.pop("indexing_directive", None),
        "enable_automatic_id_generation": kwargs.pop("enable_automatic_id_generation", False),
    }
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
    # The existing pure wire builders receive normalized options explicitly,
    # rather than depending on legacy build_options mutating an aliased dict.
    args["wire_kwargs"] = dict(kwargs, request_options=options)
    args["kwargs"] = kwargs
    return args, options


def validate_rust_item_options(op: str, args: Dict[str, Any], options: Dict[str, Any]) -> None:
    """Unsupported Rust semantics fail explicitly, never replaying on Python."""
    if op == "patch_item" and ("filterPredicate" in options or "accessCondition" in options):
        raise NotImplementedError("The Rust backend does not support filtered or conditional patches")
    for key in ("read_timeout", "connection_timeout", "retry_write", "raw_request_hook", "raw_response_hook"):
        if args["wire_kwargs"].get(key) is not None or options.get(key) is not None:
            raise NotImplementedError(f"The Rust item backend does not support per-call {key}")
    if not _timeout_is_representable(args["wire_kwargs"]):
        raise NotImplementedError("The Rust item backend cannot honor this timeout value")
    if overrides_driver_owned_header(options):
        raise NotImplementedError("The Rust item backend cannot override driver-owned initial headers")


def normalize_item_partition_key(value: Any, properties: Dict[str, Any]) -> Any:
    """Resolve sentinel keys with backend metadata, not ContainerProxy.is_system_key."""
    if value == NonePartitionKeyValue:
        return _return_undefined_or_empty_partition_key(
            properties.get("partitionKey", {}).get("systemKey", False)
        )
    if value == NullPartitionKeyValue:
        return None
    return value


def execute_item_builder(
    op: str, args: Dict[str, Any], options: Dict[str, Any],
    partition_key: Any, rid: Optional[str], defaults: ItemClientDefaults,
) -> PreparedRequest:
    """Select and invoke an item builder using the operation's argument shape.

    Shared by sync and async preparation. Returns only the PreparedRequest,
    unwrapping create's additional item id, without metadata or network calls.
    """
    common = dict(
        container_link=args["container_link"],
        partition_key_value=partition_key,
        container_rid=rid,
        kwargs=args["wire_kwargs"],
    )
    if op == "create_item":
        prepared, _ = _request_item.build_create_item_request(
            body=args["body"],
            indexing_directive=args["indexing_directive"],
            enable_automatic_id_generation=args["enable_automatic_id_generation"],
            no_response_on_write_default=defaults.no_response_on_write,
            **common,
        )
        return prepared
    if op in ("upsert_item", "replace_item"):
        if op == "replace_item":
            common["item_id"] = args["item_id"]
        builder = (
            _request_item.build_upsert_item_request if op == "upsert_item"
            else _request_item.build_replace_item_request
        )
        return builder(
            body=args["body"], access_condition=options.get("accessCondition"),
            no_response_on_write_default=defaults.no_response_on_write, **common,
        )
    if op == "patch_item":
        return _request_item.build_patch_item_request(
            item_id=args["item_id"], patch_operations=args["patch_operations"],
            no_response_on_write_default=defaults.no_response_on_write, **common,
        )
    builder = _request_item.build_read_item_request if op == "read_item" else _request_item.build_delete_item_request
    return builder(item_id=args["item_id"], **common)


class ItemHelper:
    """One Rust item operation, holding only backend, immutable defaults and headers."""

    def __init__(
        self, backend: CosmosBackend, defaults: Optional[ItemClientDefaults] = None,
        response_state: Optional[ResponseHeaderState] = None,
    ) -> None:
        if defaults is not None and not isinstance(defaults, ItemClientDefaults):
            raise TypeError("defaults must be ItemClientDefaults, not a client connection")
        if response_state is not None and not isinstance(response_state, ResponseHeaderState):
            raise TypeError("response_state must be ResponseHeaderState")
        self._backend = backend
        self._defaults = defaults if defaults is not None else ItemClientDefaults()
        self._response_state = response_state

    def _parse(self, response: BackendResponse, op: str, response_hook: Any) -> Any:
        parsed = parse_backend_response(response, response_state=self._response_state, response_hook=response_hook)
        return None if op == "delete_item" else parsed

    def _run(self, op: str, arguments: Dict[str, Any]) -> Any:
        args, options = prepare_item_arguments(op, arguments)
        validate_rust_item_options(op, args, options)
        link = args["container_link"]
        metadata = ContainerMetadataProvider(self._backend, self._response_state)

        def prepare_request() -> PreparedRequest:
            rid = metadata.container_rid(link, options)
            if op in ("create_item", "upsert_item", "replace_item"):
                key = metadata.extract_partition_key(link, args["body"], options)
            else:
                key = options.get("partitionKey", _Empty())
            key = normalize_item_partition_key(key, metadata._container_properties(link, options))
            return execute_item_builder(op, args, options, key, rid, self._defaults)

        return self._backend.run_item_operation(
            prepare_request=prepare_request,
            parse_response=lambda response: self._parse(response, op, args["kwargs"].get("response_hook")),
        )

    def create_item(self, **kwargs: Any) -> Any:
        """Create an item through Rust only."""
        return self._run("create_item", kwargs)

    def read_item(self, **kwargs: Any) -> Any:
        """Read an item through Rust only."""
        return self._run("read_item", kwargs)

    def delete_item(self, **kwargs: Any) -> Any:
        """Delete an item through Rust, returning None after parsing headers."""
        return self._run("delete_item", kwargs)

    def upsert_item(self, **kwargs: Any) -> Any:
        """Upsert an item through Rust only."""
        return self._run("upsert_item", kwargs)

    def replace_item(self, **kwargs: Any) -> Any:
        """Replace an item through Rust only."""
        return self._run("replace_item", kwargs)

    def patch_item(self, **kwargs: Any) -> Any:
        """Patch an item through Rust; unsupported guards raise explicitly."""
        return self._run("patch_item", kwargs)

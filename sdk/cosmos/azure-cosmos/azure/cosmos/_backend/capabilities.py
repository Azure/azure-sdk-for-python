# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Limit fallback to the legacy path while migration is unfinished.

For a call with several steps, such as reading and then replacing throughput,
the Python wrapper checks whether Rust supports the complete call. These
temporary rules permit some legacy-path calls only before execution, not as
a customer-facing execution choice. The Rust path is the only release path.
A failure during execution, response processing, or a customer callback is
not retried through the legacy path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from . import operations as ops

GET_OR_CREATE_DATABASE = "create_database_if_not_exists"
GET_OR_CREATE_CONTAINER = "create_container_if_not_exists"
REPLACE_THROUGHPUT = "replace_throughput"
GET_DATABASE_THROUGHPUT = "get_database_throughput"
GET_CONTAINER_THROUGHPUT = "get_container_throughput"


def require_legacy_api(connection: Any, api_name: str, *, item_context: Any = None) -> None:
    """Retain comparison-only APIs without executing them on a Rust client."""
    if item_context is not None:
        backend = item_context.adapter
    else:
        attributes = getattr(connection, "__dict__", {})
        backend = attributes.get("_backend")
    if backend is None or backend.name != "core-python":
        raise NotImplementedError(
            f"{api_name} is excluded from the Rust-backed APIs; no legacy fallback."
        )


def reject_unsupported_rust_arguments(
    proxy: Any, kwargs: Mapping[str, Any], *, strategy: Any = None, headers: Any = None,
) -> None:
    """Reject excluded inputs before metadata, paging, or retained coordinators."""
    context = getattr(proxy, "_item_context", None)
    backend = context.adapter if context is not None else getattr(
        proxy.client_connection, "__dict__", {}
    ).get("_backend")
    if backend is not None and backend.name == "core-python":
        return
    reject_rust_arguments(kwargs, strategy=strategy, headers=headers)


def reject_rust_arguments(
    kwargs: Mapping[str, Any], *, strategy: Any = None, headers: Any = None,
) -> None:
    """Validate Rust inputs without requiring a constructed client or proxy."""
    from .._availability_strategy_config import reject_rust_threshold_steps
    from .request_settings import reject_trigger_header

    reject_rust_threshold_steps(strategy)
    for options in (
        kwargs, kwargs.get("request_options"), kwargs.get("feed_options"), {"initial_headers": headers},
    ):
        if not isinstance(options, Mapping):
            continue
        for name, value in options.items():
            if name in (
                "pre_trigger_include", "post_trigger_include", "preTriggerInclude", "postTriggerInclude",
                "threshold_steps_ms",
            ):
                raise TypeError(f"{name} is not supported by the Rust-backed APIs.")
            if isinstance(name, str):
                reject_trigger_header(name)
            if name in ("availability_strategy", "availabilityStrategy"):
                reject_rust_threshold_steps(value)
            if name in ("initial_headers", "initialHeaders", "headers") and isinstance(value, Mapping):
                for header in value:
                    if isinstance(header, str):
                        reject_trigger_header(header)


@dataclass(frozen=True)
class OpCapability:
    operations: frozenset[str]
    fallback_allowed: bool = False
    unsupported_message: Optional[str] = None


CAPABILITIES: dict[str, OpCapability] = {
    GET_CONTAINER_THROUGHPUT: OpCapability(
        frozenset({ops.OP_READ_OFFER}),
        unsupported_message=(
            "The container throughput read cannot honor this input on the Rust path: "
            "a per-call timeout, availability strategy, request-header override, or "
            "additional keyword is unsupported. The Python wrapper will not send "
            "the request through the legacy Python path."
        ),
    ),
    GET_DATABASE_THROUGHPUT: OpCapability(
        frozenset({ops.OP_READ_OFFER}),
        unsupported_message=(
            "The database throughput read cannot honor this input on the Rust path: "
            "a per-call timeout, availability strategy, request-header override, or "
            "additional keyword is unsupported. The Python wrapper will not send "
            "the request through the legacy Python path."
        ),
    ),
    REPLACE_THROUGHPUT: OpCapability(
        frozenset({ops.OP_READ_OFFER, ops.OP_REPLACE_OFFER}), fallback_allowed=True
    ),
    ops.OP_CREATE_DATABASE: OpCapability(
        frozenset({ops.OP_CREATE_DATABASE}),
    ),
    ops.OP_READ_DATABASE: OpCapability(
        frozenset({ops.OP_READ_DATABASE}),
        unsupported_message=(
            "DatabaseProxy.read cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_DELETE_DATABASE: OpCapability(
        frozenset({ops.OP_DELETE_DATABASE}),
        unsupported_message=(
            "delete_database cannot run on the Rust backend for this call because a per-call setting, "
            "request hook, or header override cannot be honored. Remove the unsupported option. The "
            "request will not be sent through legacy Python."
        ),
    ),
    ops.OP_CREATE_CONTAINER: OpCapability(
        frozenset({ops.OP_CREATE_CONTAINER}),
        unsupported_message=(
            "create_container cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_READ_CONTAINER: OpCapability(
        frozenset({ops.OP_READ_CONTAINER}),
        unsupported_message=(
            "ContainerProxy.read cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_DELETE_CONTAINER: OpCapability(
        frozenset({ops.OP_DELETE_CONTAINER}),
        unsupported_message=(
            "delete_container cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_REPLACE_CONTAINER: OpCapability(
        frozenset({ops.OP_REPLACE_CONTAINER}),
        unsupported_message=(
            "replace_container cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_CREATE_ITEM: OpCapability(
        frozenset({ops.OP_CREATE_ITEM}),
    ),
    ops.OP_READ_ITEM: OpCapability(
        frozenset({ops.OP_READ_ITEM}),
    ),
    ops.OP_UPSERT_ITEM: OpCapability(
        frozenset({ops.OP_UPSERT_ITEM}),
    ),
    ops.OP_REPLACE_ITEM: OpCapability(
        frozenset({ops.OP_REPLACE_ITEM}),
    ),
    ops.OP_DELETE_ITEM: OpCapability(
        frozenset({ops.OP_DELETE_ITEM}),
    ),
    ops.OP_PATCH_ITEM: OpCapability(
        frozenset({ops.OP_PATCH_ITEM}),
    ),
    ops.OP_LIST_DATABASES: OpCapability(
        frozenset({ops.OP_LIST_DATABASES}),
        unsupported_message=(
            "list_databases cannot run on the Rust backend for this call: per-call read_timeout, an "
            "unsupported timeout value, availability_strategy, driver-owned header overrides, "
            "unsupported transport keywords/hooks, and non-list feed shapes are not supported by this "
            "listing path. Remove the unsupported option; configure connection and read timeouts when "
            "constructing CosmosClient. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_QUERY_DATABASES: OpCapability(
        frozenset({ops.OP_QUERY_DATABASES}),
        unsupported_message=(
            "query_databases cannot run on the Rust backend for this call: the query mode, timeout "
            "value, request-header override, or transport option is not supported by this query path. "
            "Remove the unsupported option; configure connection and read timeouts when constructing "
            "CosmosClient. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_LIST_CONTAINERS: OpCapability(
        frozenset({ops.OP_LIST_CONTAINERS}),
        unsupported_message=(
            "list_containers cannot run on the Rust backend for this call: per-call read_timeout, an "
            "unsupported timeout value, availability_strategy, driver-owned header overrides, "
            "unsupported transport keywords/hooks, and non-list feed shapes are not supported by this "
            "listing path. Remove the unsupported option; configure connection and read timeouts when "
            "constructing CosmosClient. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_QUERY_CONTAINERS: OpCapability(
        frozenset({ops.OP_QUERY_CONTAINERS}),
        unsupported_message=(
            "query_containers cannot run on the Rust backend for this call: the query mode, timeout "
            "value, request-header override, or transport option is not supported by this query path. "
            "Remove the unsupported option; configure connection and read timeouts when constructing "
            "CosmosClient. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_QUERY_ITEMS_CHANGE_FEED: OpCapability(
        frozenset({ops.OP_QUERY_ITEMS_CHANGE_FEED}),
    ),
    ops.OP_READ_OFFER: OpCapability(
        frozenset({ops.OP_READ_OFFER}),
        fallback_allowed=True,
    ),
    ops.OP_REPLACE_OFFER: OpCapability(
        frozenset({ops.OP_REPLACE_OFFER}),
        fallback_allowed=True,
    ),
    ops.OP_READ_FEED_RANGES: OpCapability(
        frozenset({ops.OP_READ_FEED_RANGES}),
        unsupported_message=(
            "read_feed_ranges cannot honor additional per-call options on Rust; "
            "only force_refresh is supported by this range lookup. "
            "The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_FEED_RANGE_FROM_PARTITION_KEY: OpCapability(
        frozenset({ops.OP_FEED_RANGE_FROM_PARTITION_KEY}),
        fallback_allowed=True,
    ),
    ops.OP_IS_FEED_RANGE_SUBSET: OpCapability(
        frozenset({ops.OP_IS_FEED_RANGE_SUBSET}),
        unsupported_message=(
            "is_feed_range_subset requires supported SDK-returned feed ranges "
            "with hexadecimal bounds and Boolean inclusion flags. "
            "The comparison will not run through legacy Python."
        ),
    ),
    ops.OP_READ_ALL_ITEMS: OpCapability(
        frozenset({ops.OP_READ_ALL_ITEMS}),
        fallback_allowed=True,
    ),
    ops.OP_QUERY_ITEMS: OpCapability(
        frozenset({ops.OP_QUERY_ITEMS}),
        fallback_allowed=True,
    ),
    GET_OR_CREATE_DATABASE: OpCapability(
        frozenset({ops.OP_CREATE_DATABASE, ops.OP_READ_DATABASE}),
        unsupported_message=(
            "create_database_if_not_exists cannot run on the Rust backend for this call: it was given "
            "a per-call option the Rust path cannot honor (read_timeout, a timeout the driver would "
            "interpret differently, an overridden standard request header, or a transport keyword "
            "such as connection_timeout). Remove the unsupported per-call option; configure "
            "connection and read timeouts when constructing CosmosClient."
        ),
    ),
    GET_OR_CREATE_CONTAINER: OpCapability(
        frozenset({ops.OP_CREATE_CONTAINER, ops.OP_READ_CONTAINER}),
        unsupported_message=(
            "create_container_if_not_exists cannot run on the Rust backend because a per-call "
            "setting, request hook, or header override cannot be honored by both the read and create "
            "steps. Remove the unsupported option. The request will not be sent through legacy "
            "Python."
        ),
    ),
}


@dataclass(frozen=True)
class OperationRouting:
    """Choose Rust or permitted legacy execution, not a service region or replica.

    ``capability`` can name a multi-step call whose rules differ from those of
    one step. For example, get-or-create must support both reading and creating.
    The private legacy test branch skips Rust checks and prepared request building.
    """

    op: str
    supported: bool = True
    capability: Optional[str] = None

    @property
    def policy(self) -> OpCapability:
        key = self.capability or self.op
        policy = CAPABILITIES.get(key)
        if policy is None or self.op not in policy.operations:
            raise NotImplementedError(
                f"No migration capability registered for {key!r}/{self.op!r}."
            )
        return policy

    def uses_legacy(self) -> bool:
        policy = self.policy
        if self.supported:
            return False
        if policy.fallback_allowed:
            return True
        raise NotImplementedError(
            policy.unsupported_message
            or f"{self.capability or self.op} cannot honor this request on Rust; "
            "the request will not be sent through legacy Python."
        )

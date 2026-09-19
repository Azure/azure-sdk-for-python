# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Temporary migration policy, independent of request builders and transports.

Request compatibility is evaluated by the coordinator, once for a compound
workflow. This table grants fallback only before dispatch. No execution,
response processing, or customer callback failure is replayable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from . import operations as ops

GET_OR_CREATE_DATABASE = "create_database_if_not_exists"
GET_OR_CREATE_CONTAINER = "create_container_if_not_exists"
REPLACE_THROUGHPUT = "replace_throughput"


@dataclass(frozen=True)
class OpCapability:
    operations: frozenset[str]
    fallback_allowed: bool = False
    unsupported_message: Optional[str] = None


CAPABILITIES: dict[str, OpCapability] = {
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
        fallback_allowed=True,
    ),
    ops.OP_FEED_RANGE_FROM_PARTITION_KEY: OpCapability(
        frozenset({ops.OP_FEED_RANGE_FROM_PARTITION_KEY}),
        fallback_allowed=True,
    ),
    ops.OP_IS_FEED_RANGE_SUBSET: OpCapability(
        frozenset({ops.OP_IS_FEED_RANGE_SUBSET}),
        fallback_allowed=True,
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
    """A request's compatibility decision, separate from operation policy.

    ``capability`` identifies a compound workflow when it is stricter than its
    individual wire operations. Explicit legacy backends do not evaluate this
    Rust migration decision and never build the prepared request.
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

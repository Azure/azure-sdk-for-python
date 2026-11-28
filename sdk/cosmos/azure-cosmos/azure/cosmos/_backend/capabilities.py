# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Require Rust support before dispatching an operation.

For a call with several steps, such as reading and then replacing throughput,
the Python wrapper checks whether Rust supports the complete call. These
rules reject unsupported requests without switching to legacy Python. The
separately selected legacy backend remains only for migration comparisons.
Neither preflight nor execution, response processing, or callback failures
may cause a Rust request to run through the legacy path.
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


def reject_removed_options(kwargs: Mapping[str, Any]) -> None:
    """Reject removed settings on both execution paths, including nested options.

    :param kwargs: Operation options, including any nested legacy option mappings.
    :type kwargs: typing.Mapping[str, typing.Any]
    """
    for options in (kwargs, kwargs.get("request_options"), kwargs.get("feed_options"), kwargs.get("options")):
        if not isinstance(options, Mapping):
            continue
        if "retry_throttle_backoff_max" in options:
            raise TypeError(
                "retry_throttle_backoff_max has been renamed; "
                "use throttle_retry_wait_threshold_seconds with the same value in seconds."
            )
        if "read_timeout" in options:
            raise TypeError("read_timeout has been removed; use timeout for the overall operation budget.")
        for name in ("raw_request_hook", "raw_response_hook"):
            if name in options:
                raise TypeError(
                    f"{name} has been removed; use response headers, results, tracing, or diagnostics."
                )
        for name in ("proxy_config", "proxies", "ssl_config", "connection_verify", "connection_cert", "transport"):
            if name in options:
                raise TypeError(
                    f"{name} has been removed; custom proxy, TLS, and transport settings are not supported."
                )
    policy = kwargs.get("connection_policy")
    if policy is not None:
        for name in (
            "ReadTimeout", "RecoveryReadTimeout", "DBAReadTimeout",
            "ProxyConfiguration", "SSLConfiguration", "DisableSSLVerification",
        ):
            if hasattr(policy, name):
                raise TypeError(f"connection_policy.{name} has been removed.")


def prepare_operation_kwargs(
    proxy: Any, kwargs: dict[str, Any], *, strategy: Any = None, headers: Any = None,
    inherit_timeout: bool = True,
) -> None:
    """Validate inputs and apply defaults before metadata, paging, or coordinators.

    :param proxy: Client proxy providing backend selection and client defaults.
    :type proxy: typing.Any
    :param kwargs: Operation keyword arguments validated and updated in place.
    :type kwargs: dict[str, typing.Any]
    :keyword strategy: Availability strategy to validate for Rust operations.
    :paramtype strategy: typing.Any
    :keyword headers: Initial header overrides to validate.
    :paramtype headers: typing.Any
    :keyword inherit_timeout: Whether to apply the client timeout default to the options.
    :paramtype inherit_timeout: bool
    """
    reject_removed_options(kwargs)
    context = getattr(proxy, "_client_context", None)
    backend = context.adapter if context is not None else getattr(
        proxy.client_connection, "__dict__", {}
    ).get("_backend")
    if backend is not None and backend.name == "core-python":
        for options in (kwargs, kwargs.get("request_options"), kwargs.get("feed_options")):
            if isinstance(options, Mapping) and (
                "utf8_decoding_mode" in options or "utf8DecodingMode" in options
            ):
                raise ValueError("utf8_decoding_mode is supported only by the Rust backend.")
        return
    reject_rust_arguments(kwargs, strategy=strategy, headers=headers)
    if inherit_timeout and context is not None:
        context.defaults.apply_timeout(kwargs)


def reject_rust_arguments(
    kwargs: Mapping[str, Any], *, strategy: Any = None, headers: Any = None,
) -> None:
    """Validate Rust inputs without requiring a constructed client or proxy.

    :param kwargs: Operation options, including nested request and feed options.
    :type kwargs: typing.Mapping[str, typing.Any]
    :keyword strategy: Availability strategy to check for unsupported threshold steps.
    :paramtype strategy: typing.Any
    :keyword headers: Initial header overrides to check for unsupported trigger headers.
    :paramtype headers: typing.Any
    """
    from .._availability_strategy_config import reject_rust_threshold_steps
    from .request_settings import reject_trigger_header

    reject_rust_threshold_steps(strategy)
    for options in (
        kwargs, kwargs.get("request_options"), kwargs.get("feed_options"), {"initial_headers": headers},
    ):
        if not isinstance(options, Mapping):
            continue
        if "network_span_namer" in options:
            raise TypeError(
                "network_span_namer is not supported by Rust-backed APIs; omit this keyword. "
                "The current Rust integration cannot supply the actual HTTP request to this callback."
            )
        for name, value in options.items():
            if name in ("user_agent", "user_agent_overwrite", "user_agent_use_env"):
                raise TypeError(
                    f"{name} is not supported by Rust-backed APIs because the Rust driver "
                    "does not support this setting. Omit this keyword; use user_agent_suffix "
                    "to add an application label."
                )
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
                    if not isinstance(header, str):
                        raise TypeError("Request header names must be strings.")
                    reject_trigger_header(header)


@dataclass(frozen=True)
class OpCapability:
    operations: frozenset[str]
    unsupported_message: Optional[str] = None
    unsupported_error_type: type[Exception] = NotImplementedError


CAPABILITIES: dict[str, OpCapability] = {
    ops.OP_EXECUTE_ITEM_BATCH: OpCapability(
        frozenset({ops.OP_EXECUTE_ITEM_BATCH}),
    ),
    GET_CONTAINER_THROUGHPUT: OpCapability(
        frozenset({ops.OP_GET_THROUGHPUT}),
        unsupported_message=(
            "The container throughput read cannot honor this input on the Rust path: "
            "an availability strategy, request-header override, or "
            "additional keyword is unsupported. The Python wrapper will not send "
            "the request through the legacy Python path."
        ),
    ),
    GET_DATABASE_THROUGHPUT: OpCapability(
        frozenset({ops.OP_GET_THROUGHPUT}),
        unsupported_message=(
            "The database throughput read cannot honor this input on the Rust path: "
            "an availability strategy, request-header override, or "
            "additional keyword is unsupported. The Python wrapper will not send "
            "the request through the legacy Python path."
        ),
    ),
    REPLACE_THROUGHPUT: OpCapability(
        frozenset({ops.OP_GET_THROUGHPUT, ops.OP_REPLACE_THROUGHPUT}),
        unsupported_message=(
            "The throughput replacement cannot honor this input on the Rust path: "
            "the availability strategy, request-header override, or additional "
            "keyword is unsupported. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_CREATE_DATABASE: OpCapability(
        frozenset({ops.OP_CREATE_DATABASE}),
    ),
    ops.OP_READ_DATABASE: OpCapability(
        frozenset({ops.OP_READ_DATABASE}),
        unsupported_error_type=TypeError,
        unsupported_message=(
            "DatabaseProxy.read cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_DELETE_DATABASE: OpCapability(
        frozenset({ops.OP_DELETE_DATABASE}),
        unsupported_error_type=TypeError,
        unsupported_message=(
            "delete_database cannot run on the Rust backend for this call because a per-call setting, "
            "request hook, or header override cannot be honored. Remove the unsupported option. The "
            "request will not be sent through legacy Python."
        ),
    ),
    ops.OP_CREATE_CONTAINER: OpCapability(
        frozenset({ops.OP_CREATE_CONTAINER}),
        unsupported_error_type=TypeError,
        unsupported_message=(
            "create_container cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_READ_CONTAINER: OpCapability(
        frozenset({ops.OP_READ_CONTAINER}),
        unsupported_error_type=TypeError,
        unsupported_message=(
            "ContainerProxy.read cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_DELETE_CONTAINER: OpCapability(
        frozenset({ops.OP_DELETE_CONTAINER}),
        unsupported_error_type=TypeError,
        unsupported_message=(
            "delete_container cannot run on the Rust backend for this call because a per-call "
            "setting, request hook, or header override cannot be honored. Remove the unsupported "
            "option. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_REPLACE_CONTAINER: OpCapability(
        frozenset({ops.OP_REPLACE_CONTAINER}),
        unsupported_error_type=TypeError,
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
    ops.OP_READ_ITEMS: OpCapability(
        frozenset({ops.OP_READ_ITEMS}),
    ),
    ops.OP_READ_ALL_ITEMS: OpCapability(
        frozenset({ops.OP_READ_ALL_ITEMS}),
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
            "list_databases cannot run on the Rust backend for this call: an "
            "unsupported timeout value, availability_strategy, driver-owned header overrides, "
            "unsupported transport keywords/hooks, and non-list feed shapes are not supported by this "
            "listing path. Configure connection and HTTP-request limits through CosmosRuntime; "
            "read inactivity is unsupported. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_QUERY_DATABASES: OpCapability(
        frozenset({ops.OP_QUERY_DATABASES}),
        unsupported_message=(
            "query_databases cannot run on the Rust backend for this call: the query mode, timeout "
            "value, request-header override, or transport option is not supported by this query path. "
            "Configure connection and HTTP-request limits through CosmosRuntime; "
            "read inactivity is unsupported. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_LIST_CONTAINERS: OpCapability(
        frozenset({ops.OP_LIST_CONTAINERS}),
        unsupported_message=(
            "list_containers cannot run on the Rust backend for this call: an "
            "unsupported timeout value, availability_strategy, driver-owned header overrides, "
            "unsupported transport keywords/hooks, and non-list feed shapes are not supported by this "
            "listing path. Configure connection and HTTP-request limits through CosmosRuntime; "
            "read inactivity is unsupported. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_QUERY_CONTAINERS: OpCapability(
        frozenset({ops.OP_QUERY_CONTAINERS}),
        unsupported_message=(
            "query_containers cannot run on the Rust backend for this call: the query mode, timeout "
            "value, request-header override, or transport option is not supported by this query path. "
            "Configure connection and HTTP-request limits through CosmosRuntime; "
            "read inactivity is unsupported. The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_QUERY_ITEMS_CHANGE_FEED: OpCapability(
        frozenset({ops.OP_QUERY_ITEMS_CHANGE_FEED}),
    ),
    ops.OP_GET_THROUGHPUT: OpCapability(
        frozenset({ops.OP_GET_THROUGHPUT}),
    ),
    ops.OP_READ_FEED_RANGES: OpCapability(
        frozenset({ops.OP_READ_FEED_RANGES}),
        unsupported_message=(
            "read_feed_ranges cannot honor additional per-call options on Rust; "
            "only force_refresh and timeout are supported by this range lookup. "
            "The request will not be sent through legacy Python."
        ),
    ),
    ops.OP_FEED_RANGE_FROM_PARTITION_KEY: OpCapability(
        frozenset({ops.OP_FEED_RANGE_FROM_PARTITION_KEY}),
    ),
    ops.OP_IS_FEED_RANGE_SUBSET: OpCapability(
        frozenset({ops.OP_IS_FEED_RANGE_SUBSET}),
    ),
    ops.OP_QUERY_ITEMS: OpCapability(
        frozenset({ops.OP_QUERY_ITEMS}),
    ),
    GET_OR_CREATE_DATABASE: OpCapability(
        frozenset({ops.OP_CREATE_DATABASE, ops.OP_READ_DATABASE}),
        unsupported_message=(
            "create_database_if_not_exists cannot run on the Rust backend for this call: it was given "
            "a per-call option the Rust path cannot honor (an overridden standard request "
            "header or another unsupported option). Remove the unsupported per-call option."
        ),
    ),
    GET_OR_CREATE_CONTAINER: OpCapability(
        frozenset({ops.OP_CREATE_CONTAINER, ops.OP_READ_CONTAINER}),
        unsupported_error_type=TypeError,
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
    """Validate a Rust operation's support, not a service region or replica.

    ``capability`` can name a multi-step call whose rules differ from those of
    one step. For example, get-or-create must support both reading and creating.
    The private legacy test branch skips Rust checks and prepared request building.
    """

    op: str
    supported: bool = True
    capability: Optional[str] = None
    unsupported_message: Optional[str] = None

    @property
    def policy(self) -> OpCapability:
        key = self.capability or self.op
        policy = CAPABILITIES.get(key)
        if policy is None or self.op not in policy.operations:
            raise NotImplementedError(
                f"No migration capability registered for {key!r}/{self.op!r}."
            )
        return policy

    def require_rust_support(self) -> None:
        """Raise unless the registered operation supports this request on Rust."""
        policy = self.policy
        if self.supported:
            return
        raise policy.unsupported_error_type(
            self.unsupported_message
            or policy.unsupported_message
            or f"{self.capability or self.op} cannot honor this request on Rust; "
            "the request will not be sent through legacy Python."
        )

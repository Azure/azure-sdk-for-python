# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared requests for the container operations.

Covers container creation, reading, replacement, and deletion, plus eligibility checks.

A container lives inside a database, so these builders reuse the database
module: the create path needs the parent database id out of the link, and the
eligibility checks defer to the database rules, because a container call carries
the same per-call arguments and reaches the driver through the same
account-level headers.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional, Union

from .._backend.contracts import PreparedRequest
from .._backend.operations import OP_CREATE_CONTAINER, OP_READ_CONTAINER, OP_DELETE_CONTAINER, OP_REPLACE_CONTAINER
from .._base import _validate_resource, build_options, _set_throughput_options
from .._constants import _Constants as Constants
from ..offer import ThroughputProperties

from ._body_wire import serialize_body_to_bytes
from ._request_database import _database_id_from_link, is_read_database_rust_eligible
from ._request_headers import _account_level_headers


RUST_CREATE_CONTAINER_UNSUPPORTED_MESSAGE = (
    "create_container cannot run on the Rust backend for this call because a "
    "per-call setting, request hook, or header override cannot be honored. "
    "Remove the unsupported option. The request will not be sent through legacy Python."
)

RUST_GET_OR_CREATE_CONTAINER_UNSUPPORTED_MESSAGE = (
    "create_container_if_not_exists cannot run on the Rust backend because a "
    "per-call setting, request hook, or header override cannot be honored by both "
    "the read and create steps. Remove the unsupported option. "
    "The request will not be sent through legacy Python."
)

RUST_DELETE_CONTAINER_UNSUPPORTED_MESSAGE = (
    "delete_container cannot run on the Rust backend for this call because a "
    "per-call setting, request hook, or header override cannot be honored. "
    "Remove the unsupported option. The request will not be sent through legacy Python."
)

RUST_REPLACE_CONTAINER_UNSUPPORTED_MESSAGE = (
    "replace_container cannot run on the Rust backend for this call because a "
    "per-call setting, request hook, or header override cannot be honored. "
    "Remove the unsupported option. The request will not be sent through legacy Python."
)

RUST_READ_CONTAINER_UNSUPPORTED_MESSAGE = (
    "ContainerProxy.read cannot run on the Rust backend for this call because a "
    "per-call setting, request hook, or header override cannot be honored. "
    "Remove the unsupported option. The request will not be sent through legacy Python."
)


def parse_container_create_args(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    method_name: str = "create_container",
    target_parameter: str = "id",
) -> tuple[Any, Any]:
    """Bind a container target/id and partition key without expanding the public signature."""
    required = (target_parameter, "partition_key")
    if len(args) > len(required):
        raise TypeError(
            "Unexpected positional parameters for {}(): only '{}' and "
            "'partition_key' may be positional; pass optional settings by keyword.".format(
                method_name, target_parameter
            )
        )
    for name in required[:len(args)]:
        if name in kwargs:
            raise TypeError("{}() got multiple values for argument '{}'".format(method_name, name))
    for name in required[len(args):]:
        if name not in kwargs:
            raise TypeError("{}() missing required argument: '{}'".format(method_name, name))
    return (
        args[0] if args else kwargs.pop(target_parameter),
        args[1] if len(args) > 1 else kwargs.pop("partition_key"),
    )


def validate_container_create_kwargs(
    kwargs: dict[str, Any], *, method_name: str = "create_container"
) -> None:
    """Reject obsolete options and per-call socket timeouts on container operations."""
    for option in ("session_token", "populate_query_metrics"):
        if option in kwargs:
            raise TypeError("{}() does not support the '{}' keyword argument".format(method_name, option))
    if kwargs.pop("read_timeout", None) is not None:
        raise TypeError("{}() does not support the 'read_timeout' keyword argument".format(method_name))


def prepare_container_get_or_create_read(
    kwargs: Mapping[str, Any],
    *,
    initial_headers: Optional[dict[str, str]],
    offer_throughput: Optional[Union[int, ThroughputProperties]],
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """Prepare the existence read and check both legs without consuming create kwargs."""
    read_kwargs = dict(kwargs)
    create_kwargs = dict(kwargs)
    # build_options stamps/mutates supplied options; keep each leg and the caller isolated.
    for working_kwargs in (read_kwargs, create_kwargs):
        for name in ("request_options", "feed_options"):
            if name in working_kwargs:
                working_kwargs[name] = dict(working_kwargs[name])
    if initial_headers is not None:
        read_kwargs["initial_headers"] = initial_headers
    create_kwargs["initial_headers"] = initial_headers
    read_extras = {}
    for name, option in (
        ("populate_partition_key_range_statistics", "populatePartitionKeyRangeStatistics"),
        ("populate_quota_info", "populateQuotaInfo"),
    ):
        value = read_kwargs.pop(name, None)
        if value is not None:
            read_extras[option] = value
    read_options = build_options(read_kwargs)
    read_options.update(read_extras)
    create_options = build_options(create_kwargs)
    read_kwargs.pop("etag", None)
    create_kwargs.pop("etag", None)
    _set_throughput_options(offer=offer_throughput, request_options=create_options)
    rust_eligible = (
        is_read_container_rust_eligible(read_options, read_kwargs)
        and is_create_container_rust_eligible(create_options, create_kwargs)
    )
    return read_options, read_kwargs, rust_eligible


def build_create_container_prepared(
    database_link: Any,
    container_definition: Mapping[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the Rust request that creates a container in a database."""
    _validate_resource(container_definition)
    create_options = dict(request_options)
    create_options.pop("sessionToken", None)
    return PreparedRequest(
        op=OP_CREATE_CONTAINER,
        container_link="",
        body_bytes=serialize_body_to_bytes(container_definition),
        partition_key_header="[]",
        headers=_account_level_headers(create_options, kwargs),
        item_id=_database_id_from_link(database_link),
    )


def is_create_container_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Return whether Rust supports every option on this container create."""
    if request_options.get(Constants.ContainerRID) is not None:
        return False
    return is_read_database_rust_eligible(request_options, operation_kwargs)


def build_read_container_prepared(
    container_link: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the Rust request that reads a container."""
    read_options = dict(request_options)
    read_options.pop("sessionToken", None)
    return PreparedRequest(
        op=OP_READ_CONTAINER,
        container_link=_normalized_container_link(container_link),
        body_bytes=b"",
        partition_key_header="[]",
        headers=_account_level_headers(read_options, kwargs),
    )


def _normalized_container_link(container_link: Any) -> str:
    """Validate and return ``dbs/{db}/colls/{container}``."""
    normalized = str(container_link).strip("/")
    parts = normalized.split("/")
    if len(parts) != 4 or parts[0] != "dbs" or parts[2] != "colls" or not parts[1] or not parts[3]:
        raise ValueError(
            "Failed Parsing ResourceID from link: /{}".format(normalized)
        )
    return normalized


def is_read_container_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Return whether Rust supports every option on this container read."""
    return is_read_database_rust_eligible(request_options, operation_kwargs)


def build_delete_container_prepared(
    container_link: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Pass names to Rust; metadata resolution stays inside the driver."""
    delete_options = dict(request_options)
    delete_options.pop("sessionToken", None)
    return PreparedRequest(
        op=OP_DELETE_CONTAINER,
        container_link=_normalized_container_link(container_link),
        body_bytes=b"",
        partition_key_header="[]",
        headers=_account_level_headers(delete_options, kwargs),
    )


def is_delete_container_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Use the same strict operation-option contract as container creation."""
    return is_create_container_rust_eligible(request_options, operation_kwargs)


def build_replace_container_prepared(
    container_link: Any,
    container_definition: Mapping[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Send the replacement body and names; Rust owns metadata resolution."""
    _validate_resource(container_definition)
    replace_options = dict(request_options)
    replace_options.pop("sessionToken", None)
    return PreparedRequest(
        op=OP_REPLACE_CONTAINER,
        container_link=_normalized_container_link(container_link),
        body_bytes=serialize_body_to_bytes(container_definition),
        partition_key_header="[]",
        headers=_account_level_headers(replace_options, kwargs),
    )

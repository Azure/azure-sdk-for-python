# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared requests for the container operations.

Covers create and read of a container, plus their Rust-eligibility checks.

A container lives inside a database, so these builders reuse the database
module: the create path needs the parent database id out of the link, and both
eligibility checks defer to the database rules, because a container call carries
the same per-call arguments and reaches the driver through the same
account-level headers.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

from .._backend.contracts import PreparedRequest
from .._backend.operations import OP_CREATE_CONTAINER, OP_READ_CONTAINER
from .._base import _validate_resource
from .._constants import _Constants as Constants

from ._body_wire import serialize_body_to_bytes
from ._request_database import _database_id_from_link, is_read_database_rust_eligible
from ._request_headers import _account_level_headers


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
    if request_options.get("populatePartitionKeyRangeStatistics") is not None:
        return False
    if request_options.get("populateQuotaInfo") is not None:
        return False
    return is_read_database_rust_eligible(request_options, operation_kwargs)

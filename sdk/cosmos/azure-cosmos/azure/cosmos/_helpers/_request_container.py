# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared requests for container operations without sending them.

Covers container creation, reading, replacement, and deletion, plus eligibility checks.

A container lives inside a database, so these builders reuse the database
module: the create path needs the parent database id out of the link, and the
eligibility checks defer to the database rules, because a container call carries
the same supported per-call arguments. Request headers and typed settings are
prepared together; the binding and Rust driver perform metadata resolution.
"""
from __future__ import annotations

import time
from typing import Any, Mapping, Optional, Union

from .._backend.contracts import PreparedRequest
from .._backend.capabilities import OperationRouting
from .._backend.operations import OP_CREATE_CONTAINER, OP_READ_CONTAINER, OP_DELETE_CONTAINER, OP_REPLACE_CONTAINER
from .._backend.partition_key_input import BindingPartitionKey
from .._base import _validate_resource, build_options, _set_throughput_options
from .._constants import _Constants as Constants
from ..offer import ThroughputProperties
from ._request_database import _database_id_from_link, is_read_database_rust_eligible
from ._request_settings import OPTION_HEADER_NAMES, account_request_settings, build_customer_headers
from ._wire_encoding import serialize_body_to_bytes


def parse_container_create_args(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    method_name: str = "create_container",
    target_parameter: str = "id",
) -> tuple[Any, Any]:
    """Bind a container target/id and partition key without expanding the public signature.

    :param tuple args: Positional target and partition key supplied by the caller.
    :param dict kwargs: Keyword arguments; bound required arguments are removed.
    :keyword str method_name: Operation name used in argument errors.
    :keyword str target_parameter: Name of the required container target argument.
    :return: The container target and partition key.
    :rtype: tuple
    """
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
    """Reject obsolete options on container operations.

    :param dict kwargs: Creation keywords to inspect without consuming them.
    :keyword str method_name: Operation name used in the error.
    :return: None.
    :rtype: None
    """
    for option in ("session_token", "populate_query_metrics"):
        if option in kwargs:
            raise TypeError("{}() does not support the '{}' keyword argument".format(method_name, option))


def validate_container_retry_write_kwargs(
    kwargs: Mapping[str, Any], operation: str
) -> None:
    """Reject Rust write-retry overrides before reading or deleting a container.

    :param Mapping[str, Any] kwargs: Call keywords, including nested request or feed options.
    :param str operation: Operation name used in the error.
    :return: None.
    :rtype: None
    """
    for options in (kwargs, kwargs.get("request_options"), kwargs.get("feed_options")):
        if (
            isinstance(options, Mapping)
            and options.get(Constants.Kwargs.RETRY_WRITE) is not None
        ):
            raise TypeError(
                f"{operation}() does not support retry_write; "
                "omit this option or pass None. The Rust driver manages write retries."
            )


def prepare_container_get_or_create_read(
    kwargs: Mapping[str, Any],
    *,
    initial_headers: Optional[dict[str, str]],
    offer_throughput: Optional[Union[int, ThroughputProperties]],
) -> tuple[dict[str, Any], dict[str, Any], bool, Optional[float]]:
    """Preflight both legs and give supported calls one read-and-create deadline.

    :param Mapping[str, Any] kwargs: Caller options copied separately for the read and creation.
    :keyword dict[str, str] or None initial_headers: Header overrides applied to both operations.
    :keyword int or azure.cosmos.ThroughputProperties or None offer_throughput: Creation throughput.
    :return: Read options, remaining read keywords, Rust eligibility, and the monotonic deadline.
    :rtype: tuple[dict, dict, bool, float or None]
    """
    started = time.monotonic()
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
    timeout = read_kwargs.get("timeout")
    # Unsupported inputs keep the existing preflight error, not a conversion error.
    deadline = started + float(timeout) if rust_eligible and timeout is not None else None
    return read_options, read_kwargs, rust_eligible, deadline


def container_creation_read_options(
    request_options: Mapping[str, Any],
) -> dict[str, Any]:
    """Preserve read settings without replaying creation conditions or provisioning.

    :param Mapping[str, Any] request_options: Creation options, left unchanged.
    :return: Options with creation-only settings and headers removed.
    :rtype: dict[str, Any]
    """
    create_only = {
        "accessCondition",
        "responsePayloadOnWriteDisabled",
        Constants.Kwargs.RETRY_WRITE,
        "offerThroughput",
        "autoUpgradePolicy",
        "offerType",
        "offerEnableRUPerMinuteThroughput",
    }
    create_headers = {"if-match", "if-none-match"} | {
        OPTION_HEADER_NAMES[name] for name in create_only if name in OPTION_HEADER_NAMES
    }
    read_options = {
        name: value
        for name, value in request_options.items()
        if name not in create_only and name.lower() not in create_headers
    }
    if "initialHeaders" in read_options:
        read_options["initialHeaders"] = {
            name: value
            for name, value in build_customer_headers(
                read_options["initialHeaders"]
            ).items()
            if name not in create_headers
        }
    return read_options


def build_create_container_prepared(
    database_link: Any,
    container_definition: Mapping[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build a prepared request to create a container in its parent database.

    :param Any database_link: Parent database link in ``dbs/{id}`` form.
    :param Mapping[str, Any] container_definition: Container properties to validate and serialize.
    :param Mapping[str, Any] request_options: Internal request options to translate.
    :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords, including timeout.
    :return: The serialized container creation request.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
    _validate_resource(container_definition)
    create_options = dict(request_options)
    create_options.pop("sessionToken", None)
    headers, settings = account_request_settings(create_options, kwargs)
    return PreparedRequest(
        op=OP_CREATE_CONTAINER,
        container_link="",
        body_bytes=serialize_body_to_bytes(container_definition),
        partition_key=BindingPartitionKey("cross_partition"),
        headers=headers,
        settings=settings,
        item_id=_database_id_from_link(database_link),
    )


def preflight_create_container(
    database_link: Any,
    container_definition: Mapping[str, Any],
    request_options: Mapping[str, Any],
    kwargs: Mapping[str, Any],
) -> PreparedRequest:
    """Prepare creation before a GSI source lookup, without sending a request.

    :param Any database_link: Parent database link in ``dbs/{id}`` form.
    :param Mapping[str, Any] container_definition: Container properties to validate and serialize.
    :param Mapping[str, Any] request_options: Internal creation options checked for Rust support.
    :param Mapping[str, Any] kwargs: Remaining operation keywords checked for Rust support.
    :return: The prepared creation request after eligibility validation.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
    OperationRouting(
        OP_CREATE_CONTAINER, is_create_container_rust_eligible(request_options, kwargs)
    ).require_rust_support()
    return build_create_container_prepared(database_link, container_definition, request_options, kwargs=kwargs)


def _is_container_mutation_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Reject an explicit RID and apply the shared database-request eligibility checks.

    :param Mapping[str, Any] request_options: Internal options to check, including a possible container RID.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Whether the options can be represented by the Rust request.
    :rtype: bool
    """
    if request_options.get(Constants.ContainerRID) is not None:
        return False
    return is_read_database_rust_eligible(request_options, operation_kwargs)


def is_create_container_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Apply the shared container-mutation option checks to creation.

    :param Mapping[str, Any] request_options: Internal creation options to check.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Whether the creation options can be represented by Rust.
    :rtype: bool
    """
    return _is_container_mutation_rust_eligible(request_options, operation_kwargs)


def build_read_container_prepared(
    container_link: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build a prepared request to read a container's properties.

    :param Any container_link: Container link in ``dbs/{db}/colls/{container}`` form.
    :param Mapping[str, Any] request_options: Internal read options to translate.
    :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords, including timeout.
    :return: The container read request with a normalized link.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
    read_options = dict(request_options)
    validate_container_retry_write_kwargs(read_options, "ContainerProxy.read")
    read_options.pop("sessionToken", None)
    headers, settings = account_request_settings(read_options, kwargs)
    return PreparedRequest(
        op=OP_READ_CONTAINER,
        container_link=_normalized_container_link(container_link),
        body_bytes=b"",
        partition_key=BindingPartitionKey("cross_partition"),
        headers=headers,
        settings=settings,
    )


def _normalized_container_link(container_link: Any) -> str:
    """Validate and return ``dbs/{db}/colls/{container}``.

    :param Any container_link: Link to stringify and validate.
    :return: The container link without leading or trailing slashes.
    :rtype: str
    """
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
    """Apply the shared database-request eligibility checks to a container read.

    :param Mapping[str, Any] request_options: Internal read options to check.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Whether the read options can be represented by Rust.
    :rtype: bool
    """
    return is_read_database_rust_eligible(request_options, operation_kwargs)


def build_delete_container_prepared(
    container_link: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build a named container's delete request without resolving service metadata.

    :param Any container_link: Container link in ``dbs/{db}/colls/{container}`` form.
    :param Mapping[str, Any] request_options: Internal delete options to translate.
    :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords, including timeout.
    :return: The container deletion request with a normalized link.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
    delete_options = dict(request_options)
    delete_options.pop("sessionToken", None)
    headers, settings = account_request_settings(delete_options, kwargs)
    return PreparedRequest(
        op=OP_DELETE_CONTAINER,
        container_link=_normalized_container_link(container_link),
        body_bytes=b"",
        partition_key=BindingPartitionKey("cross_partition"),
        headers=headers,
        settings=settings,
    )


def is_delete_container_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Apply the shared container-mutation option checks to deletion.

    :param Mapping[str, Any] request_options: Internal delete options to check.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Whether the deletion options can be represented by Rust.
    :rtype: bool
    """
    return _is_container_mutation_rust_eligible(request_options, operation_kwargs)


def build_replace_container_prepared(
    container_link: Any,
    container_definition: Mapping[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build a replacement request with body bytes; do not send or resolve metadata.

    :param Any container_link: Container link in ``dbs/{db}/colls/{container}`` form.
    :param Mapping[str, Any] container_definition: Replacement properties to validate and serialize.
    :param Mapping[str, Any] request_options: Internal replacement options to translate.
    :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords, including timeout.
    :return: The container replacement request with serialized properties.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
    _validate_resource(container_definition)
    replace_options = dict(request_options)
    replace_options.pop("sessionToken", None)
    headers, settings = account_request_settings(replace_options, kwargs)
    return PreparedRequest(
        op=OP_REPLACE_CONTAINER,
        container_link=_normalized_container_link(container_link),
        body_bytes=serialize_body_to_bytes(container_definition),
        partition_key=BindingPartitionKey("cross_partition"),
        headers=headers,
        settings=settings,
    )


def is_replace_container_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Apply the shared container-mutation option checks to replacement.

    :param Mapping[str, Any] request_options: Internal replacement options to check.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Whether the replacement options can be represented by Rust.
    :rtype: bool
    """
    return _is_container_mutation_rust_eligible(request_options, operation_kwargs)

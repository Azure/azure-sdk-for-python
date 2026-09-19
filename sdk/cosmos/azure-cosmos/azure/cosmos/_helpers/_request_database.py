# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared requests for the database operations.

Covers create, read and delete of a database, plus the checks that decide
whether a given call can run on the Rust path at all. A database is
account-scoped, so these requests carry no partition key and no container link.

The eligibility predicates screen known unsupported settings before dispatch.
They do not prove service acceptance or exhaustively validate arbitrary internal
option mappings. The caller's migration policy decides how to handle ineligibility.
"""
from __future__ import annotations

import json
import time
from copy import deepcopy

from .._backend.partition_key import PartitionKeyInput

from typing import Any, Dict, Mapping, Optional

from .._backend.contracts import PreparedRequest
from .._backend.operations import OP_CREATE_DATABASE, OP_DELETE_DATABASE, OP_READ_DATABASE
from .._constants import _Constants as Constants
from ..offer import ThroughputProperties
from ._resource_validation import validate_resource

from ._request_settings import (
    account_request_settings,
    build_customer_headers,
    compose_options_from_kwargs,
    OPTION_HEADER_NAMES,
    _timeout_is_representable,
    is_supported_operation_timeout,
    overrides_driver_owned_header,
)
from ._wire_encoding import serialize_body_to_bytes


# The only per-call keyword arguments a database read can carry onto the Rust
# path. ``timeout`` becomes the normalized ``timeout_seconds`` request option;
# ``response_hook`` is invoked by the coordinator after the response is parsed,
# so it never has to reach the binding. Anything else -- ``connection_timeout``,
# ``raw_request_hook``, ``raw_response_hook`` -- is consumed by the legacy
# azure-core pipeline, which the Rust path does not run, so its presence rejects
# the Rust read instead of dropping it (see
# ``is_read_database_rust_eligible``).
_RUST_READ_DATABASE_SUPPORTED_KWARGS = frozenset({
    Constants.Kwargs.TIMEOUT,
    "response_hook",
})

_CREATE_DATABASE_OPTIONS = frozenset({
    "initialHeaders", "offerThroughput", "autoUpgradePolicy", "throughputBucket",
    "priorityLevel", "excludedLocations", "availabilityStrategy",
    "correlatedActivityId", "contentType",
})
_CREATE_DATABASE_OWNED_HEADERS = frozenset({
    "accept", "cache-control", "user-agent", "x-ms-version", "x-ms-client-id",
    "x-ms-cosmos-sdk-supportedcapabilities", "authorization", "x-ms-date",
})
_CREATE_DATABASE_INAPPLICABLE_HEADERS = frozenset(
    header for option, header in OPTION_HEADER_NAMES.items()
    if option not in _CREATE_DATABASE_OPTIONS
) | {"if-match", "if-none-match", "prefer", "x-ms-documentdb-partitionkey"}


def prepare_create_database_options(
    kwargs: dict[str, Any], offer: Optional[int | ThroughputProperties],
    *, operation_name: str = "create_database", allow_read_timeout: bool = False,
) -> tuple[dict[str, Any], Optional[float]]:
    """Snapshot creation inputs and establish one budget before driver setup."""
    started = time.monotonic()
    for name in ("populate_query_metrics", "session_token", "etag", "match_condition"):
        if name in kwargs:
            raise TypeError(f"{operation_name}() does not support the '{name}' keyword argument")
    feed_options = kwargs.pop("feed_options", {})
    if "request_options" not in kwargs:
        kwargs["request_options"] = feed_options
    options = deepcopy(compose_options_from_kwargs(kwargs))
    # Get-or-create retains this option for explicitly selected legacy transport.
    # Its Rust eligibility check rejects it before the existence read.
    if not allow_read_timeout:
        for source in (kwargs, options):
            if source.pop("read_timeout", None) is not None:
                raise TypeError(f"{operation_name}() does not support the 'read_timeout' keyword argument")
    timeout = kwargs.get("timeout", options.pop("timeout", None))
    if not is_supported_operation_timeout(timeout):
        raise ValueError(f"{operation_name} timeout must be None or a finite number of seconds >= 1 and < 2**64.")
    if timeout is not None or "timeout" in kwargs:
        kwargs["timeout"] = timeout
    if offer is not None:
        options.pop("offerThroughput", None)
        options.pop("autoUpgradePolicy", None)
        if isinstance(offer, bool):
            raise TypeError("offer_throughput must be int or ThroughputProperties, not bool")
        if isinstance(offer, int):
            options["offerThroughput"] = offer
        elif isinstance(offer, ThroughputProperties):
            manual = offer.offer_throughput
            maximum = offer.auto_scale_max_throughput
            increment = offer.auto_scale_increment_percent
            if manual is not None and maximum is not None:
                raise ValueError("Specify manual throughput or autoscale, not both.")
            if maximum is not None:
                autoscale: dict[str, Any] = {"maxThroughput": maximum}
                if increment is not None:
                    autoscale["autoUpgradePolicy"] = {"throughputPolicy": {"incrementPercent": increment}}
                options["autoUpgradePolicy"] = json.dumps(autoscale)
            elif increment is not None:
                raise ValueError("auto_scale_max_throughput is required with auto_scale_increment_percent")
            elif manual is not None:
                options["offerThroughput"] = manual
            else:
                raise ValueError("ThroughputProperties must specify manual throughput or an autoscale maximum.")
        else:
            raise TypeError("offer_throughput must be int or ThroughputProperties")
    initial = build_customer_headers(options.get("initialHeaders"))
    has_manual = options.get("offerThroughput") is not None or "x-ms-offer-throughput" in initial
    has_autoscale = (
        options.get("autoUpgradePolicy") is not None
        or "x-ms-cosmos-offer-autopilot-settings" in initial
    )
    if has_manual and has_autoscale:
        raise ValueError("Specify manual throughput or autoscale, not both.")
    return options, None if timeout is None else started + float(timeout)


def database_existence_read_options(
    request_options: Mapping[str, Any], operation_kwargs: Mapping[str, Any],
) -> dict[str, Any]:
    """Keep creation settings off existence reads and reject conditional results."""
    headers = build_customer_headers(request_options.get("initialHeaders"))
    if (
        "accessCondition" in request_options
        or {"if_match", "if_none_match"}.intersection(operation_kwargs)
        or {"if-match", "if-none-match"}.intersection(headers)
    ):
        raise TypeError("create_database_if_not_exists() does not support conditional headers or access conditions")
    read_options = dict(request_options)
    read_options.pop("offerThroughput", None)
    read_options.pop("autoUpgradePolicy", None)
    if "initialHeaders" in read_options:
        read_options["initialHeaders"] = {
            name: value for name, value in headers.items()
            if name not in {"x-ms-offer-throughput", "x-ms-cosmos-offer-autopilot-settings"}
        }
    return read_options


def is_create_database_rust_eligible(
    request_options: Mapping[str, Any], operation_kwargs: Mapping[str, Any],
) -> bool:
    """Reject settings that cannot describe an account-level creation request."""
    if set(operation_kwargs).difference({"timeout"}):
        return False
    if set(request_options).difference(_CREATE_DATABASE_OPTIONS):
        return False
    initial = request_options.get("initialHeaders")
    if isinstance(initial, Mapping) and any(
        isinstance(name, str) and name.lower() in (
            _CREATE_DATABASE_OWNED_HEADERS | _CREATE_DATABASE_INAPPLICABLE_HEADERS
        )
        for name in initial
    ):
        return False
    return is_supported_operation_timeout(operation_kwargs.get("timeout"))


def build_create_database_prepared(
    database: Dict[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the account-level create-database request consumed by the Rust backend."""
    validate_resource(database)
    headers, settings = account_request_settings(request_options, kwargs)
    manual = settings.resource.offer_throughput is not None or "x-ms-offer-throughput" in headers
    autoscale = (
        settings.resource.autoscale_settings is not None
        or "x-ms-cosmos-offer-autopilot-settings" in headers
    )
    if manual and autoscale:
        raise ValueError("Specify manual throughput or autoscale, not both.")
    return PreparedRequest(
        op=OP_CREATE_DATABASE,
        container_link="",
        body_bytes=serialize_body_to_bytes(database),
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
        item_id=database["id"],
    )


def build_read_database_prepared(
    database_id: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the account-level read-database request consumed by the Rust backend.

    Two callers: ``DatabaseProxy.read`` and the existence check inside
    ``create_database_if_not_exists``. Without it a Rust-backed client has to
    run both of those on the legacy transport, because there is no Rust request
    to send.
    """
    read_options = dict(request_options)
    # Database reads are master-resource requests. The legacy session layer never
    # attaches a session token to them (``_base._is_session_token_request`` returns
    # False for a master resource), and ``_base.GetHeaders`` suppresses
    # x-ms-cosmos-intended-collection-rid when resource_type == 'dbs'. Drop both so
    # the Rust request carries the same headers the legacy request would.
    read_options.pop("sessionToken", None)
    read_options.pop(Constants.ContainerRID, None)
    normalized_database_id = str(database_id).rstrip("/")
    if not normalized_database_id:
        # Match the legacy link parser instead of sending an account-level
        # ``/dbs/`` request that fails later with a different service error.
        raise ValueError("Failed Parsing ResourceID from link: /dbs/")
    headers, settings = account_request_settings(read_options, kwargs)
    return PreparedRequest(
        op=OP_READ_DATABASE,
        container_link="",
        body_bytes=b"",
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
        # The legacy path routes the id through ``base.GetPathFromLink`` /
        # ``GetResourceIdOrFullNameFromLink``, which tolerate a trailing slash
        # ("dbs/mydb/" reads database "mydb"). The binding takes the bare name and
        # builds the path itself, so strip the slash here to keep the two paths
        # reading the same database.
        item_id=normalized_database_id,
    )


def is_read_database_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Screen database-read options for known Rust representation limits.

    The single definition of "representable" for a database read, shared by
    ``DatabaseProxy.read`` and the existence check in
    ``create_database_if_not_exists``. Both ask the same question, so they must
    not answer it differently: the same call would otherwise run on Rust in one
    method and on legacy Python in the other, honoring a different set of the
    caller's options each time.

    Returns ``False`` when the caller asked for
    something the Rust path would drop without saying so:

    * ``read_timeout`` -- a socket-level timeout. The Rust path has no
      per-request equivalent; the driver takes its read timeout from the client
      configuration.
    * any operation kwarg outside ``_RUST_READ_DATABASE_SUPPORTED_KWARGS`` --
      for example ``connection_timeout`` or ``raw_request_hook``, which the
      legacy azure-core pipeline consumes and the Rust path never sees.
    * a ``timeout`` that is not a finite, non-boolean numeric duration of at least
      one second within Rust's duration range.
    * ``initial_headers`` containing a standard header the driver always
      overwrites. The legacy pipeline preserves those caller overrides.

    Without this check the read would run on Rust regardless, and these options
    would be accepted and then quietly not applied. A customer who
    sets ``timeout=0.5`` to fail fast would wait a full second and have no way to
    tell from logs that their number was replaced.

    :param request_options: The internal options dict for this read.
    :type request_options: Mapping[str, Any]
    :param operation_kwargs: The kwargs left over after ``build_options``.
    :type operation_kwargs: Mapping[str, Any]
    :returns: ``True`` when the known timeout, kwarg, and header checks pass.
    :rtype: bool
    """
    timeout = operation_kwargs.get(Constants.Kwargs.TIMEOUT)
    option_timeout = request_options.get(Constants.Kwargs.TIMEOUT)
    # The prepared request forwards kwargs, not a timeout supplied only in options.
    if option_timeout is not None and option_timeout != timeout:
        return False
    return _database_request_options_are_supported(request_options, operation_kwargs) and (
        is_supported_operation_timeout(timeout)
    )


def _database_request_options_are_supported(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    if (
        request_options.get(Constants.Kwargs.READ_TIMEOUT) is not None
        or operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT) is not None
    ):
        return False
    if set(operation_kwargs).difference(_RUST_READ_DATABASE_SUPPORTED_KWARGS):
        return False
    if overrides_driver_owned_header(request_options):
        return False
    return True


def build_delete_database_prepared(
    database_link: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the Rust request that deletes a database."""
    delete_options = dict(request_options)
    # Same suppression as the read: a database is a master resource, so the legacy
    # session layer attaches no session token and ``_base.GetHeaders`` drops
    # x-ms-cosmos-intended-collection-rid when resource_type == 'dbs'.
    delete_options.pop("sessionToken", None)
    delete_options.pop(Constants.ContainerRID, None)
    database_id = _database_id_from_link(database_link)
    headers, settings = account_request_settings(delete_options, kwargs)
    return PreparedRequest(
        op=OP_DELETE_DATABASE,
        container_link="",
        body_bytes=b"",
        partition_key=PartitionKeyInput("cross_partition"),
        headers=headers,
        settings=settings,
        item_id=database_id,
    )


def _database_id_from_link(database_link: Any) -> str:
    """Return the database name from a ``dbs/{id}`` link."""
    normalized = str(database_link).strip("/")
    if not normalized.startswith("dbs/"):
        # Every caller reaches this through ``_get_database_link``, which always
        # emits ``dbs/{id}``. Anything else -- including a bare ``dbs`` -- means the
        # id is missing, so refuse rather than deleting a database named "dbs".
        raise ValueError("Failed Parsing ResourceID from link: /{}/".format(normalized))
    normalized = normalized[len("dbs/"):].strip("/")
    if not normalized:
        raise ValueError("Failed Parsing ResourceID from link: /dbs/")
    return normalized


def is_delete_database_rust_eligible(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> bool:
    """Keep deletion's existing deadline policy while sharing option checks."""
    return _database_request_options_are_supported(request_options, operation_kwargs) and (
        _timeout_is_representable(operation_kwargs)
    )

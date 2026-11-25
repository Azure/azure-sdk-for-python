# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared requests for the database operations.

Covers create, read and delete of a database, plus the checks that decide
whether a given call can run on the Rust path at all. A database is
account-scoped, so these requests carry no item partition-key value and use
an empty container link. The shared record's partition-key field is unused
by database binding calls.

The eligibility predicates screen known unsupported settings before execution.
They do not prove service acceptance or exhaustively validate arbitrary internal
option mappings. The caller's migration policy decides how to handle ineligibility.
"""
from __future__ import annotations

import json
import time
from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from .._backend.capabilities import OperationRouting
from .._backend.contracts import PreparedRequest
from .._backend.operations import OP_CREATE_DATABASE, OP_DELETE_DATABASE, OP_READ_DATABASE
from .._backend.partition_key_input import BindingPartitionKey
from .._backend.request_settings import ResourceSettings
from .._constants import _Constants as Constants
from ..offer import ThroughputProperties
from ._client_context import ClientOperationDefaults
from ._request_settings import (
    account_request_settings,
    build_customer_headers,
    compose_options_from_kwargs,
    HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE,
    OPTION_FIELDS,
    OPTION_HEADER_NAMES,
    is_supported_operation_timeout,
    reject_unsupported_feed_options,
    validate_operation_timeout,
)
from ._resource_validation import validate_resource
from ._wire_encoding import serialize_body_to_bytes


# The only per-call keyword arguments a database read can carry onto the Rust
# path. ``timeout`` becomes the normalized ``timeout_seconds`` request option;
# ``response_hook`` is invoked by the coordinator after the response is parsed,
# so it never has to reach the binding. Other legacy settings, such as
# ``connection_timeout``, cannot govern the Rust transport, so their presence
# rejects the Rust read instead of dropping them (see
# ``is_read_database_rust_eligible``).
_RUST_READ_DATABASE_SUPPORTED_KWARGS = frozenset({
    Constants.Kwargs.TIMEOUT,
    "response_hook",
    # Metadata preload forwards this internal timestamp; it is not a wire setting.
    Constants.OperationStartTime,
    # Azure Core handles these controls; they are not driver settings.
    "tracing_options",
    "tracing_attributes",
})

_CREATE_DATABASE_OPTIONS = frozenset({
    "initialHeaders", "offerThroughput", "autoUpgradePolicy", "throughputBucket",
    "priorityLevel", "excludedLocations", "availabilityStrategy",
    "correlatedActivityId", "contentType",
})
_CREATE_DATABASE_QUERY_OPTIONS = frozenset(
    option for option, (group, _) in OPTION_FIELDS.items() if group == "query"
)
_CREATE_DATABASE_INAPPLICABLE_HEADERS = frozenset(
    header for option, header in OPTION_HEADER_NAMES.items()
    if option not in _CREATE_DATABASE_OPTIONS
) | {"if-match", "if-none-match", "prefer", "x-ms-documentdb-partitionkey"}


def prepare_create_database_options(
    kwargs: dict[str, Any], offer: Optional[int | ThroughputProperties],
    *, operation_name: str = "create_database",
    defaults: Optional[ClientOperationDefaults] = None,
) -> tuple[dict[str, Any], Optional[float]]:
    """Snapshot creation inputs and establish one budget before driver setup.

    :param dict[str, Any] kwargs: Working call keywords, consumed and normalized in place.
    :param int or azure.cosmos.ThroughputProperties or None offer: Explicit creation throughput.
    :keyword str operation_name: Operation name used in validation errors.
    :keyword ClientOperationDefaults or None defaults: Client defaults applied after validation.
    :return: Validated creation options and an optional monotonic deadline.
    :rtype: tuple[dict, float or None]
    """
    started = time.monotonic()
    for name in ("populate_query_metrics", "session_token", "etag", "match_condition"):
        if name in kwargs:
            raise TypeError(f"{operation_name}() does not support the '{name}' keyword argument")
    feed_options = kwargs.pop("feed_options", {})
    if "request_options" not in kwargs:
        kwargs["request_options"] = feed_options
    options = deepcopy(compose_options_from_kwargs(kwargs))
    if "connection_timeout" in kwargs or "connection_timeout" in options:
        raise TypeError(
            f"{operation_name}() does not accept per-call connection_timeout; "
            "configure ConnectionPoolOptions.connection_timeout on the client's CosmosRuntime instead."
        )
    if Constants.Kwargs.RETRY_WRITE in options:
        raise TypeError(
            f"{operation_name}() does not accept retry_write; the Rust driver manages write retries."
        )
    if "responsePayloadOnWriteDisabled" in options or "no_response" in options:
        raise TypeError(
            f"{operation_name}() does not accept no_response; full database properties are required."
        )
    for name in options:
        if name in _CREATE_DATABASE_QUERY_OPTIONS:
            raise TypeError(f"{operation_name}() does not support query or paging option '{name}'")
    reject_unsupported_feed_options(
        operation_name,
        kwargs.keys() - {"timeout", "tracing_options", "tracing_attributes"},
        options,
    )
    timeout = kwargs.get("timeout", options.pop("timeout", None))
    if not is_supported_operation_timeout(timeout):
        raise ValueError(f"{operation_name} timeout must be None or a finite number of seconds >= 1 and < 2**64.")
    if timeout is not None or "timeout" in kwargs:
        kwargs["timeout"] = timeout
    _apply_creation_throughput(options, offer)
    initial = build_customer_headers(options.get("initialHeaders"))
    _validate_creation_headers(options, initial, operation_name)
    # Reads omit these fields, so their local validation must happen before the
    # workflow can return an existing database without preparing creation.
    throughput = ResourceSettings(
        offer_throughput=options.get("offerThroughput"),
        autoscale_settings=options.get("autoUpgradePolicy"),
    )
    if throughput.offer_throughput is not None and not -(2**63) <= throughput.offer_throughput < 2**63:
        raise ValueError("offer_throughput must fit a signed 64-bit integer.")
    if "initialHeaders" in options:
        options = {
            "initialHeaders": initial,
            **{key: value for key, value in options.items() if key != "initialHeaders"},
        }
    if defaults is not None:
        defaults.apply_to_options(options)
    return options, None if timeout is None else started + float(timeout)


def _apply_creation_throughput(
    options: dict[str, Any], offer: Optional[int | ThroughputProperties],
) -> None:
    """Replace provisioning options with explicitly supplied throughput.

    :param dict[str, Any] options: Working creation options updated in place.
    :param int or azure.cosmos.ThroughputProperties or None offer: Explicit throughput, or None to retain options.
    :return: None.
    :rtype: None
    """
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
            for name, value in (
                ("auto_scale_max_throughput", maximum),
                ("auto_scale_increment_percent", increment),
            ):
                # Only builtin integers are accepted; bool and int subclasses are intentionally excluded.
                if value is not None and type(value) is not int:  # pylint: disable=unidiomatic-typecheck
                    raise TypeError(f"{name} must be an integer, not a boolean or another type.")
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


def _validate_creation_headers(
    options: Mapping[str, Any], initial: Mapping[str, Any], operation_name: str,
) -> None:
    """Reject unsupported creation settings and conflicting provisioning headers.

    :param Mapping[str, Any] options: Internal creation options to validate.
    :param Mapping[str, Any] initial: Normalized customer header overrides.
    :param str operation_name: Operation name used in validation errors.
    :return: None.
    :rtype: None
    """
    if "prefer" in initial or any(isinstance(name, str) and name.lower() == "prefer" for name in options):
        raise TypeError(
            f"{operation_name}() does not accept the Prefer header; full database properties are required."
        )
    unsupported_options = options.keys() - _CREATE_DATABASE_OPTIONS
    if unsupported_options:
        names = ", ".join(sorted(repr(name) for name in unsupported_options))
        raise TypeError(
            f"{operation_name}() does not support request option(s): {names}; remove these options."
        )
    unsupported_headers = initial.keys() & _CREATE_DATABASE_INAPPLICABLE_HEADERS
    if unsupported_headers:
        names = ", ".join(repr(name) for name in sorted(unsupported_headers))
        raise TypeError(
            f"{operation_name}() does not support initial_headers entry(s): {names}; remove these headers."
        )
    has_manual = options.get("offerThroughput") is not None or "x-ms-offer-throughput" in initial
    has_autoscale = (
        options.get("autoUpgradePolicy") is not None
        or "x-ms-cosmos-offer-autopilot-settings" in initial
    )
    if has_manual and has_autoscale:
        raise ValueError("Specify manual throughput or autoscale, not both.")


def database_existence_read_options(
    request_options: Mapping[str, Any], operation_kwargs: Mapping[str, Any],
) -> dict[str, Any]:
    """Keep creation settings off existence reads and reject conditional results.

    :param Mapping[str, Any] request_options: Internal creation options, left unchanged.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords checked for conditions.
    :return: Read options without throughput provisioning settings or headers.
    :rtype: dict[str, Any]
    """
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
    """Reject settings that cannot describe an account-level creation request.

    A bad timeout raises ``ValueError``; it is a wrong value, not a Rust limit.

    :param Mapping[str, Any] request_options: Internal creation options to check.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Whether Rust can represent these account-level creation settings.
    :rtype: bool
    """
    validate_operation_timeout(operation_kwargs.get("timeout"))
    # Azure Core owns tracing controls; they are not native request settings.
    if set(operation_kwargs).difference({"timeout", "tracing_options", "tracing_attributes"}):
        return False
    if set(request_options).difference(_CREATE_DATABASE_OPTIONS):
        return False
    initial = request_options.get("initialHeaders")
    if isinstance(initial, Mapping) and any(
        isinstance(name, str) and name.lower() in _CREATE_DATABASE_INAPPLICABLE_HEADERS
        for name in initial
    ):
        return False
    return True


def build_create_database_prepared(
    database: Dict[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the account-level prepared request consumed by BindingAdapter.

    :param dict[str, Any] database: Database properties containing the resource ID.
    :param Mapping[str, Any] request_options: Internal creation options to translate.
    :keyword Mapping[str, Any] or None kwargs: Remaining call keywords, including timeout.
    :return: The account-level request with serialized database properties.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
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
        partition_key=BindingPartitionKey("cross_partition"),
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
    """Build an account-level prepared request to read a database.

    ``DatabaseProxy.read`` and ``create_database_if_not_exists`` use this same
    builder. For database "checkout", item_id holds "checkout" and container_link
    is empty. The builder performs no existence check or network I/O.

    :param Any database_id: Database name to stringify and normalize.
    :param Mapping[str, Any] request_options: Internal read options to translate.
    :keyword Mapping[str, Any] or None kwargs: Remaining call keywords, including timeout.
    :return: The account-level read request with a normalized database ID.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
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
        partition_key=BindingPartitionKey("cross_partition"),
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

    Applies to standalone ``DatabaseProxy.read``. The existence read in
    ``create_database_if_not_exists`` uses the creation contract, which allows
    driver-owned header overrides on both steps with driver values taking
    precedence.

    Returns ``False`` when the caller asked for
    something the Rust path would drop without saying so:

    * any operation kwarg outside ``_RUST_READ_DATABASE_SUPPORTED_KWARGS`` --
      for example ``connection_timeout``, which the
      legacy azure-core pipeline consumes and the Rust path never sees.
    * ``initial_headers`` containing a standard header the driver always
      overwrites. The legacy pipeline preserves those caller overrides.

    A ``timeout`` that is not None or a finite, non-boolean number of seconds
    from 1 up to 2**64 raises ``ValueError`` instead, because it is a wrong value
    rather than something Rust cannot do. For example, ``timeout=0.5`` raises
    ``ValueError``. Eligibility is not permission
    to retry a failed operation through the legacy path.

    :param request_options: The internal options dict for this read.
    :type request_options: Mapping[str, Any]
    :param operation_kwargs: The kwargs left over after ``build_options``.
    :type operation_kwargs: Mapping[str, Any]
    :returns: ``True`` when the kwarg and header checks pass.
    :rtype: bool
    :raises ValueError: If ``timeout`` is not a supported number of seconds.
    """
    return _database_request_options_error(request_options, operation_kwargs) is None


def read_database_routing(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> OperationRouting:
    """Keep argument-specific rejection messages on the Rust database-read path.

    :param Mapping[str, Any] request_options: Internal read options to check.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Read routing with an explanatory message for unsupported arguments.
    :rtype: ~azure.cosmos._backend.capabilities.OperationRouting
    """
    error = _database_request_options_error(request_options, operation_kwargs)
    return OperationRouting(
        OP_READ_DATABASE,
        error is None,
        unsupported_message=f"DatabaseProxy.read() {error}" if error is not None else None,
    )


def _database_request_options_error(
    request_options: Mapping[str, Any],
    operation_kwargs: Mapping[str, Any],
) -> Optional[str]:
    timeout = operation_kwargs.get(Constants.Kwargs.TIMEOUT)
    validate_operation_timeout(timeout)
    option_timeout = request_options.get(Constants.Kwargs.TIMEOUT)
    # The prepared request forwards kwargs, not a timeout supplied only in options.
    if option_timeout is not None and option_timeout != timeout:
        return "does not accept timeout inside an options dictionary; pass timeout directly to read()."
    if "connection_timeout" in operation_kwargs:
        return (
            "does not accept per-call connection_timeout; configure "
            "ConnectionPoolOptions.connection_timeout on the client's CosmosRuntime instead."
        )
    unsupported_kwargs = set(operation_kwargs).difference(_RUST_READ_DATABASE_SUPPORTED_KWARGS)
    if unsupported_kwargs:
        names = ", ".join(sorted(repr(name) for name in unsupported_kwargs))
        return f"does not support keyword argument(s): {names}; remove these arguments."
    initial_headers = request_options.get("initialHeaders")
    if isinstance(initial_headers, Mapping):
        unsupported_headers = [
            name
            for name in initial_headers
            if isinstance(name, str) and name.lower() in HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE
        ]
        if unsupported_headers:
            names = ", ".join(sorted(repr(name) for name in unsupported_headers))
            return f"does not support initial_headers override(s): {names}; remove these overrides."
    return None


def validate_obsolete_resource_options(
    kwargs: Mapping[str, Any], operation: str
) -> None:
    for option, key in (
        ("session_token", "sessionToken"),
        ("populate_query_metrics", "populateQueryMetrics"),
    ):
        if option in kwargs or any(
            isinstance(options, Mapping) and key in options
            for options in (kwargs.get("request_options"), kwargs.get("feed_options"))
        ):
            raise TypeError(f"{operation}() does not support the '{option}' option")


def validate_database_read_kwargs(kwargs: Mapping[str, Any]) -> None:
    """Reject excluded read options before either options dictionary is consumed.

    :param Mapping[str, Any] kwargs: Call keywords and nested options to inspect.
    :return: None.
    :rtype: None
    """
    validate_obsolete_resource_options(kwargs, "DatabaseProxy.read")


def validate_database_delete_kwargs(kwargs: Mapping[str, Any]) -> None:
    """Reject excluded delete options before building or sending a request.

    :param Mapping[str, Any] kwargs: Call keywords and nested options to inspect.
    :return: None.
    :rtype: None
    """
    validate_obsolete_resource_options(kwargs, "delete_database")


def build_delete_database_prepared(
    database_link: Any,
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the prepared request that identifies the database to delete.

    :param Any database_link: Database link in ``dbs/{id}`` form.
    :param Mapping[str, Any] request_options: Internal delete options to translate.
    :keyword Mapping[str, Any] or None kwargs: Remaining call keywords, including timeout.
    :return: The account-level deletion request with its database ID.
    :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
    """
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
        partition_key=BindingPartitionKey("cross_partition"),
        headers=headers,
        settings=settings,
        item_id=database_id,
    )


def _database_id_from_link(database_link: Any) -> str:
    """Return the database name from a ``dbs/{id}`` link.

    :param Any database_link: Link to stringify and validate.
    :return: The nonempty database name without surrounding slashes.
    :rtype: str
    """
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
    """Check database-delete options and timeout eligibility.

    :param Mapping[str, Any] request_options: Internal deletion options to check.
    :param Mapping[str, Any] operation_kwargs: Remaining call keywords to check.
    :return: Whether the deletion options can be represented by Rust.
    :rtype: bool
    """
    return _database_request_options_error(request_options, operation_kwargs) is None

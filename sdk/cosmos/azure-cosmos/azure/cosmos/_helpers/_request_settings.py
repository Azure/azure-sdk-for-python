# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared option normalization, header ownership, defaults and typed request settings."""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, Dict, Mapping, Optional, Tuple

from azure.core import MatchConditions

from .._availability_strategy_config import DEFAULT_THRESHOLD_MS
from .._backend.request_settings import (
    HedgingSettings,
    ItemSettings,
    QuerySettings,
    RequestSettings,
    ResourceSettings,
)
from .._constants import _Constants as Constants


def normalize_query_specification(
    query: Any, parameters: Any, *, operation: str,
) -> Tuple[str, tuple[dict[str, Any], ...]]:
    """Validate and snapshot SQL text and parameter values owned by the caller."""
    query, parameters = deepcopy(query), deepcopy(parameters)
    if isinstance(query, dict):
        if set(query) - {"query", "parameters"} or parameters is not None:
            raise ValueError("Supply query parameters once, with a query string or SQL query specification.")
        parameters = query.get("parameters")
        query = query.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError(f"{operation} requires a nonempty SQL query string.")
    if parameters is not None and (
        not isinstance(parameters, (list, tuple))
        or any(
            not isinstance(parameter, dict)
            or set(parameter) != {"name", "value"}
            or not isinstance(parameter["name"], str)
            or not parameter["name"].startswith("@")
            for parameter in parameters
        )
    ):
        raise ValueError("Query parameters must be name/value objects with @-prefixed names.")
    return query, tuple(parameters or ())

# snake_case kwarg name -> internal option-dict key.
COMMON_OPTIONS: Dict[str, str] = {
    "initial_headers": "initialHeaders",
    "pre_trigger_include": "preTriggerInclude",
    "post_trigger_include": "postTriggerInclude",
    "access_condition": "accessCondition",
    "session_token": "sessionToken",
    "resource_token_expiry_seconds": "resourceTokenExpirySeconds",
    "offer_enable_ru_per_minute_throughput": "offerEnableRUPerMinuteThroughput",
    "disable_ru_per_minute_usage": "disableRUPerMinuteUsage",
    "continuation": "continuation",
    "content_type": "contentType",
    "is_query_plan_request": "isQueryPlanRequest",
    "supported_query_features": "supportedQueryFeatures",
    "query_version": "queryVersion",
    "priority": "priorityLevel",
    "no_response": "responsePayloadOnWriteDisabled",
    "retry_write": Constants.Kwargs.RETRY_WRITE,
    "max_item_count": "maxItemCount",
    "throughput_bucket": "throughputBucket",
    "excluded_locations": Constants.Kwargs.EXCLUDED_LOCATIONS,
    "availability_strategy": Constants.Kwargs.AVAILABILITY_STRATEGY,
    "max_integrated_cache_staleness_in_ms": "maxIntegratedCacheStaleness",
}


def compose_options_from_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Pop every recognised kwarg out of ``kwargs`` into a fresh options dict.

    Handles only the kwarg-name -> option-key translation. Does not
    stamp timing fields, does not handle ``etag`` / ``match_condition``
    (``compose_item_options`` handles those), and does not
    pull ``read_timeout`` / ``timeout``.

    A pre-existing ``request_options`` dict in ``kwargs`` is consumed
    as the starting point; kwarg shortcuts override entries from it.

    :param kwargs: Caller's ``**kwargs``. **Mutated:** every recognised
        key (and ``request_options``) is popped.
    :type kwargs: Dict[str, Any]
    :returns: A new dict keyed by internal option-key names.
    :rtype: Dict[str, Any]
    """
    options: Dict[str, Any] = dict(kwargs.pop("request_options", {}) or {})
    for kwarg_name, option_key in COMMON_OPTIONS.items():
        if kwarg_name in kwargs:
            options[option_key] = kwargs.pop(kwarg_name)
    return options


def get_match_headers(kwargs: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Normalize the public conditional-request contract without transport state.

    Consumes only the supplied working dictionary. Both wrappers use this
    utility so their validation messages and conditional-header precedence agree.
    """
    if_match = kwargs.pop("if_match", None)
    if_none_match = kwargs.pop("if_none_match", None)
    match_condition = kwargs.pop("match_condition", None)
    if match_condition == MatchConditions.IfNotModified:
        if_match = kwargs.pop("etag", None)
        if not if_match:
            raise ValueError("'match_condition' specified without 'etag'.")
    elif match_condition == MatchConditions.IfPresent:
        if_match = "*"
    elif match_condition == MatchConditions.IfModified:
        if_none_match = kwargs.pop("etag", None)
        if not if_none_match:
            raise ValueError("'match_condition' specified without 'etag'.")
    elif match_condition == MatchConditions.IfMissing:
        if_none_match = "*"
    elif match_condition is None:
        etag = kwargs.pop("etag", None)
        if etag is not None:
            raise ValueError("'etag' specified without 'match_condition'.")
    else:
        raise TypeError("Invalid match condition: {}".format(match_condition))
    return if_match, if_none_match


def compose_item_options(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build Rust item options from a local kwargs copy, not legacy build_options.

    Owns conditional-request normalization and copies supplied option mappings.
    It generates no Python pipeline timing/retry bookkeeping. Consumed kwargs
    are removed only from the helper's working copy, never the caller's mapping.
    """
    feed_options = kwargs.pop("feed_options", {})
    if "request_options" not in kwargs:
        kwargs["request_options"] = feed_options
    options = compose_options_from_kwargs(kwargs)
    for key in (Constants.Kwargs.READ_TIMEOUT, Constants.Kwargs.TIMEOUT):
        if key in kwargs:
            options[key] = kwargs[key]
    if_match, if_none_match = get_match_headers(kwargs)
    if if_match:
        options["accessCondition"] = {"type": "IfMatch", "condition": if_match}
    if if_none_match:
        options["accessCondition"] = {"type": "IfNoneMatch", "condition": if_none_match}
    return options


def get_common_options() -> Mapping[str, str]:
    """Return a read-only view of ``COMMON_OPTIONS``.

    Returning a ``Mapping`` makes accidental mutation by a caller a
    typing error rather than a silent shared-state bug.

    :rtype: Mapping[str, str]
    """
    return COMMON_OPTIONS


# Internal option-keys the legacy ``_base.GetHeaders`` path emits only when the
# value is *truthy* -- a ``0`` / ``None`` / ``""`` value omits the header
# entirely. ``indexing_directive=IndexingDirective.Default`` is ``0`` and
# ``throughput_bucket=0`` is not a real bucket, so both must send no header to
# match v4. ``maxIntegratedCacheStaleness`` is treated the same way, for the
# same compatibility reason.
_TRUTHY_GATED_OPTION_KEYS = frozenset(
    {
        "autoUpgradePolicy",
        "containerRID",
        "continuation",
        "contentType",
        "correlatedActivityId",
        "disableRUPerMinuteUsage",
        "enableCrossPartitionQuery",
        "enableScanInQuery",
        "enableScriptLogging",
        "indexingDirective",
        "isQueryPlanRequest",
        "maxItemCount",
        "offerEnableRUPerMinuteThroughput",
        "offerThroughput",
        "offerType",
        "populateIndexMetrics",
        "populatePartitionKeyRangeStatistics",
        "populateQueryAdvice",
        "populateQueryMetrics",
        "populateQuotaInfo",
        "postTriggerInclude",
        "preTriggerInclude",
        "priorityLevel",
        "queryVersion",
        "resourceTokenExpirySeconds",
        "responseContinuationTokenLimitInKb",
        "sessionToken",
        "supportedQueryFeatures",
        "throughputBucket",
    }
)


# Legacy pipeline bookkeeping is not a service setting. Reused build_options
# dictionaries can carry these keys into point preparation.
#   * ``operationStartTime`` -- pipeline timing bookkeeping (``_base.build_options``).
#   * ``timeoutScope`` / ``timeout`` / ``read_timeout`` -- legacy timeout policy
#     inputs; supported durations travel as settings.timeout_seconds.
#     Item/page deadlines are supplied separately to execution.
#   * ``retry_write`` -- how many times to retry a non-idempotent write. It is a
#     retry-policy input, not a header: the legacy path reads it in
#     ``_request_object.RequestObject.set_retry_write`` and ``GetHeaders`` never
#     looks at it. ``_base.build_options`` copies it into the options dict for
#     every operation (it is in ``COMMON_OPTIONS``), so without this entry it
#     rides to the binding as a header named ``retry_write``.
_NON_WIRE_INTERNAL_OPTION_KEYS = frozenset(
    {
        Constants.OperationStartTime,
        Constants.TimeoutScope,
        Constants.Kwargs.TIMEOUT,
        Constants.Kwargs.READ_TIMEOUT,
        Constants.Kwargs.RETRY_WRITE,
    }
)


OPTION_HEADER_NAMES = {
    "preTriggerInclude": "x-ms-documentdb-pre-trigger-include",
    "postTriggerInclude": "x-ms-documentdb-post-trigger-include",
    "indexingDirective": "x-ms-indexing-directive",
    "maxItemCount": "x-ms-max-item-count",
    "priorityLevel": "x-ms-cosmos-priority-level",
    "throughputBucket": "x-ms-cosmos-throughput-bucket",
    "containerRID": "x-ms-cosmos-intended-collection-rid",
    "maxIntegratedCacheStaleness": "x-ms-dedicatedgateway-max-age",
    "offerThroughput": "x-ms-offer-throughput",
    "autoUpgradePolicy": "x-ms-cosmos-offer-autopilot-settings",
    "continuation": "x-ms-continuation",
    "contentType": "content-type",
    "correlatedActivityId": "x-ms-cosmos-correlated-activityid",
    "disableRUPerMinuteUsage": "x-ms-documentdb-disable-ru-per-minute-usage",
    "enableCrossPartitionQuery": "x-ms-documentdb-query-enablecrosspartition",
    "enableScanInQuery": "x-ms-documentdb-query-enable-scan",
    "enableScriptLogging": "x-ms-documentdb-script-enable-logging",
    "isQueryPlanRequest": "x-ms-cosmos-is-query-plan-request",
    "offerEnableRUPerMinuteThroughput": "x-ms-offer-is-ru-per-minute-throughput-enabled",
    "offerType": "x-ms-offer-type",
    "populateIndexMetrics": "x-ms-cosmos-populateindexmetrics",
    "populatePartitionKeyRangeStatistics": "x-ms-documentdb-populatepartitionstatistics",
    "populateQueryAdvice": "x-ms-cosmos-populatequeryadvice",
    "populateQueryMetrics": "x-ms-documentdb-populatequerymetrics",
    "populateQuotaInfo": "x-ms-documentdb-populatequotainfo",
    "queryVersion": "x-ms-cosmos-query-version",
    "resourceTokenExpirySeconds": "x-ms-documentdb-expiry-seconds",
    "responseContinuationTokenLimitInKb": "x-ms-documentdb-responsecontinuationtokenlimitinkb",
    "supportedQueryFeatures": "x-ms-cosmos-supported-query-features",
    "sessionToken": "x-ms-session-token",
}

# The Rust driver intentionally owns these standard headers and overwrites
# custom values after the binding adds ``initial_headers``. The legacy pipeline
# keeps per-call overrides for the same names, so such reads must stay on
# legacy until the driver offers a way to override them too.
HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE = frozenset(
    {
        "accept",
        "cache-control",
        "user-agent",
        "x-ms-version",
    }
)


# Exclude SDK transport defaults from direct Rust preparation. These are not the
# customer overrides listed above: authorization, date and content type are
# protocol values, whereas the list above protects overrides the legacy
# transport can honor.
HEADERS_THE_DRIVER_REGENERATES = frozenset(
    {
        "accept",
        "authorization",
        "cache-control",
        "content-type",
        "user-agent",
        "x-ms-date",
        "x-ms-version",
    }
)


def overrides_driver_owned_header(request_options: Mapping[str, Any]) -> bool:
    """Return whether ``initial_headers`` sets a header the driver would replace.

    The legacy pipeline lets the caller's value win for these names, so a read
    that sets one has to stay on the legacy path or the caller's header is
    dropped without a word.
    """
    initial_headers = request_options.get("initialHeaders")
    if not isinstance(initial_headers, Mapping):
        return False
    return any(
        isinstance(name, str)
        and name.lower() in HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE
        for name in initial_headers
    )


def is_supported_operation_timeout(timeout: Any) -> bool:
    """Whether a duration survives Rust's one-second minimum and f64 conversion."""
    if timeout is None:
        return True
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        return False
    try:
        seconds = float(timeout)
    except OverflowError:
        return False
    # These comparisons also reject NaN and infinity.
    return 1.0 <= seconds < 2**64


def _timeout_is_representable(operation_kwargs: Mapping[str, Any]) -> bool:
    """Return whether the caller's ``timeout`` survives the trip to the driver.

    The driver clamps a positive sub-second value up to one second and drops a
    zero, negative, or non-numeric one, in both cases without an error. The
    legacy path either honors the exact number or raises its own validation
    error, so anything the driver would change is kept off the Rust path.
    """
    timeout = operation_kwargs.get(Constants.Kwargs.TIMEOUT)
    if timeout is None:
        return True
    if not isinstance(timeout, (int, float)):
        return False
    seconds = float(timeout)
    # ``nan`` reaches neither backend's timeout logic -- the driver drops it as
    # non-finite and the legacy retry loop never finds it elapsed -- so it is
    # representable even though it fails every numeric bound.
    if math.isnan(seconds):
        return True
    return seconds >= 1.0


def apply_no_response_on_write_default(
    options: Dict[str, Any], no_response_on_write_default: bool
) -> None:
    """Apply the client-level ``no_response_on_write`` setting as a fallback.

    A per-call ``no_response`` always wins. The client-level default takes
    effect only when the call passes no per-call value and that default is
    truthy, so an explicit per-call ``no_response=False`` still returns the
    document body. When it applies, this sets the
    ``responsePayloadOnWriteDisabled`` option, which suppresses the write
    response body.

    :param options: The internal options dict. **Mutated** when the fallback
        applies.
    :type options: Dict[str, Any]
    :param no_response_on_write_default: The client-level
        ``connection_policy.ResponsePayloadOnWriteDisabled`` value.
    :type no_response_on_write_default: bool
    """
    if no_response_on_write_default and "responsePayloadOnWriteDisabled" not in options:
        options["responsePayloadOnWriteDisabled"] = True


def stamp_container_rid(
    options: Dict[str, Any],
    container_rid: str,
) -> None:
    """Write ``x-ms-cosmos-intended-collection-rid`` into ``options`` if absent.

    Idempotent: if the caller has already set ``Constants.ContainerRID``,
    the existing value is preserved.

    :param options: The internal options dict. Mutated in place.
    :type options: Dict[str, Any]
    :param container_rid: Already-resolved resource id; no metadata callback.
    :type container_rid: str
    :rtype: None
    """
    if Constants.ContainerRID in options:
        return
    options[Constants.ContainerRID] = container_rid


# This table accepts historical request_options input. It is not a wire schema.
OPTION_FIELDS = {
    "priorityLevel": ("", "priority"),
    "throughputBucket": ("", "throughput_bucket"),
    "sessionToken": ("", "session_token"),
    "correlatedActivityId": ("", "correlated_activity_id"),
    "consistencyLevel": ("", "consistency_level"),
    "responsePayloadOnWriteDisabled": ("", "no_response"),
    "excludedLocations": ("", "excluded_locations"),
    "timeout": ("", "timeout_seconds"),
    "availabilityStrategy": ("", "hedging"),
    "preTriggerInclude": ("item", "pre_triggers"),
    "postTriggerInclude": ("item", "post_triggers"),
    "indexingDirective": ("item", "indexing_directive"),
    "maxIntegratedCacheStaleness": ("item", "max_staleness_ms"),
    "maxItemCount": ("query", "max_item_count"),
    "continuation": ("query", "continuation"),
    "enableCrossPartitionQuery": ("query", "enable_cross_partition"),
    "enableScanInQuery": ("query", "enable_scan"),
    "populateIndexMetrics": ("query", "populate_index_metrics"),
    "populateQueryMetrics": ("query", "populate_query_metrics"),
    "populateQueryAdvice": ("query", "populate_query_advice"),
    "isQueryPlanRequest": ("query", "is_query_plan"),
    "supportedQueryFeatures": ("query", "supported_features"),
    "queryVersion": ("query", "version"),
    "responseContinuationTokenLimitInKb": ("query", "continuation_limit_kb"),
    "containerRID": ("resource", "container_rid"),
    "offerThroughput": ("resource", "offer_throughput"),
    "autoUpgradePolicy": ("resource", "autoscale_settings"),
    "offerType": ("resource", "offer_type"),
    "resourceTokenExpirySeconds": ("resource", "resource_token_expiry_seconds"),
    "offerEnableRUPerMinuteThroughput": ("resource", "enable_ru_per_minute"),
    "disableRUPerMinuteUsage": ("resource", "disable_ru_per_minute"),
    "enableScriptLogging": ("resource", "enable_script_logging"),
    "populatePartitionKeyRangeStatistics": (
        "resource",
        "populate_partition_statistics",
    ),
    "populateQuotaInfo": ("resource", "populate_quota_info"),
    "contentType": ("resource", "content_type"),
}
_HEADER_FIELDS = {wire: OPTION_FIELDS[key] for key, wire in OPTION_HEADER_NAMES.items()}
_HEADER_FIELDS.update(
    {
        "if-match": ("item", "if_match"),
        "if-none-match": ("item", "if_none_match"),
        "x-ms-consistency-level": ("", "consistency_level"),
        "x-ms-activity-id": ("", "activity_id"),
    }
)


def build_customer_headers(
    initial_headers: Optional[Mapping[str, Any]],
) -> dict[str, str]:
    if initial_headers is None:
        return {}
    if not isinstance(initial_headers, Mapping):
        raise TypeError("initial_headers must be a mapping or None.")
    result = {}
    for name, value in initial_headers.items():
        if not isinstance(name, str):
            raise TypeError("Request header names must be strings")
        result[name.lower()] = str(value)
    return result


def build_request_headers_and_settings(
    options: Mapping[str, Any],
) -> tuple[dict[str, str], RequestSettings]:
    headers: dict[str, str] = {}
    groups: dict[str, dict[str, Any]] = {
        "": {},
        "item": {},
        "query": {},
        "resource": {},
    }
    for key, value in options.items():
        if key in ("partitionKey", "disableAutomaticIdGeneration") or (
            key in _NON_WIRE_INTERNAL_OPTION_KEYS and key != Constants.Kwargs.TIMEOUT
        ):
            continue
        if key == "initialHeaders":
            for name, text in build_customer_headers(value).items():
                target = _HEADER_FIELDS.get(name)
                if target and name not in ("x-ms-activity-id", "x-ms-session-token"):
                    groups[target[0]].pop(target[1], None)
                headers[name] = text
            continue
        if key == "accessCondition":
            if value is None:
                continue
            if not isinstance(value, Mapping) or value.get("type") not in (
                "IfMatch",
                "IfNoneMatch",
            ):
                raise ValueError("accessCondition requires type IfMatch or IfNoneMatch")
            name = "if_match" if value["type"] == "IfMatch" else "if_none_match"
            if not isinstance(value.get("condition"), str):
                raise TypeError("accessCondition requires a string condition")
            groups["item"][name] = value["condition"]
            headers.pop(name.replace("_", "-"), None)
            continue
        target = OPTION_FIELDS.get(key)
        if target is None:
            if isinstance(key, str) and (
                key.lower().startswith("x-ms-")
                or key.lower()
                in (
                    "if-match",
                    "if-none-match",
                    "prefer",
                )
            ):
                name = key.lower()
                prior = _HEADER_FIELDS.get(name)
                if name in ("x-ms-activity-id", "x-ms-session-token"):
                    groups[""][
                        "activity_id" if name == "x-ms-activity-id" else "session_token"
                    ] = str(value)
                    headers.pop(name, None)
                    continue
                if prior:
                    groups[prior[0]].pop(prior[1], None)
                headers[name] = str(value)
                continue
            raise TypeError(f"Unknown Rust request option: {key}")
        if value is None:
            continue
        if (
            key in _TRUTHY_GATED_OPTION_KEYS
            or key in ("maxIntegratedCacheStaleness", "consistencyLevel")
        ) and not value:
            continue
        if key == "availabilityStrategy":
            if value is False:
                value = HedgingSettings(False)
            elif value is True:
                value = HedgingSettings(True, DEFAULT_THRESHOLD_MS)
            else:
                value = HedgingSettings(True, getattr(value, "threshold_ms", None))
        elif key in ("preTriggerInclude", "postTriggerInclude"):
            value = (value,) if isinstance(value, str) else tuple(value)
        elif key == "excludedLocations":
            if isinstance(value, str):
                raise TypeError(
                    "excluded_locations must be a sequence of region strings"
                )
            value = tuple(value)
        groups[target[0]][target[1]] = value
        wire_name = OPTION_HEADER_NAMES.get(
            key, "x-ms-consistency-level" if key == "consistencyLevel" else ""
        )
        headers.pop(wire_name, None)
    for name in ("x-ms-activity-id", "x-ms-session-token"):
        target = _HEADER_FIELDS[name]
        if target[1] in groups[target[0]]:
            headers.pop(name, None)
    return headers, RequestSettings(
        **groups[""],
        item=ItemSettings(**groups["item"]),
        query=QuerySettings(**groups["query"]),
        resource=ResourceSettings(**groups["resource"]),
    )


def prepare_service_request_settings(
    options: Mapping[str, Any],
    default_headers: Mapping[str, Any],
    *,
    resource_type: str,
) -> tuple[dict[str, str], RequestSettings]:
    initial = build_customer_headers(default_headers)
    initial.update(build_customer_headers(options.get("initialHeaders")))
    initial = {
        key: value
        for key, value in initial.items()
        if key not in HEADERS_THE_DRIVER_REGENERATES
    }
    normalized = {"initialHeaders": initial}
    normalized.update(
        (key, value) for key, value in options.items() if key != "initialHeaders"
    )
    if resource_type != "docs":
        normalized.pop("sessionToken", None)
    if resource_type == "dbs":
        normalized.pop(Constants.ContainerRID, None)
    normalized.pop("contentType", None)
    return build_request_headers_and_settings(normalized)


def account_request_settings(
    options: Mapping[str, Any],
    kwargs: Optional[Mapping[str, Any]],
) -> tuple[dict[str, str], RequestSettings]:
    normalized = dict(options)
    normalized.pop("timeout", None)
    timeout = (kwargs or {}).get("timeout")
    if timeout is not None:
        normalized["timeout"] = timeout
    return build_request_headers_and_settings(normalized)

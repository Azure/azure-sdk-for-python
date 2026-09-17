# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Wire-value assertions for migrated tests; never used by production preparation."""
from dataclasses import replace
import json

from azure.cosmos._backend.contracts import PreparedRequest, PreparedQuery
from azure.cosmos._backend.request_settings import RequestSettings, HedgingSettings
from azure.cosmos._backend.partition_key import PartitionKeyInput, UNDEFINED_PARTITION_KEY
from azure.cosmos._helpers._request_settings import build_request_headers_and_settings, _HEADER_FIELDS


def wire_headers(request):
    if not isinstance(request, (PreparedRequest, PreparedQuery)):
        return request.headers
    result = dict(request.headers)
    settings = request.settings
    for wire, (group, field) in _HEADER_FIELDS.items():
        obj = getattr(settings, group) if group else settings
        value = getattr(obj, field)
        if value is not None:
            result[wire] = ",".join(value) if isinstance(value, tuple) else str(value)
    if settings.query.is_query is not None:
        result["x-ms-documentdb-isquery"] = str(settings.query.is_query).lower()
    return result


def settings_options(request):
    if not isinstance(request, (PreparedRequest, PreparedQuery)):
        return request.request_options
    settings = request.settings
    result = {}
    for field, key in (
        ("no_response", "responsePayloadOnWriteDisabled"),
        ("excluded_locations", "excludedLocations"),
        ("timeout_seconds", "timeout_seconds"),
    ):
        value = getattr(settings, field)
        if value is not None:
            result[key] = list(value) if isinstance(value, tuple) else value
    if settings.hedging is not None:
        result["availabilityStrategy"] = (
            f"enabled:{settings.hedging.threshold_ms}" if settings.hedging.enabled else "disabled"
        )
    return result


def legacy_settings(options):
    """Translate old fixture inputs, not a runtime compatibility escape hatch."""
    options = dict(options)
    if "timeout_seconds" in options:
        options["timeout"] = options.pop("timeout_seconds")
    hedge = options.pop("availabilityStrategy", None)
    _, settings = build_request_headers_and_settings(options)
    if hedge is not None:
        if hedge == "disabled":
            settings = replace(settings, hedging=HedgingSettings(False))
        elif isinstance(hedge, str) and hedge.startswith("enabled:"):
            settings = replace(settings, hedging=HedgingSettings(True, int(hedge.split(":")[1])))
        else:
            raise ValueError("Invalid legacy hedging fixture")
    return settings


def legacy_preparation(options):
    headers, settings = build_request_headers_and_settings(options)
    request = PreparedRequest("test", "", b"", PartitionKeyInput("cross_partition"), headers=headers, settings=settings)
    return wire_headers(request), settings_options(request)


def flatten_options_to_headers(options):
    return legacy_preparation(options)[0]


def key_from_legacy_header(header, *, extract=True, feed_range=False):
    """Translate old test fixture literals; never used in production dispatch."""
    if header is None:
        return PartitionKeyInput("extract" if extract else "cross_partition")
    if header == "":
        return PartitionKeyInput("cross_partition")
    values = json.loads(header)
    if not values:
        return PartitionKeyInput("empty_sentinel" if feed_range else "cross_partition")
    if values == [[]]:
        return PartitionKeyInput("empty_sequence")
    return PartitionKeyInput("components", tuple(
        UNDEFINED_PARTITION_KEY if value == {} else value for value in values
    ))


def legacy_partition_key_from_request(request):
    """Project a typed key only for legacy wire-value assertions."""
    key = getattr(request, "partition_key", None)
    if not isinstance(key, PartitionKeyInput):
        return request.partition_key_header
    if key.kind == "extract":
        return None
    if key.kind in ("cross_partition", "empty_sentinel"):
        return "[]"
    if key.kind == "empty_sequence":
        return "[[]]"
    return json.dumps(
        [{} if value is UNDEFINED_PARTITION_KEY else value for value in key.values],
        separators=(",", ":"), ensure_ascii=True,
    )

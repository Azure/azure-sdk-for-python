# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Helpers that read a prepared request back as the flat values older tests expect.

Older tests were written when everything travelled as a single bag of headers and a
single bag of options. The current code keeps most of that information in named fields
instead. Rather than rewrite every one of those tests, these helpers read a prepared
request and rebuild the flat view it would have had.

This direction is deliberate: it reads a real request and reports what it contains. It
never feeds anything back into production code, so a test cannot accidentally check a
shape that only these helpers can produce.
"""
from dataclasses import replace
import json

from azure.cosmos._backend.contracts import PreparedRequest, PreparedPageRequest
from azure.cosmos._backend.request_settings import RequestSettings, HedgingSettings
from azure.cosmos._backend.partition_key_input import BindingPartitionKey, UNDEFINED_PARTITION_KEY
from azure.cosmos._helpers._request_settings import build_request_headers_and_settings, _HEADER_FIELDS


def wire_headers(request):
    """Return every header a request would send, including those held as named fields.

    A prepared request keeps some values in named fields even though they leave as
    headers. This adds them back under their header names, so a test can check the full
    set the service would receive. Anything that is not a prepared request already keeps
    all of its headers together, so it is returned unchanged.
    """
    if not isinstance(request, (PreparedRequest, PreparedPageRequest)):
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
    """Return the settings that are not headers, under the option names older tests use.

    These four values never travelled as headers even in the old code; they were options
    the client acted on itself. Only values that were actually chosen appear, so a test
    can tell "left alone" apart from "set to something".
    """
    if not isinstance(request, (PreparedRequest, PreparedPageRequest)):
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
    """Build settings from old-style fixture inputs, for tests only.

    Two of the old fixture spellings no longer match what the code accepts, so they are
    translated here. This exists to keep old test inputs working; it is not a way for
    real callers to keep using the old names.
    """
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
    """Put a bag of old-style options through the real split and read the result back out.

    This is the round trip: options go in, the production code sorts them into headers
    and named settings, and the two helpers above flatten them again. A test that gets
    back what it put in has proved the split loses nothing.
    """
    headers, settings = build_request_headers_and_settings(options)
    request = PreparedRequest("test", "", b"", BindingPartitionKey("cross_partition"), headers=headers, settings=settings)
    return wire_headers(request), settings_options(request)


def flatten_options_to_headers(options):
    """Run the round trip above and return only the headers, for tests that ignore the rest."""
    return legacy_preparation(options)[0]


def key_from_legacy_header(header, *, extract=True, feed_range=False):
    """Build a partition key from the text an old test wrote, for tests only.

    Old tests express a key as the header string it used to become. This reads that back
    into the record the code now uses, including the cases where the text alone is
    ambiguous: no header at all means take the key from the item for a point operation
    but search everywhere for a feed, and an empty list means different things in the two
    settings, which is why the caller says which one it is.

    Production code never reads a key back from text.
    """
    if header is None:
        return BindingPartitionKey("extract" if extract else "cross_partition")
    if header == "":
        return BindingPartitionKey("cross_partition")
    values = json.loads(header)
    if not values:
        return BindingPartitionKey("empty_sentinel" if feed_range else "cross_partition")
    if values == [[]]:
        return BindingPartitionKey("empty_sequence")
    return BindingPartitionKey("components", tuple(
        UNDEFINED_PARTITION_KEY if value == {} else value for value in values
    ))


def legacy_partition_key_from_request(request):
    """Write a request's partition key back out as the text an old test expects.

    The reverse of the helper above, and the one place the four situations become the
    same kind of text again: take the key from the item is written as no header at all,
    both the no-key-at-all cases as an empty list, and an empty list as a list holding an
    empty list. Real values are written compactly, exactly as the old code wrote them.

    Two of those situations share one spelling, which is why the record exists and why
    this direction is only safe in a test that already knows which it meant.
    """
    key = getattr(request, "partition_key", None)
    if not isinstance(key, BindingPartitionKey):
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

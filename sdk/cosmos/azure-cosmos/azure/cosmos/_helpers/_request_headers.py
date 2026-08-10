# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Turn a call's options into the headers and values that go on the wire.

Every prepared request, whatever resource it targets, ends up needing the same
translation: the internal option keys the SDK assembled (``preTriggerInclude``,
``indexingDirective``, ``accessCondition``, ...) have to become the exact header
names and string values the service expects, and they have to match what the
legacy path would have sent byte for byte.

That translation lives here, once, so the database, container and item builders
share it instead of each re-deriving it. ``flatten_options_to_headers`` is the
main entry point; the rest handle the cases where a value needs special care --
a sequence that must be comma-joined, a key the driver owns, a timeout that
cannot be represented, or a default that only applies to writes.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Mapping, Optional

from .._availability_strategy_config import DEFAULT_THRESHOLD_MS
from .._constants import _Constants as Constants
from ..http_constants import HttpHeaders


# Internal option-keys whose value may arrive as a *sequence* of names.
# The legacy ``_base.GetHeaders`` path comma-joins such a sequence into the
# single string the service expects (``"t1,t2"``); the Rust binding, by
# contrast, stringifies a non-``str`` value with Python ``str()``, which
# would put a list's ``repr`` (``"['t1', 't2']"``) on the wire. Normalising
# here keeps the wire bytes byte-identical to v4 for every operation.
_SEQUENCE_VALUED_OPTION_KEYS = frozenset({"preTriggerInclude", "postTriggerInclude"})


# Internal option-keys the legacy ``_base.GetHeaders`` path emits only when the
# value is *truthy* -- a ``0`` / ``None`` / ``""`` value omits the header
# entirely. ``indexing_directive=IndexingDirective.Default`` is ``0`` and
# ``throughput_bucket=0`` is not a real bucket, so both must send no header to
# match v4. (``maxIntegratedCacheStaleness`` is also truthy-gated but keeps its
# own wire-name branch in ``flatten_options_to_headers``.)
_TRUTHY_GATED_OPTION_KEYS = frozenset({
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
})


# Internal option-keys that live in the options dict for the legacy pipeline's
# own use but are NOT wire headers, so ``flatten_options_to_headers`` must never
# emit them. The legacy ``_base.GetHeaders`` path already ignores them (it reads
# only the keys it knows); the Rust prep's catch-all would otherwise copy them
# through as bogus headers (dropped by the binding in production, but a hard
# error under ``COSMOS_WIRE_STRICT``). These reach a point-operation's options
# only when a caller reuses a ``build_options``-processed / query options dict as
# the request options -- e.g. ``read_items`` routes each single-item leg through
# the point-read prep with the batch's query options. The normal point methods
# build a minimal ``{"partitionKey": ...}`` options dict and never carry these.
#   * ``operationStartTime`` -- pipeline timing bookkeeping (``_base.build_options``).
#   * ``timeoutScope`` / ``timeout`` / ``read_timeout`` -- legacy timeout policy
#     inputs; the Rust path takes the timeout via the ``__overall_timeout_seconds``
#     sentinel header instead, set from the ``timeout`` kwarg.
#   * ``retry_write`` -- how many times to retry a non-idempotent write. It is a
#     retry-policy input, not a header: the legacy path reads it in
#     ``_request_object.RequestObject.set_retry_write`` and ``GetHeaders`` never
#     looks at it. ``_base.build_options`` copies it into the options dict for
#     every operation (it is in ``COMMON_OPTIONS``), so without this entry it
#     rides to the binding as a header named ``retry_write``.
_NON_WIRE_INTERNAL_OPTION_KEYS = frozenset({
    Constants.OperationStartTime,
    Constants.TimeoutScope,
    Constants.Kwargs.TIMEOUT,
    Constants.Kwargs.READ_TIMEOUT,
    Constants.Kwargs.RETRY_WRITE,
})


# Option-keys that ``flatten_options_to_headers`` hands to the binding as their
# raw camelCase form, expecting the RUST fast path to translate them to the
# ``x-ms-*`` wire header (or lift them to a typed driver field). This is the
# shared vocabulary of the header/option mapping that is split across two
# languages: this module owns truthy-gating and a handful of translations, while
# ``extract_op_modifiers`` (azure_cosmos_rust/src/wire/request.rs) owns the camelCase ->
# ``x-ms-`` table and the typed-field lifting.
#
# WHY THIS MATTERS (the landmine): the Rust match ends in ``_ => continue``, so
# any option-key Python emits that Rust does not recognise is SILENTLY DROPPED --
# no error, wrong wire bytes, green tests. Adding a knob on the Python side alone
# would therefore quietly no-op on the fast path. Two guards defend this:
#   1. ``test_rust_option_key_parity`` enforces that every key below has a matching
#      arm in ``wire/request.rs`` (and vice versa), turning contract drift into a loud test
#      failure. This relies on the new key being added to *this* set.
#   2. The Rust ``COSMOS_WIRE_STRICT=1`` runtime gate (extract_op_modifiers in
#      wire/request.rs) hard-errors on any unrecognised, non-allowlisted key that actually
#      reaches the binding -- catching a key that drifted into
#      ``flatten_options_to_headers`` / ``COMMON_OPTIONS`` even when this set was
#      not updated. Off by default (production keeps the lenient silent drop, zero
#      behavior change); set it in tests/CI.
# Keep this set, the Rust ``extract_op_modifiers`` arms, and the parity test in
# lockstep.
RUST_HANDLED_OPTION_KEYS = frozenset({
    "preTriggerInclude",
    "postTriggerInclude",
    "indexingDirective",
    "maxItemCount",
    "priorityLevel",
    "throughputBucket",
    "containerRID",
    "maxIntegratedCacheStaleness",
    "responsePayloadOnWriteDisabled",
    "excludedLocations",
    "sessionToken",
    # Lifted to a typed driver field / forwarded verbatim by the binding
    # (see extract_op_modifiers). availabilityStrategy -> cross-region hedging
    # control; initialHeaders -> arbitrary customer headers forwarded as-is.
    "availabilityStrategy",
    "initialHeaders",
    "offerThroughput",
    "autoUpgradePolicy",
    "continuation",
    "contentType",
    "correlatedActivityId",
    "disableRUPerMinuteUsage",
    "enableCrossPartitionQuery",
    "enableScanInQuery",
    "enableScriptLogging",
    "isQueryPlanRequest",
    "offerEnableRUPerMinuteThroughput",
    "offerType",
    "populateIndexMetrics",
    "populatePartitionKeyRangeStatistics",
    "populateQueryAdvice",
    "populateQueryMetrics",
    "populateQuotaInfo",
    "queryVersion",
    "resourceTokenExpirySeconds",
    "responseContinuationTokenLimitInKb",
    "supportedQueryFeatures",
})


# The Rust driver intentionally owns these standard headers and overwrites
# custom values after the binding adds ``initial_headers``. The legacy pipeline
# preserves per-call overrides for the same names, so such reads must stay on
# legacy until the driver exposes an equivalent override contract.
_DRIVER_OWNED_INITIAL_HEADERS = frozenset({
    "accept",
    "cache-control",
    "user-agent",
    "x-ms-version",
})


# Headers the rust driver builds for itself on every request. A path that hands
# the binding *legacy-prepared wire headers* (rather than camelCase option-keys)
# must strip these before building its ``PreparedRequest``.
#
# Two paths do that: the query/feed pages and the throughput offer operations.
# Both call ``_base.GetHeaders`` to build a complete legacy header map, which
# necessarily includes the standard headers the driver also writes -- the
# authorization signature, the timestamp, the negotiated content type. Forwarding
# them is pointless and, in two ways, actively unhelpful:
#
#   * ``authorization`` / ``accept`` / ``cache-control`` / ``content-type`` have
#     no translation arm in ``extract_op_modifiers``, so the binding silently
#     drops them -- and under ``COSMOS_WIRE_STRICT`` rejects them outright,
#     which would block the very CI gate meant to catch real divergence.
#   * ``x-ms-date`` / ``x-ms-version`` DO reach the driver (they match the
#     ``x-ms-`` passthrough arm) as custom headers carrying our stale values.
#     The driver overwrites both afterwards, so the wire bytes are unaffected
#     today -- but sending a timestamp the driver is about to replace is
#     misleading, and it would matter if that override order ever changed.
#
# Stripping them therefore leaves the wire bytes identical while making the
# hand-off honest: the binding receives only what it is meant to act on.
#
# Distinct from ``_DRIVER_OWNED_INITIAL_HEADERS`` above, which answers a
# different question -- whether a *customer's* ``initial_headers`` override must
# force a legacy fallback because the driver would silently overwrite it. That
# set is about honoring a caller's intent; this one is about not shipping our own
# redundant plumbing.
DRIVER_OWNED_REQUEST_HEADERS = frozenset({
    "accept",
    "authorization",
    "cache-control",
    "content-type",
    "user-agent",
    "x-ms-date",
    "x-ms-version",
})


def _normalize_option_value(option_key: str, value: Any) -> Any:
    """Return the wire-ready value for one option-key / value pair.

    Comma-joins a list/tuple trigger-include into the single string the
    service expects (matching ``_base.GetHeaders``); a trigger-include that
    is already a plain string, and every non-trigger option, passes through
    unchanged.

    :param option_key: The internal (camelCase) option-key being written.
    :type option_key: str
    :param value: The value the customer supplied for it.
    :type value: Any
    :returns: The value to place in the wire-headers map.
    :rtype: Any
    """
    if option_key in _SEQUENCE_VALUED_OPTION_KEYS and isinstance(value, (list, tuple)):
        return ",".join(str(component) for component in value)
    return value


def _account_level_headers(
    request_options: Mapping[str, Any],
    kwargs: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Flatten one account-level operation's options into wire headers.

    Create-database and read-database share exactly this much: the option ->
    header flattening plus the overall-timeout sentinel the binding reads. They
    differ in everything else (create validates and sends a body, read sends
    none and drops the session token), so only this part is shared.
    """
    headers = flatten_options_to_headers(request_options)
    timeout = (kwargs or {}).get(Constants.Kwargs.TIMEOUT)
    if timeout is not None:
        headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout
    return headers


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
        and name.lower() in _DRIVER_OWNED_INITIAL_HEADERS
        for name in initial_headers
    )


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
    # ``nan`` reaches neither engine's timeout logic -- the driver drops it as
    # non-finite and the legacy retry loop never finds it elapsed -- so it is
    # representable even though it fails every numeric bound.
    if math.isnan(seconds):
        return True
    return seconds >= 1.0


def _availability_strategy_to_wire(value: Any) -> Optional[str]:
    """Normalize a per-request ``availability_strategy`` into the compact string
    the rust binding parses (see ``parse_availability_strategy`` in
    ``wire/request.rs``).

    The customer's value has already been validated into one of:
      * ``False`` -> hedging explicitly disabled -> ``"disabled"``
      * ``True`` -> hedging on with the SDK default threshold
      * a ``CrossRegionHedgingStrategy`` (from a dict) -> hedging on with its
        primary ``threshold_ms``
    Returns ``None`` when there is nothing to send (unrecognized / no threshold),
    leaving the driver on its default.
    """
    if value is False:
        return "disabled"
    if value is True:
        return "enabled:{}".format(DEFAULT_THRESHOLD_MS)
    threshold_ms = getattr(value, "threshold_ms", None)
    if threshold_ms is not None:
        return "enabled:{}".format(int(threshold_ms))
    return None


def flatten_options_to_headers(options: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the ``PreparedRequest.headers`` map from an internal options dict.

    Single source of truth for the options -> wire-headers step shared by
    every point operation, so the six cannot drift on the bytes they emit.
    It mirrors the value handling of the legacy ``_base.GetHeaders`` path:

    - ``initialHeaders`` -- the customer's per-request headers -- is passed
      through as a nested dict under the same key, so the binding forwards each
      entry verbatim (including non-``x-ms-`` names). Keeping it nested (rather
      than flattening into the top-level map) preserves its "these are customer
      headers" provenance, so the binding never confuses them with option-keys.
    - ``availabilityStrategy`` -- the per-request cross-region hedging control --
      is normalized to the compact string the binding parses (``disabled`` /
      ``enabled[:<ms>]``); ``availability_strategy=False`` ships ``disabled`` so
      the caller's explicit disable reaches the driver.
    - ``accessCondition`` -- the ``{"type", "condition"}`` shape built from
      ``etag`` / ``match_condition`` -- becomes an ``If-Match`` /
      ``If-None-Match`` header (the rust path does not run the legacy header
      step that would otherwise emit it). A no-op when the key is absent, so
      operations that never carry it (create / patch) are unaffected.
    - ``maxIntegratedCacheStaleness`` becomes ``x-ms-dedicatedgateway-max-age``,
      emitted **only when truthy** -- ``0`` is a documented no-op, matching
      the legacy ``GetHeaders`` gate.
    - ``consistencyLevel`` -- a per-request consistency override passed
      through ``request_options`` -- becomes the ``x-ms-consistency-level``
      header, emitted **only when truthy**. Without this step the raw
      ``consistencyLevel`` key would be sent as a header the driver ignores.
    - ``preTriggerInclude`` / ``postTriggerInclude`` supplied as a list/tuple
      of trigger ids are comma-joined (see ``_normalize_option_value``).
    - ``indexingDirective`` / ``throughputBucket`` / ``containerRID`` are emitted
      **only when truthy** -- ``indexing_directive=Default(0)`` and
      ``throughput_bucket=0`` ship no header, matching the legacy ``GetHeaders``
      truthy gate.
    - pipeline-internal keys that are not wire headers
      (``_NON_WIRE_INTERNAL_OPTION_KEYS``: ``operationStartTime``,
      ``timeoutScope``, ``timeout``, ``read_timeout``, ``retry_write``) are
      skipped -- the legacy path reads them from the options dict directly
      (timeout policy, retry policy) and ``GetHeaders`` never emits them.
    - every other option-key is copied through unchanged.

    Does **not** stamp the container rid or the overall-timeout sentinel:
    those are not options-dict entries and are written by the caller after
    this returns.

    :param options: The internal options dict (camelCase option-keys).
    :type options: Mapping[str, Any]
    :returns: A fresh wire-headers map.
    :rtype: Dict[str, Any]
    """
    headers: Dict[str, Any] = {}
    for option_key, option_value in options.items():
        if option_key in _NON_WIRE_INTERNAL_OPTION_KEYS:
            # Pipeline-internal bookkeeping that is not a wire header (see the
            # constant's note). Skip so it never rides as a bogus header on the
            # Rust path; the legacy path ignores it in GetHeaders regardless.
            continue
        if option_key == "initialHeaders":
            # Keep customer headers as a nested dict so the binding can forward
            # them verbatim -- including non-``x-ms-`` names it would otherwise
            # drop -- without confusing them with internal option-keys (which
            # keeps the COSMOS_WIRE_STRICT option-key guard meaningful). The
            # legacy path handles initial_headers separately, and this helper is
            # rust-prep-only, so only the rust point path is affected.
            #
            # Anything that is not a dict carries no headers and is dropped. A
            # public method that forwards ``initial_headers=None`` unguarded --
            # ``create_container_if_not_exists`` does, when falling through to
            # the create -- puts a ``None`` here, and copying that through as a
            # header value makes the binding reject the whole request.
            if isinstance(option_value, dict):
                headers["initialHeaders"] = dict(option_value)
            continue
        if option_key == "availabilityStrategy":
            # Normalize the per-request hedging control to the compact string the
            # binding parses (``disabled`` / ``enabled[:<ms>]``). ``False`` (the
            # customer explicitly disabling hedging) must reach the wire, so this
            # is not truthy-gated.
            wire_value = _availability_strategy_to_wire(option_value)
            if wire_value is not None:
                headers["availabilityStrategy"] = wire_value
            continue
        if option_key == "accessCondition" and isinstance(option_value, dict):
            condition = option_value.get("condition")
            cond_type = option_value.get("type")
            if isinstance(condition, str) and cond_type == "IfMatch":
                headers["If-Match"] = condition
            elif isinstance(condition, str) and cond_type == "IfNoneMatch":
                headers["If-None-Match"] = condition
            continue
        if option_key == "maxIntegratedCacheStaleness":
            # Emit only when truthy. ``0`` is a documented no-op and must
            # NOT produce ``x-ms-dedicatedgateway-max-age: 0``; None / missing
            # also skip.
            if option_value:
                headers[HttpHeaders.DedicatedGatewayCacheStaleness] = str(option_value)
            continue
        if option_key == "consistencyLevel":
            # Translate the per-request override to the
            # ``x-ms-consistency-level`` header. Emit only when truthy;
            # None / "" sends no header. The raw key on its own would be a
            # header the driver ignores.
            if option_value:
                headers[HttpHeaders.ConsistencyLevel] = option_value
            continue
        if option_key in _TRUTHY_GATED_OPTION_KEYS and not option_value:
            # A falsy value (0 / None / "") omits the header, matching the
            # legacy GetHeaders truthy gate -- e.g. indexing_directive=
            # Default(0) and throughput_bucket=0 ship no header.
            continue
        headers[option_key] = _normalize_option_value(option_key, option_value)
    return headers


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

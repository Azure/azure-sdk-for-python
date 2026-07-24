# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Compose the wire-prep helpers into a single ``PreparedRequest``.

Five small helpers each handle one slice of request preparation:

- ``_options.compose_options_from_kwargs`` — kwarg → option-key.
- ``_container_rid.stamp_container_rid`` — container rid into options.
- ``_auto_id.ensure_item_id`` — guarantee the document has an id.
- ``_pk_wire.serialize_partition_key_to_wire`` — partition key → header string.
- ``_body_wire.serialize_body_to_bytes`` — document → wire bytes.

This module runs them together as pure functions. The caller
(``ItemHelper`` / ``AsyncItemHelper``) handles all side-effectful
inputs (cache lookups, PK extraction from the body). Pure composition
lets both backends consume the same ``PreparedRequest`` and produce
identical wire bytes.

The public builders:

- ``build_create_database_prepared`` — account-level JSON body plus
  throughput and customer-header options.
- ``build_create_item_prepared`` — full request with JSON body and
  id minting.
- ``build_delete_item_prepared`` — bodiless request; the document id
  rides on ``PreparedRequest.item_id``; reads ``accessCondition``
  out of the options dict and emits the equivalent ``If-Match`` /
  ``If-None-Match`` wire header for the binding to forward.
- ``build_read_item_prepared`` — bodiless request; the document id
  rides on ``PreparedRequest.item_id``; same access-condition
  translation as delete (``If-Match`` / ``If-None-Match``) but the
  dominant case is ``If-None-Match`` (conditional GET / cache
  validation, success surfaces as 304); additionally emits
  ``x-ms-dedicatedgateway-max-age`` from
  ``options["maxIntegratedCacheStaleness"]`` **only when truthy** —
  ``0`` is a silent no-op on the wire, matching the legacy
  behaviour.
- ``build_upsert_item_prepared`` — full request with JSON body, like
  create, but never mints an id (an upsert always disables id
  generation) and emits the same ``If-Match`` / ``If-None-Match``
  header as delete (an upsert honours ``etag`` / ``match_condition``
  where create drops them). The insert-or-replace semantics ride on
  the ``OP_UPSERT_ITEM`` discriminator, not on a header.
- ``build_replace_item_prepared`` — the overwrite-only sibling of
  ``build_upsert_item_prepared``. Byte-identical on the wire except the
  ``OP_REPLACE_ITEM`` discriminator (the backend maps it to the binding's
  ``replace_item`` entry point, driver ``OperationType::Replace``). Both
  share ``_build_write_with_body_prepared``.
- ``build_patch_item_prepared`` — names an existing document like
  delete / read (id on ``PreparedRequest.item_id``, partition key from
  the caller's argument) but carries a body: the patch-operations
  payload. It emits no ``If-Match`` header and serialises no filter
  condition; the helper routes a conditional or guarded patch to the
  legacy path instead.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Tuple

from .._base import _validate_resource
from .._availability_strategy_config import DEFAULT_THRESHOLD_MS
from .._backend.base import (
    OP_CREATE_DATABASE,
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    OP_PATCH_ITEM,
    OP_READ_ITEM,
    OP_REPLACE_ITEM,
    OP_UPSERT_ITEM,
    PreparedRequest,
)
from .._constants import _Constants as Constants
from ..http_constants import HttpHeaders
from ._auto_id import ensure_item_id
from ._body_wire import serialize_body_to_bytes
from ._container_rid import stamp_container_rid
from ._options import compose_options_from_kwargs
from ._pk_wire import serialize_partition_key_to_wire


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
_TRUTHY_GATED_OPTION_KEYS = frozenset({"indexingDirective", "throughputBucket"})

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
#   * ``enableCrossPartitionQuery`` -- a query knob with no meaning on a point read.
_NON_WIRE_INTERNAL_OPTION_KEYS = frozenset({
    Constants.OperationStartTime,
    Constants.TimeoutScope,
    Constants.Kwargs.TIMEOUT,
    Constants.Kwargs.READ_TIMEOUT,
    "enableCrossPartitionQuery",
})

# Option-keys that ``flatten_options_to_headers`` hands to the binding as their
# raw camelCase form, expecting the RUST fast path to translate them to the
# ``x-ms-*`` wire header (or lift them to a typed driver field). This is the
# shared vocabulary of the header/option mapping that is split across two
# languages: this module owns truthy-gating and a handful of translations, while
# ``extract_op_modifiers`` (azure_cosmos_rust/src/wire.rs) owns the camelCase ->
# ``x-ms-`` table and the typed-field lifting.
#
# WHY THIS MATTERS (the landmine): the Rust match ends in ``_ => continue``, so
# any option-key Python emits that Rust does not recognise is SILENTLY DROPPED --
# no error, wrong wire bytes, green tests. Adding a knob on the Python side alone
# would therefore quietly no-op on the fast path. Two guards defend this:
#   1. ``test_rust_option_key_parity`` enforces that every key below has a matching
#      arm in ``wire.rs`` (and vice versa), turning contract drift into a loud test
#      failure. This relies on the new key being added to *this* set.
#   2. The Rust ``COSMOS_WIRE_STRICT=1`` runtime gate (extract_op_modifiers in
#      wire.rs) hard-errors on any unrecognised, non-allowlisted key that actually
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


def _build_create_database_prepared(
    op: str,
    database: Dict[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the account-level create-database request consumed by the Rust backend."""
    _validate_resource(database)
    headers = flatten_options_to_headers(request_options)
    timeout = (kwargs or {}).get(Constants.Kwargs.TIMEOUT)
    if timeout is not None:
        headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout
    return PreparedRequest(
        op=op,
        container_link="",
        body_bytes=serialize_body_to_bytes(database),
        partition_key_header="[]",
        headers=headers,
        item_id=database["id"],
    )


def build_create_database_prepared(
    database: Dict[str, Any],
    request_options: Mapping[str, Any],
    *,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> PreparedRequest:
    """Build the request for a plain account-level create-database."""
    return _build_create_database_prepared(
        OP_CREATE_DATABASE,
        database,
        request_options,
        kwargs=kwargs,
    )


def _availability_strategy_to_wire(value: Any) -> Optional[str]:
    """Normalize a per-request ``availability_strategy`` into the compact string
    the rust binding parses (see ``parse_availability_strategy`` in wire.rs).

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
    - ``indexingDirective`` / ``throughputBucket`` are emitted **only when
      truthy** -- ``indexing_directive=Default(0)`` and ``throughput_bucket=0``
      ship no header, matching the legacy ``GetHeaders`` truthy gate.
    - pipeline-internal keys that are not wire headers
      (``_NON_WIRE_INTERNAL_OPTION_KEYS``: ``operationStartTime``,
      ``timeoutScope``, ``timeout``, ``read_timeout``,
      ``enableCrossPartitionQuery``) are skipped -- they only appear when a
      caller reuses a query / ``build_options`` options dict for a point op
      (e.g. ``read_items``' single-item legs), and the legacy path ignores them
      too.
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
        if option_key == "initialHeaders" and isinstance(option_value, dict):
            # Keep customer headers as a nested dict so the binding can forward
            # them verbatim -- including non-``x-ms-`` names it would otherwise
            # drop -- without confusing them with internal option-keys (which
            # keeps the COSMOS_WIRE_STRICT option-key guard meaningful). The
            # legacy path handles initial_headers separately, and this helper is
            # rust-prep-only, so only the rust point path is affected.
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


def build_create_item_prepared(
    *,
    container_link: str,
    body: Dict[str, Any],
    partition_key_value: Any,
    container_rid: Optional[str],
    enable_automatic_id_generation: bool = True,
    indexing_directive: Optional[Any] = None,
    no_response_on_write_default: bool = False,
    kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[PreparedRequest, str]:
    """Build a ``PreparedRequest`` for a single ``create_item`` call.

    Pure: does not read caches, does not trigger refreshes, does not
    extract the partition-key from the body. The caller has done those
    because they require a ``CosmosClientConnection``.

    :param container_link: Container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``.
    :type container_link: str
    :param body: The Cosmos document. **Mutated in place** when an id
        is minted (missing id + ``enable_automatic_id_generation=True``).
    :type body: Dict[str, Any]
    :param partition_key_value: PK value already extracted from the body
        (or supplied by the caller). Accepted shapes are documented on
        ``serialize_partition_key_to_wire``.
    :type partition_key_value: Any
    :param container_rid: The container's resource id. ``None`` skips
        rid stamping; the caller is responsible for ensuring a rid
        reaches the wire when needed for recreate-detection.
    :type container_rid: Optional[str]
    :param enable_automatic_id_generation: Defaults to ``True``. When
        ``False``, a body without an id is left untouched and the
        request will be rejected server-side.
    :type enable_automatic_id_generation: bool
    :param indexing_directive: When supplied, written to
        ``options["indexingDirective"]``.
    :type indexing_directive: Optional[Any]
    :param no_response_on_write_default: The client-level
        ``no_response_on_write`` setting. Applied as a fallback only when the
        call carries no per-call ``no_response``.
    :type no_response_on_write_default: bool
    :param kwargs: Remaining customer kwargs. **Mutated** — recognised
        option-shortcut keys are popped via
        ``compose_options_from_kwargs``.
    :type kwargs: Optional[Dict[str, Any]]
    :returns: ``(prepared, item_id)``. ``item_id`` is the id the body
        now carries, or ``""`` when no id was present and minting was
        disabled.
    :rtype: Tuple[PreparedRequest, str]
    """
    # Translate kwarg shortcuts to internal option keys.
    options = compose_options_from_kwargs(kwargs if kwargs is not None else {})

    # Two non-kwarg-shortcut option keys the legacy create_item path
    # also writes directly.
    options["disableAutomaticIdGeneration"] = not enable_automatic_id_generation
    if indexing_directive is not None:
        options["indexingDirective"] = indexing_directive

    # Fall back to the client-level no_response_on_write setting when the
    # call did not pass a per-call no_response.
    apply_no_response_on_write_default(options, no_response_on_write_default)

    if container_rid is not None:
        stamp_container_rid(
            options,
            container_link,
            get_rid=lambda _link: container_rid,
        )

    item_id = ensure_item_id(body, generate=enable_automatic_id_generation)
    if item_id is None:
        item_id = ""

    partition_key_header = serialize_partition_key_to_wire(partition_key_value)
    body_bytes = serialize_body_to_bytes(body)

    # Build the wire-headers map from the options dict. Shared across all
    # point operations via ``flatten_options_to_headers`` (it also
    # comma-joins list-valued trigger includes the way the legacy path does).
    headers: Dict[str, Any] = flatten_options_to_headers(options)
    if container_rid is not None:
        # Keep an explicit copy under the canonical key so a backend
        # that bypasses ``options`` still sees the rid.
        headers[Constants.ContainerRID] = container_rid

    # timeout (seconds, float) is the customer-facing overall request
    # timeout. On the legacy path azure-core consumes it; the rust
    # path bypasses azure-core, so we copy the value into a dedicated
    # header the binding reads into its typed timeout policy. The
    # kwarg is not popped -- the legacy path still needs it intact.
    if kwargs is not None and "timeout" in kwargs:
        timeout_value = kwargs.get("timeout")
        if timeout_value is not None:
            headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout_value

    prepared = PreparedRequest(
        op=OP_CREATE_ITEM,
        container_link=container_link,
        body_bytes=body_bytes,
        partition_key_header=partition_key_header,
        headers=headers,
        # Pass the id Python already resolved so the binding does not re-parse the
        # whole (possibly large) body just to read one field. Only a non-empty
        # string id qualifies; "" / non-string is left unset so the binding's
        # body-parse fallback reproduces the existing missing/non-string-id error.
        item_id=item_id if isinstance(item_id, str) and item_id else None,
    )
    return prepared, item_id


def build_delete_item_prepared(
    *,
    container_link: str,
    item_id: str,
    partition_key_value: Any,
    container_rid: Optional[str],
    kwargs: Optional[Dict[str, Any]] = None,
) -> PreparedRequest:
    """Build a ``PreparedRequest`` for a single ``delete_item`` call.

    Pure: does not read caches, does not extract the partition-key
    from a body (delete has no body to inspect). The caller has done
    those because they require a ``CosmosClientConnection``.

    :param container_link: Container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``.
    :type container_link: str
    :param item_id: The id of the document to delete. The binding
        carries it on ``PreparedRequest.item_id`` because there is no
        body to extract it from.
    :type item_id: str
    :param partition_key_value: PK value the caller supplied or
        extracted via ``Container._set_partition_key``. Accepted shapes
        are documented on ``serialize_partition_key_to_wire``.
    :type partition_key_value: Any
    :param container_rid: The container's resource id. ``None`` skips
        rid stamping; the caller is responsible for ensuring a rid
        reaches the wire when needed for recreate-detection.
    :type container_rid: Optional[str]
    :param kwargs: Remaining customer kwargs. **Mutated** — recognised
        option-shortcut keys are popped via
        ``compose_options_from_kwargs``.
    :type kwargs: Optional[Dict[str, Any]]
    :returns: The prepared request.
    :rtype: PreparedRequest
    """
    # Translate kwarg shortcuts to internal option keys.
    options = compose_options_from_kwargs(kwargs if kwargs is not None else {})

    if container_rid is not None:
        stamp_container_rid(
            options,
            container_link,
            get_rid=lambda _link: container_rid,
        )

    partition_key_header = serialize_partition_key_to_wire(partition_key_value)

    # Build the wire-headers map from the options dict (shared across all
    # point operations -- see ``flatten_options_to_headers``). The
    # accessCondition -> If-Match / If-None-Match translation and the
    # trigger-include comma-join both live there.
    headers: Dict[str, Any] = flatten_options_to_headers(options)
    if container_rid is not None:
        headers[Constants.ContainerRID] = container_rid

    # timeout (seconds, float) rides under a dedicated header the
    # binding reads into the driver's typed timeout policy. Same
    # mechanism as create_item.
    if kwargs is not None and "timeout" in kwargs:
        timeout_value = kwargs.get("timeout")
        if timeout_value is not None:
            headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout_value

    return PreparedRequest(
        op=OP_DELETE_ITEM,
        container_link=container_link,
        body_bytes=b"",
        partition_key_header=partition_key_header,
        headers=headers,
        item_id=item_id,
    )


def build_read_item_prepared(
    *,
    container_link: str,
    item_id: str,
    partition_key_value: Any,
    container_rid: Optional[str],
    kwargs: Optional[Dict[str, Any]] = None,
) -> PreparedRequest:
    """Build a ``PreparedRequest`` for a single ``read_item`` call.

    Pure: does not read caches. Same structure as
    ``build_delete_item_prepared`` — both are bodiless, both translate
    ``accessCondition`` to ``If-Match`` / ``If-None-Match``, both carry
    the document id on ``PreparedRequest.item_id``. Read adds one
    header: ``x-ms-dedicatedgateway-max-age`` from
    ``options["maxIntegratedCacheStaleness"]``, emitted **only when
    the value is truthy** so that ``0`` ships no header (matching the
    legacy behaviour, where ``0`` is a documented no-op).

    :param container_link: Container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``.
    :type container_link: str
    :param item_id: The id of the document to read. The binding carries
        it on ``PreparedRequest.item_id`` because GET has no body.
    :type item_id: str
    :param partition_key_value: PK value the caller supplied. Accepted
        shapes are documented on ``serialize_partition_key_to_wire``.
    :type partition_key_value: Any
    :param container_rid: The container's resource id, or ``None`` to
        skip rid stamping.
    :type container_rid: Optional[str]
    :param kwargs: Remaining customer kwargs. **Mutated** — recognised
        option-shortcut keys are popped via
        ``compose_options_from_kwargs``.
    :type kwargs: Optional[Dict[str, Any]]
    :returns: The prepared request.
    :rtype: PreparedRequest
    """
    # Translate kwarg shortcuts to internal option keys.
    options = compose_options_from_kwargs(kwargs if kwargs is not None else {})

    if container_rid is not None:
        stamp_container_rid(
            options,
            container_link,
            get_rid=lambda _link: container_rid,
        )

    partition_key_header = serialize_partition_key_to_wire(partition_key_value)

    # Build the wire-headers map from the options dict (shared across all
    # point operations -- see ``flatten_options_to_headers``). That helper
    # owns the three read-relevant special cases: initialHeaders flatten,
    # accessCondition -> If-Match / If-None-Match, and
    # maxIntegratedCacheStaleness -> x-ms-dedicatedgateway-max-age
    # (truthy-only; ``0`` ships no header).
    headers: Dict[str, Any] = flatten_options_to_headers(options)
    if container_rid is not None:
        headers[Constants.ContainerRID] = container_rid

    # timeout (seconds, float) rides under a dedicated header the
    # binding reads into the driver's typed timeout policy. Same
    # mechanism as create_item / delete_item.
    if kwargs is not None and "timeout" in kwargs:
        timeout_value = kwargs.get("timeout")
        if timeout_value is not None:
            headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout_value

    return PreparedRequest(
        op=OP_READ_ITEM,
        container_link=container_link,
        body_bytes=b"",
        partition_key_header=partition_key_header,
        headers=headers,
        item_id=item_id,
    )


def _build_write_with_body_prepared(
    *,
    op: str,
    container_link: str,
    body: Dict[str, Any],
    partition_key_value: Any,
    container_rid: Optional[str],
    access_condition: Optional[Dict[str, Any]] = None,
    item_id: Optional[str] = None,
    no_response_on_write_default: bool = False,
    kwargs: Optional[Dict[str, Any]] = None,
) -> PreparedRequest:
    """Build a ``PreparedRequest`` for a write-with-body op that never mints an id.

    Shared by ``build_upsert_item_prepared`` and
    ``build_replace_item_prepared`` -- the two are byte-identical on the
    wire except for the ``op`` discriminator (which the backend maps to
    the binding's ``upsert_item`` vs ``replace_item`` entry point, i.e. an
    insert-or-replace POST vs an overwrite-only PUT) and the ``item_id``
    slot. Both:

    * carry the document body and serialise it to JSON bytes;
    * never mint an id (``disableAutomaticIdGeneration`` is always
      ``True``); a body without an id is rejected server-side, matching the
      legacy ``UpsertItem`` / ``ReplaceItem`` contract;
    * honour ``etag`` / ``match_condition`` by emitting the matching
      ``If-Match`` / ``If-None-Match`` header from ``access_condition``
      (the same translation ``build_delete_item_prepared`` does).

    The difference is *which* id the wire URL uses. Upsert has no separate
    ``item`` argument, so it leaves ``item_id`` unset and the binding reads
    the id out of the body. Replace names an existing ``item``, so the
    caller passes that resolved id as ``item_id`` and the binding uses it
    for the URL (matching the legacy ``ReplaceItem``, whose URL id is the
    resolved document link); the body still carries its own id for the
    payload.

    Pure: does not read caches, does not extract the partition key from the
    body. The caller has done those because they require a
    ``CosmosClientConnection``.

    :param op: The ``OP_*`` discriminator (``OP_UPSERT_ITEM`` or
        ``OP_REPLACE_ITEM``).
    :type op: str
    :param container_link: Container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``.
    :type container_link: str
    :param body: The Cosmos document. Serialised as-is; **not mutated**.
    :type body: Dict[str, Any]
    :param partition_key_value: PK value already extracted from the body
        (or supplied by the caller). Accepted shapes are documented on
        ``serialize_partition_key_to_wire``.
    :type partition_key_value: Any
    :param container_rid: The container's resource id, or ``None`` to skip
        rid stamping.
    :type container_rid: Optional[str]
    :param access_condition: The ``{"type": ..., "condition": ...}`` shape
        the legacy options build produced from the
        ``(etag, match_condition)`` pair, or ``None``. Emitted as
        ``If-Match`` / ``If-None-Match``.
    :type access_condition: Optional[Dict[str, Any]]
    :param item_id: The id of the document the wire URL targets, when the
        op names one explicitly (``replace_item``). ``None`` for ops that
        derive the id from the body (``upsert_item``).
    :type item_id: Optional[str]
    :param no_response_on_write_default: The client-level
        ``no_response_on_write`` setting. Applied as a fallback only when the
        call carries no per-call ``no_response``.
    :type no_response_on_write_default: bool
    :param kwargs: Remaining customer kwargs. **Mutated** -- recognised
        option-shortcut keys are popped via
        ``compose_options_from_kwargs``.
    :type kwargs: Optional[Dict[str, Any]]
    :returns: The prepared request.
    :rtype: PreparedRequest
    """
    # Translate kwarg shortcuts to internal option keys.
    options = compose_options_from_kwargs(kwargs if kwargs is not None else {})

    # Both ops target a specific id (the one inside the body), so neither
    # mints one -- the same value the legacy paths write unconditionally.
    options["disableAutomaticIdGeneration"] = True

    # Fall back to the client-level no_response_on_write setting when the
    # call did not pass a per-call no_response.
    apply_no_response_on_write_default(options, no_response_on_write_default)

    # The caller computed the access-condition on the legacy options build
    # (``etag`` / ``match_condition`` -> accessCondition); inject it so the
    # shared header loop below emits the wire header. A write-with-body op
    # cannot seed ``request_options`` the way the bodiless delete / read
    # prep do without leaking the partition key into the headers map --
    # hence the explicit parameter.
    if access_condition is not None:
        options["accessCondition"] = access_condition

    if container_rid is not None:
        stamp_container_rid(
            options,
            container_link,
            get_rid=lambda _link: container_rid,
        )

    partition_key_header = serialize_partition_key_to_wire(partition_key_value)
    body_bytes = serialize_body_to_bytes(body)

    # Upsert (item_id is None) derives the wire id from the body. Python already
    # holds the document dict, so pass the body's id through on
    # PreparedRequest.item_id and let the binding skip re-parsing the whole
    # (possibly large) body just to read one field. Only a non-empty string id
    # qualifies; anything else is left unset so the binding's body-parse fallback
    # reproduces the existing missing/non-string-id error. Replace passes an
    # explicit item_id (the URL target) and is left untouched -- its id must come
    # from the `item` argument, never the body.
    if item_id is None:
        body_id = body.get("id")
        if isinstance(body_id, str) and body_id:
            item_id = body_id

    # Build the wire-headers map from the options dict (shared across all
    # point operations -- see ``flatten_options_to_headers``). That helper
    # flattens initialHeaders and translates accessCondition ->
    # If-Match / If-None-Match (same block delete / read use).
    headers: Dict[str, Any] = flatten_options_to_headers(options)
    if container_rid is not None:
        headers[Constants.ContainerRID] = container_rid

    # timeout (seconds, float) rides under a dedicated header the binding
    # reads into the driver's typed timeout policy. Same mechanism as
    # create_item / delete_item / read_item.
    if kwargs is not None and "timeout" in kwargs:
        timeout_value = kwargs.get("timeout")
        if timeout_value is not None:
            headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout_value

    return PreparedRequest(
        op=op,
        container_link=container_link,
        body_bytes=body_bytes,
        partition_key_header=partition_key_header,
        headers=headers,
        item_id=item_id,
    )


def build_upsert_item_prepared(
    *,
    container_link: str,
    body: Dict[str, Any],
    partition_key_value: Any,
    container_rid: Optional[str],
    access_condition: Optional[Dict[str, Any]] = None,
    no_response_on_write_default: bool = False,
    kwargs: Optional[Dict[str, Any]] = None,
) -> PreparedRequest:
    """Build a ``PreparedRequest`` for a single ``upsert_item`` call.

    Thin wrapper over ``_build_write_with_body_prepared`` with the
    ``OP_UPSERT_ITEM`` discriminator. Upsert is the write-with-body
    sibling of ``create_item`` that never mints an id and honours
    ``etag`` / ``match_condition`` (insert-only or version-guarded
    replace); the insert-or-replace behaviour rides on the discriminator,
    so no ``x-ms-documentdb-is-upsert`` header is stamped here -- the
    backend's upsert entry point owns that.

    See ``_build_write_with_body_prepared`` for the per-parameter docs.

    :rtype: PreparedRequest
    """
    return _build_write_with_body_prepared(
        op=OP_UPSERT_ITEM,
        container_link=container_link,
        body=body,
        partition_key_value=partition_key_value,
        container_rid=container_rid,
        access_condition=access_condition,
        no_response_on_write_default=no_response_on_write_default,
        kwargs=kwargs,
    )


def build_replace_item_prepared(
    *,
    container_link: str,
    body: Dict[str, Any],
    item_id: str,
    partition_key_value: Any,
    container_rid: Optional[str],
    access_condition: Optional[Dict[str, Any]] = None,
    no_response_on_write_default: bool = False,
    kwargs: Optional[Dict[str, Any]] = None,
) -> PreparedRequest:
    """Build a ``PreparedRequest`` for a single ``replace_item`` call.

    Thin wrapper over ``_build_write_with_body_prepared`` with the
    ``OP_REPLACE_ITEM`` discriminator. Replace is the overwrite-only
    write-with-body op: the ``body`` is the new content (serialised as-is,
    no id minting -- matching the legacy ``ReplaceItem`` which always set
    ``disableAutomaticIdGeneration``), and ``etag`` / ``match_condition``
    become the version guard (``If-Match: <etag>`` -> 412 on a stale etag).

    Unlike upsert, replace names an existing document: ``item_id`` is the
    id of the document to overwrite (resolved from the ``item`` argument by
    the container method), and it -- **not** the body's own id -- is what
    the binding puts in the wire URL. That matches the legacy ``ReplaceItem``
    and prevents a body whose id disagreed with ``item`` from silently
    overwriting the wrong document. The overwrite-vs-insert behaviour rides
    on the discriminator, which the backend maps to the binding's
    ``replace_item`` entry point (driver ``OperationType::Replace``).

    See ``_build_write_with_body_prepared`` for the per-parameter docs.

    :param item_id: The id of the document to overwrite (the resolved
        ``item`` argument). Carried on ``PreparedRequest.item_id``.
    :type item_id: str
    :rtype: PreparedRequest
    """
    return _build_write_with_body_prepared(
        op=OP_REPLACE_ITEM,
        container_link=container_link,
        body=body,
        partition_key_value=partition_key_value,
        container_rid=container_rid,
        access_condition=access_condition,
        item_id=item_id,
        no_response_on_write_default=no_response_on_write_default,
        kwargs=kwargs,
    )


# The public patch vocabulary spells increment ``incr``; the driver spells
# it ``increment``. Map only this op; every other op-code (add / set /
# replace / remove / move) is identical on both sides.
_PATCH_OP_INCREMENT_PUBLIC = "incr"
_PATCH_OP_INCREMENT_DRIVER = "increment"


def build_patch_operations_payload(patch_operations: Any) -> Dict[str, Any]:
    """Build the driver's ``PatchInstructions`` body from ``patch_operations``.

    Returns ``{"operations": [...]}``. The one op-code that differs between
    the public and driver spellings (``incr`` vs ``increment``) is
    translated via a shallow copy, so the caller's list is not mutated.

    :param patch_operations: The public list of patch-operation dicts.
    :type patch_operations: Any
    :returns: The ``{"operations": [...]}`` payload dict.
    :rtype: Dict[str, Any]
    """
    translated = []
    for operation in patch_operations:
        if isinstance(operation, dict) and operation.get("op") == _PATCH_OP_INCREMENT_PUBLIC:
            operation = {**operation, "op": _PATCH_OP_INCREMENT_DRIVER}
        translated.append(operation)
    return {"operations": translated}


def build_patch_item_prepared(
    *,
    container_link: str,
    item_id: str,
    patch_operations: Any,
    partition_key_value: Any,
    container_rid: Optional[str],
    no_response_on_write_default: bool = False,
    kwargs: Optional[Dict[str, Any]] = None,
) -> PreparedRequest:
    """Build a ``PreparedRequest`` for a single ``patch_item`` call.

    Names an existing document like delete / read (id on
    ``PreparedRequest.item_id``, partition key from the caller's argument)
    but carries a body: the patch-operations payload built by
    ``build_patch_operations_payload``. Pure -- the caller has already done
    any cache and partition-key lookups.

    Only unconditional, unguarded patches reach this builder, so it emits no
    ``If-Match`` header and serialises no filter condition; the helper routes
    the rest to the legacy path.

    :param container_link: Container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``.
    :type container_link: str
    :param item_id: The id of the document to patch. The binding carries it
        on ``PreparedRequest.item_id``.
    :type item_id: str
    :param patch_operations: The public list of patch-operation dicts.
    :type patch_operations: Any
    :param partition_key_value: PK value the caller supplied via
        ``Container._set_partition_key``. Accepted shapes are documented on
        ``serialize_partition_key_to_wire``.
    :type partition_key_value: Any
    :param container_rid: The container's resource id, or ``None`` to skip
        rid stamping.
    :type container_rid: Optional[str]
    :param no_response_on_write_default: The client-level
        ``no_response_on_write`` setting. Applied as a fallback only when the
        call carries no per-call ``no_response``.
    :type no_response_on_write_default: bool
    :param kwargs: Remaining customer kwargs. **Mutated** -- recognised
        option-shortcut keys are popped via ``compose_options_from_kwargs``.
    :type kwargs: Optional[Dict[str, Any]]
    :returns: The prepared request.
    :rtype: PreparedRequest
    """
    # Translate kwarg shortcuts to internal option keys.
    options = compose_options_from_kwargs(kwargs if kwargs is not None else {})

    # Patch carries a body like the other writes, so it honours the
    # client-level no_response_on_write fallback too.
    apply_no_response_on_write_default(options, no_response_on_write_default)

    if container_rid is not None:
        stamp_container_rid(
            options,
            container_link,
            get_rid=lambda _link: container_rid,
        )

    partition_key_header = serialize_partition_key_to_wire(partition_key_value)
    body_bytes = serialize_body_to_bytes(build_patch_operations_payload(patch_operations))

    # Build the wire-headers map from the options dict (shared across all
    # point operations -- see ``flatten_options_to_headers``). Patch never
    # carries an ``accessCondition`` (a guarded patch takes the legacy
    # path), so that branch of the helper is a no-op here.
    headers: Dict[str, Any] = flatten_options_to_headers(options)
    if container_rid is not None:
        headers[Constants.ContainerRID] = container_rid

    # timeout (seconds) rides under a dedicated header, same as the other ops.
    if kwargs is not None and "timeout" in kwargs:
        timeout_value = kwargs.get("timeout")
        if timeout_value is not None:
            headers[Constants.OVERALL_TIMEOUT_SECONDS] = timeout_value

    return PreparedRequest(
        op=OP_PATCH_ITEM,
        container_link=container_link,
        body_bytes=body_bytes,
        partition_key_header=partition_key_header,
        headers=headers,
        item_id=item_id,
    )

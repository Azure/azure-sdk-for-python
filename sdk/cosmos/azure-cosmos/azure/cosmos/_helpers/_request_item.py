# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Build prepared requests for the item operations.

Covers the six point operations on a document -- create, read, upsert, replace,
delete and patch -- which are the calls that carry a partition key and, for the
writes, a serialized body.

These differ from the database and container builders in that the caller has
already resolved the container metadata and extracted the partition key from
the document. What is left here is pure: mint an id if the operation needs one,
serialize the body, serialize the partition key to its header form, and flatten
the options. The Rust backend consumes the resulting ``PreparedRequest``; the
core-Python backend receives a separate ``LegacyOperation``. On a
Rust-selected client, that legacy operation is also the temporary fallback for
request shapes that have not been migrated yet.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .._backend.contracts import PreparedRequest
from .._backend.operations import (
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    OP_PATCH_ITEM,
    OP_READ_ITEM,
    OP_REPLACE_ITEM,
    OP_UPSERT_ITEM,
)
from .._constants import _Constants as Constants

from ._auto_id import ensure_item_id
from ._body_wire import serialize_body_to_bytes
from ._container_rid import stamp_container_rid
from ._options import compose_options_from_kwargs
from ._pk_wire import serialize_partition_key_to_wire
from ._request_headers import apply_no_response_on_write_default, flatten_options_to_headers


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

    Pure: does not resolve container metadata, trigger refreshes, or extract the
    partition key from the body. The caller supplies those resolved values.

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

    Pure: does not resolve container metadata or extract the partition key from
    a body (delete has no body to inspect). The caller supplies those values.

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

    Pure: does not resolve container metadata or extract the partition key from
    the body. The caller supplies those values.

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

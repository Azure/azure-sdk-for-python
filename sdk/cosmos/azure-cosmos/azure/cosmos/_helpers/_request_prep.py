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
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .._backend.base import (
    OP_CREATE_ITEM,
    OP_DELETE_ITEM,
    OP_READ_ITEM,
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


def build_create_item_prepared(
    *,
    container_link: str,
    body: Dict[str, Any],
    partition_key_value: Any,
    container_rid: Optional[str],
    enable_automatic_id_generation: bool = True,
    indexing_directive: Optional[Any] = None,
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

    # Headers map: every option-key except ``initialHeaders``, which is
    # flattened so the Rust binding's per-header pass-through receives
    # each inner ``x-ms-…`` directly. Customer-set entries override
    # helper-written entries (matches legacy precedence).
    headers: Dict[str, str] = {}
    for option_key, option_value in options.items():
        if option_key == "initialHeaders" and isinstance(option_value, dict):
            for inner_name, inner_value in option_value.items():
                headers[inner_name] = inner_value
            continue
        headers[option_key] = option_value
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

    # Headers map: every option-key except ``initialHeaders``, which is
    # flattened so the binding's per-header pass-through receives each
    # inner ``x-ms-…`` directly. Customer-set entries override
    # helper-written entries (matches legacy precedence).
    headers: Dict[str, str] = {}
    for option_key, option_value in options.items():
        if option_key == "initialHeaders" and isinstance(option_value, dict):
            for inner_name, inner_value in option_value.items():
                headers[inner_name] = inner_value
            continue
        # accessCondition is the internal shape the legacy options
        # build produces from etag + match_condition. Translate it to
        # the wire header here because the rust path does not run the
        # legacy header step that would normally emit it.
        if option_key == "accessCondition" and isinstance(option_value, dict):
            condition = option_value.get("condition")
            cond_type = option_value.get("type")
            if isinstance(condition, str) and cond_type == "IfMatch":
                headers["If-Match"] = condition
            elif isinstance(condition, str) and cond_type == "IfNoneMatch":
                headers["If-None-Match"] = condition
            continue
        headers[option_key] = option_value
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

    # Headers map: every option-key except three special-cased ones:
    #   * initialHeaders is flattened so each inner x-ms-... rides as
    #     its own header instead of as a nested dict.
    #   * accessCondition becomes If-Match / If-None-Match.
    #   * maxIntegratedCacheStaleness becomes
    #     x-ms-dedicatedgateway-max-age (truthy-only).
    headers: Dict[str, str] = {}
    for option_key, option_value in options.items():
        if option_key == "initialHeaders" and isinstance(option_value, dict):
            for inner_name, inner_value in option_value.items():
                headers[inner_name] = inner_value
            continue
        # Access-condition shape, same as delete. On read the common
        # case is If-None-Match (cache validation, success returns
        # 304); If-Match is the rare write-style precondition.
        if option_key == "accessCondition" and isinstance(option_value, dict):
            condition = option_value.get("condition")
            cond_type = option_value.get("type")
            if isinstance(condition, str) and cond_type == "IfMatch":
                headers["If-Match"] = condition
            elif isinstance(condition, str) and cond_type == "IfNoneMatch":
                headers["If-None-Match"] = condition
            continue
        # Dedicated-gateway max-age: emit only when truthy. Zero is a
        # documented no-op and must NOT produce
        # x-ms-dedicatedgateway-max-age: 0. None / missing also skip.
        if option_key == "maxIntegratedCacheStaleness":
            if option_value:
                headers[HttpHeaders.DedicatedGatewayCacheStaleness] = str(option_value)
            continue
        headers[option_key] = option_value
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


def build_upsert_item_prepared(
    *,
    container_link: str,
    body: Dict[str, Any],
    partition_key_value: Any,
    container_rid: Optional[str],
    access_condition: Optional[Dict[str, Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
) -> PreparedRequest:
    """Build a ``PreparedRequest`` for a single ``upsert_item`` call.

    Pure: does not read caches, does not extract the partition-key from
    the body. The caller has done those because they require a
    ``CosmosClientConnection``.

    Upsert is the write-with-body sibling of ``create_item``: it carries
    the document id inside the body and serialises the body to JSON
    bytes. It differs from create in two ways, both reflected here:

    * It never mints an id. ``disableAutomaticIdGeneration`` is always
      ``True`` and the body is serialised exactly as supplied; a body
      without an id is rejected server-side, matching the legacy
      ``UpsertItem`` contract.
    * It honours ``etag`` / ``match_condition`` (create deprecates and
      drops them). The caller computes the access-condition shape on the
      legacy options build and passes it in as ``access_condition``;
      this function emits the matching ``If-Match`` / ``If-None-Match``
      header, the same translation ``build_delete_item_prepared`` does.

    The insert-or-replace behaviour rides on the ``OP_UPSERT_ITEM``
    discriminator, so no ``x-ms-documentdb-is-upsert`` header is stamped
    here; the backend's upsert entry point owns that.

    :param container_link: Container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``.
    :type container_link: str
    :param body: The Cosmos document. Serialised as-is; **not mutated**
        (upsert never mints an id).
    :type body: Dict[str, Any]
    :param partition_key_value: PK value already extracted from the body
        (or supplied by the caller). Accepted shapes are documented on
        ``serialize_partition_key_to_wire``.
    :type partition_key_value: Any
    :param container_rid: The container's resource id. ``None`` skips
        rid stamping; the caller is responsible for ensuring a rid
        reaches the wire when needed for recreate-detection.
    :type container_rid: Optional[str]
    :param access_condition: The ``{"type": ..., "condition": ...}``
        shape the legacy options build produced from the
        ``(etag, match_condition)`` pair, or ``None`` when the caller
        passed neither. Emitted as ``If-Match`` / ``If-None-Match``.
    :type access_condition: Optional[Dict[str, Any]]
    :param kwargs: Remaining customer kwargs. **Mutated** — recognised
        option-shortcut keys are popped via
        ``compose_options_from_kwargs``.
    :type kwargs: Optional[Dict[str, Any]]
    :returns: The prepared request.
    :rtype: PreparedRequest
    """
    # Translate kwarg shortcuts to internal option keys.
    options = compose_options_from_kwargs(kwargs if kwargs is not None else {})

    # Upsert always disables id generation (it targets a specific id),
    # the same value the legacy ``upsert_item`` writes unconditionally.
    options["disableAutomaticIdGeneration"] = True

    # The caller computed the access-condition on the legacy options
    # build (``etag`` / ``match_condition`` -> accessCondition); inject
    # it so the shared header loop below emits the wire header. Upsert is
    # write-with-body, so it cannot seed ``request_options`` the way the
    # bodiless delete / read prep do without leaking the partition key
    # into the headers map -- hence the explicit parameter.
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

    # Headers map: every option-key except two special-cased ones:
    #   * initialHeaders is flattened so each inner x-ms-... rides as its
    #     own header (the binding's per-header pass-through).
    #   * accessCondition becomes If-Match / If-None-Match (same block as
    #     delete / read). Customer-set entries override helper-written
    #     entries (matches legacy precedence).
    headers: Dict[str, str] = {}
    for option_key, option_value in options.items():
        if option_key == "initialHeaders" and isinstance(option_value, dict):
            for inner_name, inner_value in option_value.items():
                headers[inner_name] = inner_value
            continue
        if option_key == "accessCondition" and isinstance(option_value, dict):
            condition = option_value.get("condition")
            cond_type = option_value.get("type")
            if isinstance(condition, str) and cond_type == "IfMatch":
                headers["If-Match"] = condition
            elif isinstance(condition, str) and cond_type == "IfNoneMatch":
                headers["If-None-Match"] = condition
            continue
        headers[option_key] = option_value
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
        op=OP_UPSERT_ITEM,
        container_link=container_link,
        body_bytes=body_bytes,
        partition_key_header=partition_key_header,
        headers=headers,
    )



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

Two public builders:

- ``build_create_item_prepared`` — full request with JSON body and
  id minting.
- ``build_delete_item_prepared`` — bodiless request; the document id
  rides on ``PreparedRequest.item_id``; reads ``accessCondition``
  out of the options dict and emits the equivalent ``If-Match`` /
  ``If-None-Match`` wire header for the binding to forward.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .._backend.base import OP_CREATE_ITEM, OP_DELETE_ITEM, PreparedRequest
from .._constants import _Constants as Constants
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

    # ``timeout`` (seconds, float) is the customer-facing overall
    # request timeout. On the legacy path azure-core consumes it; the
    # Rust path bypasses azure-core, so we forward the value under a
    # sentinel header name the binding lifts into its typed
    # ``EndToEndOperationLatencyPolicy``. We do not pop the kwarg —
    # the legacy path still needs it intact.
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
        # ``accessCondition`` is the internal shape ``_base.build_options``
        # produces from ``etag`` + ``match_condition``. Translate it to
        # the wire header here because the rust path does not run the
        # legacy ``GetHeaders`` step that would normally emit them.
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

    # ``timeout`` (seconds, float): forward under the sentinel header
    # the binding lifts into the driver's typed timeout policy. Same
    # mechanism as ``build_create_item_prepared``.
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



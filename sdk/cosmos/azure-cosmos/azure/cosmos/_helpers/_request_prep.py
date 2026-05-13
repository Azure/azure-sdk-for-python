# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Compose the five wire-prep pure helpers into a single ``PreparedRequest``.

.. note::
    **No production caller today.** This module assembles the
    ``PreparedRequest`` shape the future Rust adapter will hand to
    the Rust driver. Today, the production ``CreateItem`` path runs
    through ``_base.GetHeaders`` / the legacy connection helpers; this
    module is exercised only by ``tests/test_request_prep_unit.py``.
    Do **not** delete it as YAGNI — it is the seam the next phase
    (wiring ``CorePythonBackend.create_item`` as a real adapter)
    plugs into. When that adapter lands, ``ItemHelper.create_item``
    will start calling ``build_create_item_prepared`` instead of
    falling through to the legacy ``CreateItem``, and the five
    wire-prep helpers will replace ``_base.GetHeaders``'s inline
    serialisation. Until then the parallel paths are intentional and
    the redundancy is one-way (no runtime double-execution; the
    legacy path runs in production, the new path runs only in tests).

There are five small helpers that each handle one slice of request
preparation:

* ``_options.compose_options_from_kwargs`` — kwarg → option-key.
* ``_container_rid.stamp_container_rid`` — write the container rid into options.
* ``_auto_id.ensure_item_id`` — guarantee the document has an id.
* ``_pk_wire.serialize_partition_key_to_wire`` — partition key → header string.
* ``_body_wire.serialize_body_to_bytes`` — document → wire bytes.

This module is the first place all five run together. It is a *pure*
function: it takes already-derived inputs (the partition-key value,
the container rid) and returns a ``PreparedRequest`` plus the
final document id. The caller — typically an item helper that owns
the ``CosmosClientConnection`` and the container-properties cache —
is responsible for the side-effectful inputs (cache lookups, PK
extraction from the body using the container's PK definition).

Keeping the side-effect-free composition isolated here gives us two
properties the future response-parse adapter depends on:

1. The composition is unit-testable in milliseconds with no
   ``CosmosClientConnection``, no cache, no network. The tests in
   ``tests/test_request_prep_unit.py`` cover every branch.
2. Both backends can be handed the *same* ``PreparedRequest`` and
   produce the same wire bytes. That is the byte-for-byte parity
   guarantee that lets the rust path be a drop-in replacement for the
   core-python path.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .._backend.base import PreparedRequest
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

    The function performs the side-effect-free portion of request
    preparation: option composition, id minting, partition-key
    serialization, body serialization. It does **not** read the
    container-properties cache, does **not** trigger a refresh, and
    does **not** extract the partition-key value from the body — the
    caller has already done those because they require a
    ``CosmosClientConnection``.

    :param container_link: The container self-link, e.g.
        ``"dbs/{db}/colls/{coll}"``. Goes straight onto
        ``PreparedRequest.container_link``.
    :type container_link: str
    :param body: The Cosmos document. **Mutated in place** when the
        body lacks an ``id`` and ``enable_automatic_id_generation``
        is ``True`` — a fresh UUID4 is written to ``body["id"]``. The
        caller is responsible for copying the body first if they
        need to preserve the original.
    :type body: Dict[str, Any]
    :param partition_key_value: The partition-key value already
        extracted from the body (or supplied by the caller). Accepted
        shapes are documented in
        ``_helpers/_pk_wire.serialize_partition_key_to_wire``: single
        scalar, ``_Empty``/``_Undefined`` sentinels, or a
        list/tuple for hierarchical keys. The function does not
        extract this from the body itself.
    :type partition_key_value: Any
    :param container_rid: The container's resource id (the immutable
        internal id, not the user-facing name). Already looked up by
        the caller. ``None`` means the container hasn't been read
        yet and the helper will skip rid stamping — the caller is on
        the hook for ensuring a rid is present before the request
        leaves, otherwise the container-recreate-detection retry
        won't fire.
    :type container_rid: Optional[str]
    :param enable_automatic_id_generation: Defaults to ``True`` to
        match the user-facing ``Container.create_item`` default.
        Setting it to ``False`` means a body without an id is left
        without an id (and the request will fail server-side).
    :type enable_automatic_id_generation: bool
    :param indexing_directive: When supplied, written to
        ``options["indexingDirective"]``. Normally a
        ``documents.IndexingDirective`` enum value but the helper
        does not interpret it — the legacy ``_base.GetHeaders``
        consumer reads it and writes the matching wire header.
    :type indexing_directive: Optional[Any]
    :param kwargs: The remaining customer kwargs after the call site
        has stripped its own (``populate_query_metrics`` etc.). Run
        through ``compose_options_from_kwargs`` to extract every
        recognised kwarg into the options dict. **Mutated** — the
        same kwargs dict the caller is about to forward to azure-core
        gets its option-shortcut keys popped out so the same value
        is not handed down twice.
    :type kwargs: Optional[Dict[str, Any]]
    :returns: A two-tuple ``(prepared, item_id)``. ``prepared`` is the
        immutable ``PreparedRequest`` ready to hand to the backend.
        ``item_id`` is the document id the body now carries — useful
        for pinning against an ``ItemReference`` constructor (the
        rust path needs this to assert body and routing reference
        agree on the id).
    :rtype: Tuple[PreparedRequest, str]
    """
    # B1: Translate kwarg shortcuts into the internal option-key
    # vocabulary. Mutates kwargs by popping each recognised key.
    options = compose_options_from_kwargs(kwargs if kwargs is not None else {})

    # The legacy create_item path also writes these two non-kwarg-
    # shortcut option keys directly. We do the same so the resulting
    # options dict is byte-identical to what the legacy path produced
    # for the same inputs.
    options["disableAutomaticIdGeneration"] = not enable_automatic_id_generation
    if indexing_directive is not None:
        options["indexingDirective"] = indexing_directive

    # B2: Container rid. The helper signs no contract about *how* the
    # rid was obtained; if the caller already had it, we stamp it.
    # Skipping when None means the caller decided rid stamping does
    # not apply (test fixtures, future paths). The legacy path always
    # has a rid by the time it reaches its create_item call.
    if container_rid is not None:
        stamp_container_rid(
            options,
            container_link,
            get_rid=lambda _link: container_rid,
        )

    # B3: Make sure the body has an id. Mutates body in place when
    # minting; no-op when the body already has a truthy id. The
    # returned id is the value the body now carries — same string
    # every time within one call, so the rust path can pin its
    # ItemReference id against it.
    item_id = ensure_item_id(body, generate=enable_automatic_id_generation)
    if item_id is None:
        # The "I told you not to mint and there is no id" case. The
        # request will be rejected server-side with a 400. We surface
        # an empty string so the return type stays str rather than
        # Optional[str] for the common case; the caller can detect
        # the empty value and skip the id-pinning assertion if they
        # care to.
        item_id = ""

    # B4: Partition key value -> wire header string. The caller has
    # already extracted the value; we just serialize it.
    partition_key_header = serialize_partition_key_to_wire(partition_key_value)

    # B5: Body -> JSON bytes. Compact separators, key order
    # preserved, no incidental whitespace.
    body_bytes = serialize_body_to_bytes(body)

    # The headers map on PreparedRequest is everything *other* than
    # the partition-key header (which has its own dedicated slot
    # because it is universal across operations). We pass the option-
    # dict keys so the backend has access to them; the existing
    # ``_base.GetHeaders`` will translate option-keys to wire
    # headers when the core-python backend builds its azure-core
    # request. This is a temporary shape: once the response-parse adapter is wired in, the
    # helper returns wire-ready headers directly.
    headers: Dict[str, str] = {}
    for option_key, option_value in options.items():
        headers[option_key] = option_value
    if container_rid is not None:
        # Mirror the constant key the rest of the SDK reads. Belt-and-
        # braces: stamp_container_rid above already wrote it into
        # options, but the headers map gets its own copy so a future
        # backend that bypasses options still has the rid.
        headers[Constants.ContainerRID] = container_rid

    prepared = PreparedRequest(
        container_link=container_link,
        body_bytes=body_bytes,
        partition_key_header=partition_key_header,
        headers=headers,
    )
    return prepared, item_id

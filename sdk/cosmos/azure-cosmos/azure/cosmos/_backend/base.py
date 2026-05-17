# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract backend type plus the two small data classes used to talk to it.

Every concrete backend (today: ``RustBackend`` only — the
"core-python" selection is represented by the absence of a backend,
not by a placeholder class)
implements the ``CosmosBackend`` ABC defined here. Container methods
call the backend through this ABC so that the dispatch site never has
to know which underlying transport actually ran the request.

The backend exposes a single dispatch method, ``execute(prepared)``.
The operation kind (create_item, read_item, query_items, …) is carried
on the ``PreparedRequest`` itself as the ``op`` field. Adding a new
operation is one new value of ``op`` plus one new branch inside each
backend's ``execute`` — the call sites and the dispatch contract do
not change.

``PreparedRequest`` is what the helper hands a backend; ``BackendResponse``
is what the helper expects back. Both are frozen dataclasses (immutable
after construction) so a backend cannot accidentally mutate the input it
was handed or the output it produced.
"""
from __future__ import annotations

import abc
import re as _re
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from azure.core.utils import CaseInsensitiveDict


# ---------------------------------------------------------------------------
# Operation discriminator values
# ---------------------------------------------------------------------------
#
# These are the string values the ``op`` field on ``PreparedRequest``
# can carry. Backends dispatch on them inside their ``execute`` method.
# Only ``OP_CREATE_ITEM`` exists today; the other item operations land
# as the binding gains support.

OP_CREATE_ITEM = "create_item"


@dataclass(frozen=True)
class PreparedRequest:
    """A single Cosmos operation, fully prepared and ready to send.

    The helper layer that owns request preparation builds one of these
    from the user's call arguments. Both backends receive the *same*
    instance so neither one re-derives the wire format from the
    original kwargs; that is the only way to guarantee byte-for-byte
    parity between them.
    """

    #: Which operation this request describes. One of the ``OP_*``
    #: constants above. Backends dispatch on this inside ``execute``.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"``.
    container_link: str

    #: The request body, already serialized to JSON bytes by the helper.
    body_bytes: bytes

    #: The partition-key header value, already serialized to its on-wire
    #: JSON shape (e.g. ``'["customerA"]'`` for a single-value PK).
    partition_key_header: str

    #: Everything else that needs to ride on the request: triggers,
    #: indexing directive, intended-collection-rid, etc.
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BackendResponse:
    """Normalized shape every backend produces, regardless of transport.

    The core-python backend builds one of these from an azure-core
    ``HttpResponse``; the Rust backend builds one from the PyO3 return
    value. Code above the backend never branches on which backend
    handled the call — it just reads these fields.
    """

    #: HTTP status code returned by the service.
    status_code: int

    #: Cosmos sub-status code (header ``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Full response header map. Populated from the underlying response
    #: object so that long-tail headers (e.g. ``x-ms-cosmos-llsn``) survive
    #: the trip across the backend boundary.
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. May be empty for a 204 / no-content reply.
    body: bytes = b""

    #: Per-backend diagnostics blob the helper does not introspect. The
    #: core-python backend stores its existing diagnostics here; the Rust
    #: backend stores its structured diagnostics here.
    diagnostics: Any = None


class CosmosBackend(abc.ABC):
    """Abstract dispatch target for any Cosmos operation (sync variant).

    Every sync backend (today: ``RustBackend`` only) inherits
    from this class. The helper holds one of these by interface and
    calls ``execute`` on it without knowing which concrete backend it
    has. The operation kind is on ``prepared.op``; the backend is the
    one place that branches on it.

    Today, request preparation and response parsing still live in
    their existing locations (``Container.create_item`` and the
    ``CosmosClientConnection`` helpers), so a backend that returns
    ``None`` from ``execute`` is interpreted as "I have nothing to
    return; the caller should run its existing in-place
    implementation." Once the helper layer takes over request prep and
    response parsing the contract tightens so that every backend
    produces a real ``BackendResponse`` and the ``Optional`` annotations
    go away.
    """

    #: Short identifier used in the startup INFO log line emitted at
    #: client construction. Concrete subclasses set this from
    #: ``constants.BACKEND_NAME_CORE_PYTHON`` or
    #: ``constants.BACKEND_NAME_RUST``.
    name: str = "abstract"

    @abc.abstractmethod
    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single Cosmos operation.

        The operation kind is on ``prepared.op``; the backend dispatches
        on it. Returning ``None`` (the temporary contract until the
        helper layer lands) tells the caller to use its existing
        in-place implementation. Returning a ``BackendResponse`` tells
        the caller to use that response directly. ``prepared`` may be
        ``None`` while the caller still owns request preparation.
        """
        ...


# ---------------------------------------------------------------------------
# Driver error → BackendResponse recovery
# ---------------------------------------------------------------------------
#
# The compiled rust binding currently surfaces *every* driver error as
# a Python ``RuntimeError`` (see ``azure_cosmos_rust/src/lib.rs``). That
# includes successful HTTP round-trips that returned a non-2xx status
# code (409 Conflict, 404 Not Found, 412 Precondition Failed, etc.) —
# the driver returns those as ``Err`` rather than ``Ok(response)`` with
# the status code on it.
#
# Without help, customer code doing ``except CosmosResourceExistsError:``
# (the duplicate-id idempotency check) would silently break on the rust
# path: the 409 would surface as ``RuntimeError("driver execute_operation
# failed: Cosmos DB returned HTTP 409: Unknown")`` instead of the typed
# subclass.
#
# This helper recognises the driver's error-message shape and turns the
# RuntimeError back into a ``BackendResponse`` carrying the status code.
# The helper-layer parser (``parse_backend_response``) then routes that
# response through the typed-exception mapping the same way it would
# for a core-python failure.
#
# When the driver eventually exposes structured HTTP errors (tracked as
# gap ``R3-DRIVER-TYPED-HTTP-ERRORS``), this helper becomes a no-op
# (the regex won't match anything) and can be deleted.

_DRIVER_HTTP_STATUS_RE = _re.compile(r"\bCosmos DB returned HTTP\s+([1-5]\d{2})\b")


def recover_backend_response_from_driver_error(
    exc: BaseException,
) -> Optional[BackendResponse]:
    """Synthesise a ``BackendResponse`` from a driver ``RuntimeError`` if it carries an HTTP status.

    Returns ``None`` when the error is not a recognisable HTTP-status
    failure (genuine driver-internal error, network error, etc.) — the
    caller should re-raise in that case.

    The synthesised response carries:

    * ``status_code`` — the HTTP status parsed from the message.
    * ``sub_status = 0`` — the driver does not surface a sub-status
      with the error today; the parser will use 0.
    * ``headers = None`` — the error path does not carry response
      headers.
    * ``body`` — the original error message bytes, so
      ``extract_message_from_body`` has something to fall back on
      when populating the typed exception's ``message``.
    """
    msg = str(exc)
    match = _DRIVER_HTTP_STATUS_RE.search(msg)
    if match is None:
        return None
    status_code = int(match.group(1))
    if status_code < 100 or status_code > 599:
        return None
    return BackendResponse(
        status_code=status_code,
        sub_status=0,
        headers=None,
        body=msg.encode("utf-8"),
        diagnostics=None,
    )


# ---------------------------------------------------------------------------
# Response-header name normalisation (Rust binding → legacy spelling)
# ---------------------------------------------------------------------------
#
# The legacy core-python path surfaces some replication-progress headers
# *without* a ``cosmos-`` prefix (e.g. ``x-ms-llsn``,
# ``x-ms-quorum-acked-llsn``). The Rust driver models the same physical
# fields under their ``cosmos-``-prefixed wire names and the binding
# forwards them as-is. The two backends are emitting the *same* data
# under *different* keys, which would otherwise show up as "header only
# on rust" / "header only on core-python" parity failures even when both
# backends are working correctly.
#
# This helper makes the un-prefixed legacy spelling **also** available on
# the Rust path's response-headers dict. It is an **alias-add**, not a
# rename: the original ``cosmos-``-prefixed key stays in place, and the
# un-prefixed legacy name is added as a second key pointing at the same
# value. Customer code that reads either spelling works on both backends.
#
# Why alias-add and not rename?
#
#   * On the legacy core-python path the gateway emits the *prefixed*
#     names today (``x-ms-cosmos-llsn`` etc.), and azure-core's transport
#     surfaces them verbatim. A pure rename on the Rust side would make
#     ``x-ms-llsn`` appear only on Rust and ``x-ms-cosmos-llsn`` appear
#     only on core-python — the exact mismatch this helper was meant to
#     eliminate.
#   * Customer code in the wild reads *both* spellings depending on when
#     it was written. Surfacing both keys means no caller breaks.
#   * The parity diff matches because both backends now expose the
#     prefixed key (already true for core-python; alias-add provides it
#     on Rust too).
#
# Add a new entry only when you can name (a) the wire-level header on
# both sides and (b) the customer-facing read site that depends on the
# legacy spelling. Adding a one-way alias here without those two
# anchors makes the parity diff lie.

_RUST_PREFIXED_TO_LEGACY_ALIASES: Mapping[str, str] = {
    # LSN family — replica/replication-progress counters Cosmos has
    # historically surfaced under the un-prefixed name on the legacy
    # azure-core path. Customer monitoring code reads these for
    # replication-lag diagnostics.
    "x-ms-cosmos-llsn": "x-ms-llsn",
    "x-ms-cosmos-quorum-acked-llsn": "x-ms-quorum-acked-llsn",
    "x-ms-cosmos-item-llsn": "x-ms-item-llsn",
    # ``x-ms-cosmos-quorum-acked-lsn`` (no second L) → un-prefixed form
    # also used by some legacy callers.
    "x-ms-cosmos-quorum-acked-lsn": "x-ms-quorum-acked-lsn",
}


def normalize_response_headers(
    headers: Optional[Mapping[str, Any]],
) -> Optional[CaseInsensitiveDict]:
    """Add legacy-name aliases for the Rust binding's ``cosmos-``-prefixed LSN headers.

    Returns a fresh ``CaseInsensitiveDict`` that contains every key from
    the input *plus* an extra entry for each known prefixed→legacy alias,
    so customer code that reads either spelling on the Rust path finds
    the value. If the legacy alias is already present in the input
    (driver started emitting it on its own), the existing value wins.

    Passing ``None`` or an empty mapping returns ``None`` so callers can
    keep their existing ``if response.headers:`` guards unchanged.

    Lives at the backend boundary deliberately: applying the alias in
    the binding's own response path keeps every layer above it
    (``BackendResponse`` consumers, response parser,
    ``last_response_headers``, the parity harness) seeing both spellings,
    so they don't each have to re-implement the map.
    """
    if not headers:
        return None
    # Copy all original keys first, preserving insertion order.
    result = CaseInsensitiveDict()
    for raw_key, value in headers.items():
        result[raw_key] = value
    # Then add legacy-name aliases for any prefixed key the table knows
    # about, but never clobber a key that's already present.
    for prefixed, legacy in _RUST_PREFIXED_TO_LEGACY_ALIASES.items():
        if prefixed in result and legacy not in result:
            result[legacy] = result[prefixed]
    return result




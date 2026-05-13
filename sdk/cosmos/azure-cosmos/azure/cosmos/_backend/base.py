# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract backend type plus the two small data classes used to talk to it.

Every concrete backend (``CorePythonBackend``, ``RustBackend``)
implements the ``CosmosBackend`` ABC defined here. Container methods
call the backend through this ABC so that the dispatch site never has
to know which underlying transport actually ran the request.

``PreparedRequest`` is what the helper hands a backend; ``BackendResponse``
is what the helper expects back. Both are frozen dataclasses (immutable
after construction) so a backend cannot accidentally mutate the input it
was handed or the output it produced.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from azure.core.utils import CaseInsensitiveDict


@dataclass(frozen=True)
class PreparedRequest:
    """A single Cosmos operation, fully prepared and ready to send.

    The helper layer that owns request preparation builds one of these
    from the user's ``create_item`` arguments. Both backends receive
    the *same* instance so neither one re-derives the wire format from
    the original kwargs; that is the only way to guarantee byte-for-byte
    parity between them.
    """

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

    Every sync backend (``CorePythonBackend``, ``RustBackend``) inherits
    from this class. The container's dispatch site holds one of these by
    interface and calls ``create_item`` on it without knowing which
    concrete backend it has.

    Today, request preparation and response parsing still live in
    their existing locations (``Container.create_item`` and the
    ``CosmosClientConnection`` helpers), so a backend that returns
    ``None`` from ``create_item`` is interpreted as "I have nothing to
    return; the caller should run its existing in-place
    implementation." Once the helper layer takes over request prep and
    response parsing the contract tightens so that every backend
    produces a real ``BackendResponse`` and the ``Optional`` annotations
    go away.
    """

    #: Short identifier used in two places: the startup INFO log line
    #: emitted at client construction, and the per-request user-agent
    #: suffix (``backend=<name>``). Concrete subclasses set this from
    #: ``constants.BACKEND_NAME_CORE_PYTHON`` or
    #: ``constants.BACKEND_NAME_RUST``.
    name: str = "abstract"

    @abc.abstractmethod
    def create_item(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single ``create_item`` call.

        Returning ``None`` (the temporary contract until the helper
        layer lands) tells the caller to use its existing in-place
        implementation. Returning a ``BackendResponse`` tells the
        caller to use that response directly. ``prepared`` may be
        ``None`` while the caller still owns request preparation.
        """
        ...


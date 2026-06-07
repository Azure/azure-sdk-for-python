# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract backend type and the data classes used to talk to it.

Every concrete backend (today: ``RustBackend``; the "core-python"
selection is represented by the absence of a backend) implements the
``CosmosBackend`` ABC defined here.

Backends expose a single dispatch method, ``execute(prepared)``. The
operation kind (create_item, read_item, …) rides on the
``PreparedRequest.op`` field. Adding a new operation is one new ``op``
value plus one new branch in each backend's ``execute``.

``PreparedRequest`` and ``BackendResponse`` are frozen dataclasses so a
backend cannot accidentally mutate the input it received or the output
it produced.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from azure.core.utils import CaseInsensitiveDict


# Operation discriminator values for ``PreparedRequest.op``.
OP_CREATE_ITEM = "create_item"
OP_DELETE_ITEM = "delete_item"


@dataclass(frozen=True)
class PreparedRequest:
    """A single Cosmos operation, fully prepared and ready to send.

    Both backends receive the *same* instance so neither re-derives the
    wire format from the original kwargs.
    """

    #: One of the ``OP_*`` constants above.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"``.
    container_link: str

    #: Request body already serialized to JSON bytes. Empty for
    #: bodiless ops (e.g. ``delete_item``).
    body_bytes: bytes

    #: Partition-key header value already serialized to its on-wire
    #: JSON shape (e.g. ``'["customerA"]'``).
    partition_key_header: str

    #: Everything else that needs to ride on the request: triggers,
    #: indexing directive, intended-collection-rid, etc.
    headers: Mapping[str, str] = field(default_factory=dict)

    #: Target document id for ops where the id is not carried in
    #: ``body_bytes`` (``delete_item`` has no body). ``None`` for ops
    #: that derive the id from the body (``create_item``).
    item_id: Optional[str] = None


@dataclass(frozen=True)
class BackendResponse:
    """Normalised shape every backend produces, regardless of transport.

    Code above the backend never branches on which backend handled the
    call; it just reads these fields.
    """

    #: HTTP status code.
    status_code: int

    #: Cosmos sub-status code (``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Full response header map (long-tail headers preserved).
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. May be empty for 204 / no-content.
    body: bytes = b""

    #: Per-backend diagnostics blob the helper does not introspect.
    diagnostics: Any = None


class CosmosBackend(abc.ABC):
    """Abstract dispatch target for any Cosmos operation (sync).

    The helper holds one of these by interface and calls ``execute`` on
    it without knowing which concrete backend it has. The operation kind
    is on ``prepared.op``; the backend branches on it.

    Until the helper layer takes over request prep and response parsing
    for every operation, ``execute`` may return ``None`` to signal
    "caller should run the legacy in-place implementation." A returned
    ``BackendResponse`` is consumed by ``parse_backend_response``.
    """

    #: Short identifier used in the startup INFO log line. Subclasses
    #: set this from ``constants.BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    @abc.abstractmethod
    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single Cosmos operation.

        Dispatch on ``prepared.op``. Return ``None`` to let the caller
        run the legacy implementation, or a ``BackendResponse`` to have
        the caller parse the result.
        """
        ...


# ---------------------------------------------------------------------------
# Response-header name normalisation (Rust binding → legacy spelling)
# ---------------------------------------------------------------------------
#
# Some replication-progress headers (``x-ms-llsn``, ``x-ms-quorum-acked-llsn``, …)
# appear without a ``cosmos-`` prefix on the legacy core-python path. The Rust
# driver emits the same fields under their ``cosmos-``-prefixed wire names. To
# keep customer code reading either spelling working on both backends, we add the
# un-prefixed legacy name as an alias when the prefixed name is present; the
# prefixed key stays in place. Never clobber an existing entry.

_RUST_PREFIXED_TO_LEGACY_ALIASES: Mapping[str, str] = {
    "x-ms-cosmos-llsn": "x-ms-llsn",
    "x-ms-cosmos-quorum-acked-llsn": "x-ms-quorum-acked-llsn",
    "x-ms-cosmos-item-llsn": "x-ms-item-llsn",
    "x-ms-cosmos-quorum-acked-lsn": "x-ms-quorum-acked-lsn",
}


def normalize_response_headers(
    headers: Optional[Mapping[str, Any]],
) -> Optional[CaseInsensitiveDict]:
    """Add legacy-name aliases for the Rust binding's ``cosmos-``-prefixed LSN headers.

    Returns a fresh ``CaseInsensitiveDict`` containing every key from
    the input plus one alias entry for each known prefixed → legacy
    mapping. Existing legacy entries are never overwritten. ``None`` or
    empty input returns ``None``.
    """
    if not headers:
        return None
    result = CaseInsensitiveDict()
    for raw_key, value in headers.items():
        result[raw_key] = value
    for prefixed, legacy in _RUST_PREFIXED_TO_LEGACY_ALIASES.items():
        if prefixed in result and legacy not in result:
            result[legacy] = result[prefixed]
    return result


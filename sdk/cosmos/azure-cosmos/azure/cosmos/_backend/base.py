# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract backend type and the data classes used to talk to it.

``RustBackend`` is the backend going forward and the only one intended for
production use. The "core-python" selection -- represented by the absence
of a backend, which falls back to the legacy in-place implementation -- is
kept only for testing and comparison, not as a long-term alternative. Every
concrete backend implements the ``CosmosBackend`` ABC defined here.

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
OP_READ_ITEM = "read_item"
OP_UPSERT_ITEM = "upsert_item"
OP_REPLACE_ITEM = "replace_item"
OP_PATCH_ITEM = "patch_item"


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
    """Normalised shape every backend produces, regardless of which
    backend's HTTP stack sent the request.

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

    The helper already builds the ``PreparedRequest`` before calling ``execute``
    and parses the returned ``BackendResponse`` with ``parse_backend_response`` --
    it does this for every operation -- so a backend only has to send the
    request and report the reply. ``execute`` may still return ``None`` as a
    fallback hatch, which tells the helper to run the legacy in-place
    core-python implementation; that path is kept only for testing, not
    production.
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
# Response-header normalisation (Rust binding dict -> CaseInsensitiveDict)
# ---------------------------------------------------------------------------
#
# The Rust binding hands back a plain dict keyed by the gateway's wire
# header names. The legacy core-python path surfaces azure-core's
# ``CaseInsensitiveDict`` (it just does ``copy.copy(response.headers)`` --
# the raw gateway headers, no renaming or aliasing). To keep
# ``last_response_headers`` lookups case-insensitive and identical across
# both backends, we wrap the binding's dict in the same type. No keys are
# added or renamed: both backends surface exactly the header names the
# gateway emitted (e.g. ``x-ms-cosmos-llsn``, ``x-ms-item-lsn``, ``lsn``).


def normalize_response_headers(
    headers: Optional[Mapping[str, Any]],
) -> Optional[CaseInsensitiveDict]:
    """Wrap the Rust binding's response-header dict in a ``CaseInsensitiveDict``.

    A pure type-normalisation step: every key from the input is copied
    through unchanged so the rust path surfaces the same gateway header
    names the legacy path does. ``None`` or empty input returns ``None``.
    """
    if not headers:
        return None
    result = CaseInsensitiveDict()
    for raw_key, value in headers.items():
        result[raw_key] = value
    return result

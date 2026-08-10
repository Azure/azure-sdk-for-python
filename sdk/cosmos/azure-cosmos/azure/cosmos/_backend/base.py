# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The abstract backend that every concrete sync backend implements.

``RustBackend`` is the backend going forward and the only one intended for
production use. The "core-python" selection runs the legacy in-place
implementation through the explicit :class:`~azure.cosmos._backend.legacy.LegacyBackend`
(see that module), kept only for testing and comparison, not as a long-term
alternative. Every concrete backend implements the :class:`CosmosBackend` ABC
defined here.

Backends expose three dispatch methods, one per reply shape. ``execute`` and
``execute_pages`` are implemented today (the latter only for ``query_items`` /
``read_all_items``); ``execute_batch`` raises ``NotImplementedError`` until the
batch operation is added. Defining it now means adding that operation does not
change this file.

* ``execute`` -- one request, one reply (``BackendResponse``), for every
  single-reply operation (database create, item CRUD, feed-range, offer).
* ``execute_pages`` -- one request, one page of results (``QueryPage``), for
  the query and read-many operations. One call fetches one page; the caller
  re-invokes it per page, carrying the previous page's continuation forward.
* ``execute_batch`` -- a transactional batch, one result per operation
  (``BatchResponse``). Reserved; not implemented yet.

The operation kind (create_item, read_item, query_items, ...) is carried on the
``PreparedRequest`` / ``PreparedQuery`` ``op`` field, and is one of the names in
:mod:`~azure.cosmos._backend.operations`. Adding a single-reply operation is one
new ``op`` value plus one new branch in each backend's ``execute``; adding a
query/read-many operation is the same for ``execute_pages``.

The request and reply objects those methods take and return live in
:mod:`~azure.cosmos._backend.contracts`, because the async backends in
:mod:`azure.cosmos.aio._backend` share them with this module.
"""
from __future__ import annotations

import abc
from typing import Any, Callable, Iterator, Optional

from ._fallback_metrics import record_rust_compatibility_fallback
from .contracts import (
    BackendResponse,
    BatchResponse,
    LegacyOperation,
    PreparedBatch,
    PreparedQuery,
    PreparedRequest,
    QueryPage,
)
from .errors import BackendProtocolError


class CosmosBackend(abc.ABC):
    """Abstract dispatch target for any Cosmos operation (sync).

    A per-family coordinator (:class:`~azure.cosmos._helpers.item_helper.ItemHelper`,
    the throughput functions in
    :mod:`~azure.cosmos._helpers.container_throughput_helper` and
    :mod:`~azure.cosmos._helpers.database_throughput_helper`, and the feed-range
    functions in :mod:`~azure.cosmos._helpers.feed_range_helper`) holds one of
    these by interface and drives its operations through :meth:`run_operation`
    or :meth:`run_page_operation` without knowing which concrete backend it
    has. Engine selection and legacy fallback happen behind this interface: a
    rust-backed client holds a
    :class:`RustBackend` and a core-python client holds a
    :class:`~azure.cosmos._backend.legacy.LegacyBackend`, and every coordinator
    treats both the same -- none of them branch on ``None``, on which concrete
    backend they hold, or on a wire primitive returning ``None``. The operation
    kind is on ``prepared.op``; the backend branches on it.

    ``execute`` and ``execute_pages`` are the wire-level primitives used behind
    those two coordinator methods. The core-python
    :class:`~azure.cosmos._backend.legacy.LegacyBackend` is **not**
    ``PreparedRequest``-driven -- its work is the original public call arguments,
    not a wire request -- so it does not implement the wire primitives and
    instead overrides :meth:`run_operation` and :meth:`run_page_operation` to
    run the legacy operation.
    """

    #: Short identifier used in the startup INFO log line. Subclasses
    #: set this from ``constants.BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    @abc.abstractmethod
    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single Cosmos operation on the wire and return the raw reply.

        Dispatch on ``prepared.op`` and return a ``BackendResponse`` for the
        caller to parse. This is the rust wire primitive; a backend that does
        not send prepared requests (the core-python legacy backend) does not
        implement it.
        """
        ...

    def resolve_container_metadata(self, container_link: str) -> Optional[BackendResponse]:
        """Resolve container metadata through this backend when supported."""
        return None

    def run_operation(
        self,
        *,
        build_prepared: Callable[[], PreparedRequest],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[BackendResponse], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
        allow_legacy_fallback: bool = True,
        unsupported_message: Optional[str] = None,
    ) -> Any:
        """Run one engine-selected operation end to end and return the final result.

        This is the single entry point every family coordinator uses (items,
        throughput, feed-range) so none of them ever has to interpret ``None``
        from selection or from ``execute`` to decide whether to call the legacy
        path -- the chosen backend does that here, behind the interface.

        The default is the engine (rust) flow: when the request is representable
        by this engine (``rust_eligible``), build the ``PreparedRequest`` lazily,
        send it with :meth:`execute`, and parse the reply; otherwise run the
        supplied legacy operation. ``LegacyBackend`` overrides this to always run
        the legacy operation.

        The two callables plus ``legacy_operation`` keep this class free of any
        dependency on the helper layer (it never imports ``parse_backend_response``)
        and keep :class:`PreparedRequest` data-oriented -- the legacy call is a
        separate, typed argument here (see :class:`LegacyOperation`), never
        something attached to the request object:

        * ``build_prepared`` builds the ``PreparedRequest``; it is invoked only
          on the rust path, so a core-python client never does the extra
          partition-key / body work.
        * ``legacy_operation`` names the op and runs the legacy
          ``client_connection.<Op>Item`` call, returning the already-parsed result.
        * ``parse_response`` turns a rust ``BackendResponse`` into the final
          result (it binds the client connection and response hook).

        Falling back to the legacy path is usually the right answer: the request
        still succeeds and the customer sees no difference. For a few requests it
        is the wrong answer, because the fallback would change something the
        customer asked for. A customer who selected the Rust backend and passed a
        per-call socket timeout would get that timeout honored on one request and
        silently ignored on the next, with nothing to show which happened. For
        those, ``allow_legacy_fallback=False`` turns the silent switch into an
        error the customer can read and act on.

        :keyword build_prepared: Zero-arg builder for the rust ``PreparedRequest``.
        :keyword legacy_operation: Typed port to the legacy call; see
            :class:`LegacyOperation`.
        :keyword parse_response: Parser from ``BackendResponse`` to final result.
        :keyword rust_eligible: ``False`` when this specific request cannot be
            represented on the rust path (e.g. a filtered / guarded patch), which
            forces the legacy operation even on a rust-backed client.
        :keyword fallback_exceptions: Narrow, operation-specific compatibility
            failures that should retry through the supplied legacy operation.
        :keyword allow_legacy_fallback: When ``False``, an ineligible request
            fails explicitly instead of crossing from a Rust-selected client to
            the legacy transport.
        :keyword unsupported_message: Customer-facing message used when an
            ineligible request cannot fall back.
        :returns: The final result the public method returns to the caller.
        :rtype: Any
        """
        if not rust_eligible:
            if not allow_legacy_fallback:
                raise NotImplementedError(
                    unsupported_message
                    or "{} is not supported by the Rust backend for this request".format(
                        legacy_operation.op
                    )
                )
            return legacy_operation.invoke()
        try:
            prepared = build_prepared()
            response = self.execute(prepared)
            assert response is not None  # execute() only returns None for a None prepared request
            return parse_response(response)
        except fallback_exceptions:
            if not allow_legacy_fallback:
                raise
            record_rust_compatibility_fallback()
            return legacy_operation.invoke()

    def run_page_operation(  # pylint: disable=too-many-arguments
        self,
        *,
        build_prepared: Callable[[], PreparedQuery],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[QueryPage], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
    ) -> Any:
        """Run one backend-selected page without exposing fallback sentinels.

        An ineligible request or an explicit capability exception runs the
        supplied legacy operation. An empty page iterator is a backend contract
        violation and propagates as ``BackendProtocolError``; it never replays
        the request through legacy.

        Without this method each caller would repeat the same try/except and
        fallback bookkeeping, and a caller that got it slightly wrong could run
        the same feed twice -- once on Rust and again on legacy.
        """
        if not rust_eligible:
            return legacy_operation.invoke()
        page: Optional[QueryPage] = None
        try:
            pages = self.execute_pages(build_prepared())
            try:
                page = next(pages)
            except StopIteration:
                pass
            finally:
                # One page per call: the iterator is left suspended at its
                # ``yield`` and is not resumed. Closing it here finalizes it at a
                # deterministic point instead of leaving it for the garbage
                # collector, so a long-lived client paging a large feed does not
                # accumulate suspended generators between collections. Guarded
                # because ``execute_pages`` is documented to return an iterator,
                # which need not be a generator.
                close = getattr(pages, "close", None)
                if close is not None:
                    close()
        except fallback_exceptions:
            record_rust_compatibility_fallback()
            return legacy_operation.invoke()
        if page is None:
            raise BackendProtocolError(
                f"{type(self).__name__} returned no page for {legacy_operation.op!r}"
            )
        return parse_response(page)

    # --- execute_pages is implemented by RustBackend; execute_batch is
    # reserved for the not-yet-built batch operation ----------------------
    #
    # Concrete (not abstract) so today's backends stay valid without
    # implementing them. A backend adds query or batch support by overriding
    # the method; this class does not change.

    def execute_pages(self, prepared: PreparedQuery) -> Iterator[QueryPage]:
        """Return a paged query or read-feed result one ``QueryPage`` at a time.

        The default here raises; :class:`~azure.cosmos._backend.rust.RustBackend`
        overrides it (using ``QUERY_TO_BINDING_METHOD``) to dispatch
        ``query_items`` / ``read_all_items`` / ``list_databases``. A backend
        that does not implement this -- ``LegacyBackend`` never reaches it, since
        :meth:`run_page_operation` invokes the legacy call directly -- keeps
        this raising default.
        """
        raise NotImplementedError(
            "execute_pages is not implemented by this backend."
        )

    def execute_batch(self, prepared: PreparedBatch) -> BatchResponse:
        """Run a transactional batch and return one result per operation.

        Reserved: the batch operation is not implemented yet, so this raises.
        A backend that supports it overrides it (using
        ``BATCH_TO_BINDING_METHOD``).
        """
        raise NotImplementedError(
            "execute_batch is reserved for the transactional-batch operation "
            "and is not implemented yet."
        )

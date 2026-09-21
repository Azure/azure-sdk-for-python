# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Define how synchronous helpers call a backend and receive results.

Helpers that prepare Rust requests call execute or execute_pages directly.
Operations still supporting migration fallback use run_operation or
run_page_operation. These choose Rust or an allowed Python call before
execution. They do not retry execution, parsing, or callback failures through
the other implementation.

A single operation returns BackendResponse. A page fetch returns QueryPage,
including a continuation token when available.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Callable, Iterator, Optional

from .capabilities import OperationRouting
from ._fallback_metrics import record_rust_compatibility_fallback
from .contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedQuery,
    PreparedRequest,
    QueryPage,
)
from .errors import BindingProtocolError, PagePreflightError

if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class CosmosBackend(abc.ABC):
    """Base methods for synchronous Rust and legacy Python backends.

    RustBinding sends prepared requests. LegacyBackend instead runs a supplied
    function using the original Python arguments; it overrides run_operation
    and run_page_operation and does not send PreparedRequest objects.
    """

    #: Short identifier used in the startup INFO log line. Subclasses
    #: set this from ``constants.BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    def close(self) -> None:
        """Release resources owned by this backend.

        Backends with no resources can keep this empty default.
        """

    @abc.abstractmethod
    def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Send one prepared operation and return status, headers, and body.

        The caller parses BackendResponse, including successful empty bodies.
        No response object is an error. The Rust implementation chooses a
        binding function using prepared.op.

        ``deadline`` is an absolute time from time.monotonic(), a clock
        unaffected by wall-clock changes. Subtract the current reading before
        the binding call to pass the remaining seconds.
        """
        ...

    def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None
    ) -> ContainerMetadata:
        """Get the container ID and partition-key definition, or raise if unsupported."""
        raise NotImplementedError("This backend does not provide container metadata")

    def run_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedRequest],
        process_response: Callable[[BackendResponse], Any],
        legacy_call: Optional[Callable[[], Any]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Choose an allowed implementation before executing one operation."""
        if routing.uses_legacy():
            if legacy_call is None:
                raise BindingProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return legacy_call()
        prepared = build_request()
        if prepared.op != routing.op:
            raise BindingProtocolError(
                f"Prepared operation {prepared.op!r} does not match {routing.op!r}"
            )
        response = self.execute(prepared, deadline=deadline)
        return process_response(response)

    def run_page_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedQuery],
        process_response: Callable[[QueryPage], Any],
        legacy_call: Optional[Callable[[], Any]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Choose an allowed implementation before fetching and processing a page."""
        if routing.uses_legacy():
            if legacy_call is None:
                raise BindingProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return legacy_call()
        prepared = build_request()
        if prepared.op != routing.op:
            raise BindingProtocolError(
                f"Prepared operation {prepared.op!r} does not match {routing.op!r}"
            )
        try:
            self.validate_page_request(prepared)
        except PagePreflightError as error:
            if (
                type(error) is not PagePreflightError
                or not routing.policy.fallback_allowed
                or prepared.continuation is not None
            ):
                raise
            if legacy_call is None:
                raise BindingProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return legacy_call()
        pages = self.execute_pages(prepared, deadline=deadline)
        try:
            page = next(pages)
        except StopIteration as error:
            raise BindingProtocolError(
                f"{type(self).__name__} returned no page for {routing.op!r}"
            ) from error
        finally:
            close = getattr(pages, "close", None)
            if close is not None:
                close()
        return process_response(page)

    def execute_pages(
        self, prepared: PreparedQuery, *, deadline: Optional[float] = None
    ) -> Iterator[QueryPage]:
        """Fetch results as QueryPage objects, or raise if unsupported.

        RustBinding currently yields one page per call, with or without a Rust
        cursor that keeps progress between fetches. When deadline is supplied,
        it passes the remaining seconds to the selected binding function.
        LegacyBackend uses its supplied Python function instead.
        """
        raise NotImplementedError("execute_pages is not implemented by this backend.")

    def validate_page_request(self, prepared: PreparedQuery) -> None:
        """Check that a page fetch is supported without sending or creating a driver."""

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create a Rust object to keep page progress, without acquiring a driver."""
        raise NotImplementedError(
            "This backend does not provide native item-feed cursors"
        )

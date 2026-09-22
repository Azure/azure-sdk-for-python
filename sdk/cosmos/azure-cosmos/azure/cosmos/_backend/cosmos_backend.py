# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Define how the synchronous Python wrapper calls the Python/Rust binding.

Helpers that build prepared requests call execute or execute_pages directly.
Operations still supporting migration fallback use run_operation or
run_page_operation. These permit specific legacy-path calls before execution
while migration is unfinished. They do not offer another release execution
path or repeat execution, parsing, or callback failures through the legacy path.

A single operation returns BackendResponse. A page fetch returns BackendPage,
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
    PreparedPageRequest,
    PreparedRequest,
    BackendPage,
)
from .errors import BindingProtocolError, PagePreflightError

if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class CosmosBackend(abc.ABC):
    """Shared Python methods used while legacy migration code remains.

    RustBackend is part of the Python wrapper; it calls the compiled
    Python/Rust binding with prepared requests. LegacyBackend runs a supplied
    function using the original Python arguments; it overrides run_operation
    and run_page_operation and does not send PreparedRequest objects.
    """

    #: Short identifier used in the startup INFO log line. Subclasses
    #: set this from ``constants.BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    def close(self) -> None:
        """Release this Python wrapper object's resources.

        A caller with no resources can keep this empty default.
        """

    @abc.abstractmethod
    def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Send one prepared request and return a backend response.

        The caller parses BackendResponse, including successful empty bodies.
        No response object is an error. The Python wrapper chooses a
        Python/Rust binding function using prepared.op.

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
        """Execute through the Rust path or choose permitted legacy-path fallback."""
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
        build_request: Callable[[], PreparedPageRequest],
        process_response: Callable[[BackendPage], Any],
        legacy_call: Optional[Callable[[], Any]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Fetch one backend page through Rust or use permitted legacy-path fallback."""
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
        self, prepared: PreparedPageRequest, *, deadline: Optional[float] = None
    ) -> Iterator[BackendPage]:
        """Fetch results as BackendPage objects, or raise if unsupported.

        RustBackend yields one backend page per call. Retained paging also
        passes a feed cursor to the binding. A supplied deadline contributes
        its remaining seconds. LegacyBackend instead uses a legacy-path function.
        """
        raise NotImplementedError("execute_pages is not implemented by this backend.")

    def validate_page_request(self, prepared: PreparedPageRequest) -> None:
        """Perform page preflight without a driver acquisition or page fetch."""

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create a feed cursor without acquiring a driver handle or fetching a page."""
        raise NotImplementedError(
            "This backend does not provide native item-feed cursors"
        )

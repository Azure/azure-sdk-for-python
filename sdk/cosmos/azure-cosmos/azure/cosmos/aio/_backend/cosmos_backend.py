# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Define how the asynchronous Python wrapper executes prepared requests.

Migrated helpers call execute or execute_pages directly. Remaining migration
helpers use run_operation or run_page_operation, supplying a request builder,
function to process the response, OperationRouting, and optional legacy-path function.
OperationRouting selects an execution path, not a region or replica.

Prepared requests produce backend responses; prepared page requests produce
backend pages. The invocation's absolute deadline is supplied separately.
Python page iterators create feed cursors through create_item_feed_cursor;
that synchronous binding constructor does not acquire a driver handle.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Awaitable, Any, AsyncIterator, Callable, Optional

from azure.cosmos._backend.capabilities import OperationRouting
from azure.cosmos._backend.errors import (
    BindingProtocolError,
    PagePreflightError,
)

from azure.cosmos._backend.contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedPageRequest,
    PreparedRequest,
    BackendPage,
)
from azure.cosmos._backend._fallback_metrics import record_rust_compatibility_fallback

__all__ = ["AsyncCosmosBackend"]


if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class AsyncCosmosBackend(abc.ABC):
    """Shared Python interface for asynchronous request execution.

    AsyncRustBackend implements execute and execute_pages through the binding.
    AsyncLegacyBackend instead awaits supplied legacy-path functions through
    run_operation and run_page_operation; it does not consume prepared requests.

    Those two migration methods choose any permitted fallback before execution.
    They never repeat execution, response-processing, or callback failures
    through the legacy path. Retiring that path also removes its selection
    policy, not the requirement to validate unsupported request options.
    """

    #: Python backend identifier used in the startup INFO log. Subclasses set this from
    #: ``BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    async def close(self) -> None:
        """Release resources owned by this Python backend.

        Implementations with no owned resources can keep this empty default.
        """

    @abc.abstractmethod
    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Execute a prepared request and return a backend response.

        AsyncRustBackend selects a binding function using prepared.op, calls it,
        and awaits its result. The returned BackendResponse still needs body
        parsing by the caller, including for an empty successful body.

        deadline is an absolute reading of time.monotonic(), not a new duration.
        For example, a deadline of 105 with the clock now at 102 leaves three
        seconds for the binding call. AsyncLegacyBackend rejects this method.
        """
        ...

    async def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None
    ) -> ContainerMetadata:
        """Get the container id and partition-key definition, or raise if unsupported."""
        raise NotImplementedError("This backend does not provide container metadata")

    async def run_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedRequest],
        process_response: Callable[[BackendResponse], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Choose the permitted execution path, await its result, then process it.

        A supplied legacy_call is used only when migration policy permits it
        before execution. A response-processing error is raised, not used to
        choose the legacy path.
        """
        if routing.uses_legacy():
            if legacy_call is None:
                raise BindingProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return await legacy_call()
        prepared = build_request()
        if prepared.op != routing.op:
            raise BindingProtocolError(
                f"Prepared operation {prepared.op!r} does not match {routing.op!r}"
            )
        response = await self.execute(prepared, deadline=deadline)
        return process_response(response)

    async def run_page_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedPageRequest],
        process_response: Callable[[BackendPage], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Fetch one backend page through Rust or choose permitted legacy fallback.

        Page preflight precedes driver acquisition and fetching. Its specific
        PagePreflightError can allow fallback only when the operation's policy
        permits it and no continuation token was supplied. Execution errors do not.
        """
        if routing.uses_legacy():
            if legacy_call is None:
                raise BindingProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return await legacy_call()
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
            return await legacy_call()
        pages = self.execute_pages(prepared, deadline=deadline)
        try:
            page = await pages.__anext__()
        except StopAsyncIteration as error:
            raise BindingProtocolError(
                f"{type(self).__name__} returned no page for {routing.op!r}"
            ) from error
        finally:
            close = getattr(pages, "aclose", None)
            if close is not None:
                await close()
        return process_response(page)

    def execute_pages(
        self, prepared: PreparedPageRequest, *, deadline: Optional[float] = None
    ) -> AsyncIterator[BackendPage]:
        """Return the asynchronous iterator used to fetch a backend page.

        AsyncRustBackend yields one BackendPage per call. Advancing its async
        generator performs the fetch; constructing that generator does not.
        The operation name and presence of a feed cursor select stateless or
        retained paging. A supplied deadline contributes its remaining seconds.

        This base implementation raises. AsyncLegacyBackend uses its supplied
        legacy-path page function instead.
        """
        raise NotImplementedError("execute_pages is not implemented by this backend.")

    def validate_page_request(self, prepared: PreparedPageRequest) -> None:
        """Provide a page-preflight hook before driver acquisition or page fetching.

        This base method performs no check. AsyncRustBackend checks that the
        operation and cursor mode have the required async binding function.
        """

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create a feed cursor synchronously, without driver acquisition or page fetching."""
        raise NotImplementedError(
            "This backend does not provide native item-feed cursors"
        )

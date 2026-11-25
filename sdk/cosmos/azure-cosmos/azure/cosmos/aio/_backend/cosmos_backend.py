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
from azure.cosmos._backend.errors import BindingProtocolError

from azure.cosmos._backend.contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedPageRequest,
    PreparedRequest,
    BackendPage,
)

__all__ = ["AsyncCosmosBackend"]


if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class AsyncCosmosBackend(abc.ABC):
    """Shared Python interface for asynchronous request execution.

    AsyncBindingAdapter implements execute and execute_pages through the binding.
    AsyncLegacyBackend instead awaits supplied legacy-path functions through
    run_operation and run_page_operation; it does not consume prepared requests.

    Those two methods validate support before execution and never fall back to
    legacy Python. Only the separately selected legacy backend awaits legacy
    calls; unsupported requests and failures on Rust propagate to the caller.
    """

    #: Python backend identifier used for execution-path routing. Subclasses set this from
    #: ``BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    async def initialize(self) -> None:
        """Prepare account-level resources before the customer enters the client.

        Backends with no owned startup resources can keep this empty default.
        """

    async def close(self) -> None:
        """Release resources owned by this Python backend.

        Implementations with no owned resources can keep this empty default.
        """

    @abc.abstractmethod
    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Execute a prepared request and return a backend response.

        AsyncBindingAdapter selects a binding function using prepared.op, calls it,
        and awaits its result. The returned BackendResponse still needs body
        parsing by the caller, including for an empty successful body.

        deadline is an absolute reading of time.monotonic(), not a new duration.
        For example, a deadline of 105 with the clock now at 102 leaves three
        seconds for the binding call. AsyncLegacyBackend rejects this method.

        :param prepared: Operation inputs to send through the binding.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedRequest
        :keyword deadline: Absolute monotonic deadline, or None.
        :paramtype deadline: float or None
        :return: Binding response before public result processing.
        :rtype: ~azure.cosmos._backend.contracts.BackendResponse
        """
        ...

    async def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None, op: Optional[str] = None
    ) -> ContainerMetadata:
        """Get the container id and partition-key definition, or raise if unsupported.

        ``op`` names the operation that needs the lookup, such as ``"read_items"``.

        :param container_link: Container resource address.
        :type container_link: str
        :keyword deadline: Absolute monotonic deadline, or None.
        :paramtype deadline: float or None
        :keyword op: Operation requiring metadata, or None when not associated with an operation.
        :paramtype op: str or None
        :return: Container identity and partition-key definition; the base implementation raises.
        :rtype: ~azure.cosmos._backend.contracts.ContainerMetadata
        """
        raise NotImplementedError("This backend does not provide container metadata")

    async def run_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedRequest],
        process_response: Callable[[BackendResponse], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,  # pylint: disable=unused-argument
        deadline: Optional[float] = None,
    ) -> Any:
        """Validate support, await Rust execution, and process its response.

        :keyword routing: Operation capability to validate before building the request.
        :paramtype routing: ~azure.cosmos._backend.capabilities.OperationRouting
        :keyword build_request: Synchronous factory for the prepared operation.
        :paramtype build_request: typing.Callable[[], azure.cosmos._backend.contracts.PreparedRequest]
        :keyword process_response: Synchronous callback converting the binding response.
        :paramtype process_response: typing.Callable
        :keyword legacy_call: Legacy override hook retained for interface compatibility; unused on Rust.
        :paramtype legacy_call: typing.Callable or None
        :keyword deadline: Absolute monotonic deadline, or None.
        :paramtype deadline: float or None
        :return: Result of the response-processing callback.
        :rtype: typing.Any
        """
        routing.require_rust_support()
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
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,  # pylint: disable=unused-argument
        deadline: Optional[float] = None,
    ) -> Any:
        """Validate support and fetch one Rust page without legacy fallback.

        :keyword routing: Operation capability to validate before preparing the page.
        :paramtype routing: ~azure.cosmos._backend.capabilities.OperationRouting
        :keyword build_request: Synchronous factory for the prepared page request.
        :paramtype build_request: typing.Callable[[], azure.cosmos._backend.contracts.PreparedPageRequest]
        :keyword process_response: Synchronous callback converting the fetched page.
        :paramtype process_response: typing.Callable
        :keyword legacy_call: Legacy override hook retained for interface compatibility; unused on Rust.
        :paramtype legacy_call: typing.Callable or None
        :keyword deadline: Absolute monotonic deadline, or None.
        :paramtype deadline: float or None
        :return: Result of processing the first backend page.
        :rtype: typing.Any
        """
        routing.require_rust_support()
        prepared = build_request()
        if prepared.op != routing.op:
            raise BindingProtocolError(
                f"Prepared operation {prepared.op!r} does not match {routing.op!r}"
            )
        self.validate_page_request(prepared)
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

        AsyncBindingAdapter yields one BackendPage per call. Advancing its async
        generator performs the fetch; constructing that generator does not.
        The operation name and presence of a feed cursor select stateless or
        retained paging. A supplied deadline contributes its remaining seconds.

        This base implementation raises. AsyncLegacyBackend uses its supplied
        legacy-path page function instead.

        :param prepared: Inputs for one page fetch.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        :keyword deadline: Absolute monotonic deadline, or None.
        :paramtype deadline: float or None
        :return: Asynchronous iterator of backend pages; the base implementation raises.
        :rtype: typing.AsyncIterator[azure.cosmos._backend.contracts.BackendPage]
        """
        raise NotImplementedError("execute_pages is not implemented by this backend.")

    def validate_page_request(self, prepared: PreparedPageRequest) -> None:
        """Provide a page-preflight hook before driver acquisition or page fetching.

        This base method performs no check. AsyncBindingAdapter checks that the
        operation and cursor mode have the required async binding function.

        :param prepared: Page request to validate.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        """

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create a feed cursor synchronously, without driver acquisition or page fetching.

        :return: Empty native feed cursor; the base implementation raises.
        :rtype: ~azure.cosmos._rust._ItemFeedCursor
        """
        raise NotImplementedError(
            "This backend does not provide native item-feed cursors"
        )

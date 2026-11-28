# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Define how the synchronous Python wrapper calls the Python/Rust binding.

Helpers that build prepared requests call execute or execute_pages directly.
Other operations use run_operation or run_page_operation to validate support
before execution. Unsupported requests and all failures propagate without
legacy fallback. Only the separately selected legacy backend runs legacy calls.

A single operation returns BackendResponse. A page fetch returns BackendPage,
including a continuation token when available.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Callable, Iterator, Optional

from .capabilities import OperationRouting
from .contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedPageRequest,
    PreparedRequest,
    BackendPage,
)
from .errors import BindingProtocolError

if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


class CosmosBackend(abc.ABC):
    """Shared Python methods used while legacy migration code remains.

    BindingAdapter is part of the Python wrapper; it calls the compiled
    Python/Rust binding with prepared requests. LegacyBackend runs a supplied
    function using the original Python arguments; it overrides run_operation
    and run_page_operation and does not send PreparedRequest objects.
    """

    #: Short identifier used for execution-path routing. Subclasses
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

        :param prepared: Operation inputs to send through the binding.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedRequest
        :keyword deadline: Absolute monotonic deadline, or None for no caller deadline.
        :paramtype deadline: float or None
        :return: Binding response before public result processing.
        :rtype: ~azure.cosmos._backend.contracts.BackendResponse
        """
        ...

    def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None, op: Optional[str] = None
    ) -> ContainerMetadata:
        """Get the container ID and partition-key definition, or raise if unsupported.

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

    def run_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedRequest],
        process_response: Callable[[BackendResponse], Any],
        legacy_call: Optional[Callable[[], Any]] = None,  # pylint: disable=unused-argument
        deadline: Optional[float] = None,
    ) -> Any:
        """Validate support and execute through Rust without legacy fallback.

        :keyword routing: Operation capability to validate before building the request.
        :paramtype routing: ~azure.cosmos._backend.capabilities.OperationRouting
        :keyword build_request: Factory for the prepared operation.
        :paramtype build_request: typing.Callable[[], azure.cosmos._backend.contracts.PreparedRequest]
        :keyword process_response: Callback converting the binding response to the caller's result.
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
        response = self.execute(prepared, deadline=deadline)
        return process_response(response)

    def run_page_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedPageRequest],
        process_response: Callable[[BackendPage], Any],
        legacy_call: Optional[Callable[[], Any]] = None,  # pylint: disable=unused-argument
        deadline: Optional[float] = None,
    ) -> Any:
        """Validate support and fetch one Rust page without legacy fallback.

        :keyword routing: Operation capability to validate before preparing the page.
        :paramtype routing: ~azure.cosmos._backend.capabilities.OperationRouting
        :keyword build_request: Factory for the prepared page request.
        :paramtype build_request: typing.Callable[[], azure.cosmos._backend.contracts.PreparedPageRequest]
        :keyword process_response: Callback converting the fetched page to the caller's result.
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

        BindingAdapter yields one backend page per call. Retained paging also
        passes a feed cursor to the binding. A supplied deadline contributes
        its remaining seconds. LegacyBackend instead uses a legacy-path function.

        :param prepared: Inputs for one page fetch.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        :keyword deadline: Absolute monotonic deadline, or None.
        :paramtype deadline: float or None
        :return: Iterator of backend pages; the base implementation raises.
        :rtype: typing.Iterator[azure.cosmos._backend.contracts.BackendPage]
        """
        raise NotImplementedError("execute_pages is not implemented by this backend.")

    def validate_page_request(self, prepared: PreparedPageRequest) -> None:
        """Perform page preflight without a driver acquisition or page fetch.

        :param prepared: Page request to validate; this base hook performs no checks.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        """

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create a feed cursor without acquiring a driver handle or fetching a page.

        :return: Empty native feed cursor; the base implementation raises.
        :rtype: ~azure.cosmos._rust._ItemFeedCursor
        """
        raise NotImplementedError(
            "This backend does not provide native item-feed cursors"
        )

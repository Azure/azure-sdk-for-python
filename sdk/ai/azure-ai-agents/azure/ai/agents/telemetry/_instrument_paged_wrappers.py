# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Callable, AsyncIterator, Iterator, Optional, cast
from types import TracebackType

from opentelemetry.trace import Span, StatusCode

from azure.core.tracing._abstract_span import AbstractSpan
from azure.core.async_paging import AsyncItemPaged
from azure.core.paging import ItemPaged


class _SpanLogger:
    """The class, providing safe logging of events to the span"""

    def log_to_span_safe(
        self,
        val: Any,
        instrumentation_fun: Callable[[AbstractSpan, Any], None],
        span: AbstractSpan,
    ) -> None:
        """
        Log value to the span if span exists.

        :param val: The value to be logged.
        :type val: Any
        :param instrumentation_fun: The function to be used to log val.
        :type instrumentation_fun: Callable[[AbstractSpan, Any], None]
        :param span: The span to be used for logging. Span must be opened before calling this method.
        :type span: AbstractSpan
        """
        try:
            instrumentation_fun(span, val)

        except Exception as exc:
            # Set the span status to error
            if isinstance(span.span_instance, Span):  # pyright: ignore [reportPossiblyUnboundVariable]
                span.span_instance.set_status(
                    StatusCode.ERROR,  # pyright: ignore [reportPossiblyUnboundVariable]
                    description=str(exc),
                )
            module = getattr(exc, "__module__", "")
            module = module if module != "builtins" else ""
            error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
            span.add_attribute("error.type", error_type)
            raise


class _AsyncInstrumentedItemPaged(AsyncItemPaged, _SpanLogger):
    """The list class to mimic the AsyncPageable returned by a list."""

    def __init__(
        self,
        async_iter: AsyncItemPaged,
        start_span_function: Callable[[Optional[str], Optional[str], Optional[str]], AbstractSpan],
        item_instrumentation_function: Callable[[AbstractSpan, Any], None],
        server_address: Optional[str] = None,
        thread_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._iter = async_iter
        self._server_address = server_address
        self._thread_id = thread_id
        self._run_id = run_id
        self._start_span_function = start_span_function
        self._item_instrumentation_function = item_instrumentation_function
        self._gen: Optional[AsyncIterator[Any]] = None

    def __getattr__(self, name: str) -> Any:
        """
        Delegate every attribute we do not override to the wrapped object

        :param name: The name of the attribute to get.
        :type name: str

        :return: The value of the attribute.
        :rtype: Any
        """
        return getattr(self._iter, name)

    def __aiter__(self) -> AsyncIterator[Any]:
        async def _gen() -> AsyncIterator[Any]:
            async for val in self._iter:
                span: Optional[AbstractSpan] = self._start_span_function(
                    self._server_address, self._thread_id, self._run_id
                )
                if span is not None:
                    self.log_to_span_safe(val, self._item_instrumentation_function, span)
                    # We cast None to TracebackType, because traceback is
                    # not used in the downstream code.
                    span.__exit__(None, None, cast(TracebackType, None))
                    span = None
                yield val

        if self._gen is None:
            self._gen = _gen()
        return self._gen


class _InstrumentedItemPaged(ItemPaged, _SpanLogger):
    """The list class to mimic the Pageable returned by a list."""

    def __init__(
        self,
        iter_val: ItemPaged,
        start_span_function: Callable[[Optional[str], Optional[str], Optional[str]], AbstractSpan],
        item_instrumentation_function: Callable[[AbstractSpan, Any], None],
        server_address: Optional[str] = None,
        thread_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._iter = iter_val
        self._server_address = server_address
        self._thread_id = thread_id
        self._run_id = run_id
        self._start_span_function = start_span_function
        self._item_instrumentation_function = item_instrumentation_function
        self._gen: Optional[Iterator[Any]] = None

    def __getattr__(self, name: str) -> Any:
        """
        Delegate every attribute we do not override to the wrapped object

        :param name: The name of the attribute to get.
        :type name: str

        :return: The value of the attribute.
        :rtype: Any
        """
        return getattr(self._iter, name)

    def __iter__(self) -> Iterator[Any]:
        def _gen() -> Iterator[Any]:
            for val in self._iter:
                span: Optional[AbstractSpan] = self._start_span_function(
                    self._server_address, self._thread_id, self._run_id
                )
                if span is not None:
                    self.log_to_span_safe(val, self._item_instrumentation_function, span)
                    # We cast None to TracebackType, because traceback is
                    # not used in the downstream code.
                    span.__exit__(None, None, cast(TracebackType, None))
                    span = None
                yield val

        if self._gen is None:
            self._gen = _gen()
        return self._gen

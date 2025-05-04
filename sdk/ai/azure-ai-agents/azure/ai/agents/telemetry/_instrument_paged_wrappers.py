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
        instrumentation_fun: Callable[[AbstractSpan, Any], None],
        span: Optional[AbstractSpan],
    ) -> None:
        super().__init__()
        self._iter = async_iter
        self._inst_fun = instrumentation_fun
        self._span = span
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
            try:
                async for val in self._iter:
                    if self._span is not None:
                        self.log_to_span_safe(val, self._inst_fun, self._span)
                    yield val
            finally:
                if self._span is not None:
                    # We cast None to TracebackType, because traceback is
                    # not used in the downstream code.
                    self._span.__exit__(None, None, cast(TracebackType, None))

        if self._gen is None:
            if self._span is not None:
                self._span.__enter__()
            self._gen = _gen()
        return self._gen


class _InstrumentedItemPaged(ItemPaged, _SpanLogger):
    """The list class to mimic the Pageable returned by a list."""

    def __init__(
        self,
        iter_val: ItemPaged,
        instrumentation_fun: Callable[[AbstractSpan, Any], None],
        span: Optional[AbstractSpan],
    ) -> None:
        super().__init__()
        self._iter = iter_val
        self._inst_fun = instrumentation_fun
        self._span = span
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
            try:
                for val in self._iter:
                    if self._span is not None:
                        self.log_to_span_safe(val, self._inst_fun, self._span)
                    yield val
            finally:
                if self._span is not None:
                    # We cast None to TracebackType, because traceback is
                    # not used in the downstream code.
                    self._span.__exit__(None, None, cast(TracebackType, None))

        if self._gen is None:
            if self._span is not None:
                self._span.__enter__()
            self._gen = _gen()
        return self._gen

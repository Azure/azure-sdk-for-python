# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Callable, Iterator, Any
from azure.core.paging import ItemPaged
from azure.core.async_paging import AsyncItemPaged
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Optional,
 )


class _InstrumentedPaged(ItemPaged):
    """Proxy around ``ItemPaged`` that adds telemetry."""

    def __init__(
        self,
        paged: ItemPaged,
        span_cm,
        add_evt: Callable[[Any, Any], None],
        on_error: Callable[[Any, Exception], None],
    ) -> None:
        self._paged = paged
        self._span_cm = span_cm
        self._add_evt = add_evt
        self._on_error = on_error
        self._iter: Optional[Iterator[Any]] = None

    def __getattr__(self, name: str) -> Any:
        # Delegate every attribute we do not override to the wrapped object.
        return getattr(self._paged, name)

    def __iter__(self) -> Iterator[Any]:
        if self._iter is None:
            self._span_cm.__enter__()

            def _gen() -> Iterator[Any]:
                try:
                    for elem in self._paged:
                        self._add_evt(self._span_cm, elem)
                        yield elem
                except Exception as exc:
                    self._on_error(self._span_cm, exc)
                    raise
                finally:
                    self._span_cm.__exit__(None, None, None)

            self._iter = _gen()

        return self._iter


class _InstrumentedAsyncPaged(AsyncItemPaged):
    """Async counterpart that wraps ``AsyncItemPaged`` with telemetry."""

    def __init__(
        self,
        paged: AsyncItemPaged,
        span_cm,
        add_evt: Callable[[Any, Any], None],
        on_error: Callable[[Any, Exception], None],
    ) -> None:
        self._paged = paged
        self._span_cm = span_cm
        self._add_evt = add_evt
        self._on_error = on_error
        self._iter: Optional[AsyncIterator[Any]] = None   # created lazily

    def __getattr__(self, name: str) -> Any:
        return getattr(self._paged, name)

    def __aiter__(self) -> AsyncIterator[Any]:
        if self._iter is None:
            self._span_cm.__enter__()

            async def _agen() -> AsyncIterator[Any]:
                try:
                    async for elem in self._paged:
                        self._add_evt(self._span_cm, elem)
                        yield elem
                except Exception as exc:
                    self._on_error(self._span_cm, exc)
                    raise
                finally:
                    self._span_cm.__exit__(None, None, None)

            self._iter = _agen()

        return self._iter

    def by_page(
        self,
        continuation_token: Optional[str] = None,
    ) -> AsyncIterator[AsyncIterator[Any]]:

        if self._iter is None:
            self._span_cm.__enter__()

        async def _page_gen() -> AsyncIterator[AsyncIterator[Any]]:
            try:
                async for page in self._paged.by_page(
                    continuation_token=continuation_token
                ):
                    # create a generator that will trace each element of this page
                    async def _instrumented_page(
                        page_iter: AsyncIterator[Any] = page,
                    ) -> AsyncIterator[Any]:
                        async for elem in page_iter:
                            self._add_evt(self._span_cm, elem)
                            yield elem

                    # yield the generator object
                    yield _instrumented_page()
            except Exception as exc:
                self._on_error(self._span_cm, exc)
                raise
            finally:
                self._span_cm.__exit__(None, None, None)

        return _page_gen()

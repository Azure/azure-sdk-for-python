# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from typing import Any, AsyncIterator, Iterator, Iterable, List, Mapping, Optional

from azure.core.async_paging import AsyncItemPaged
from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict

from ._diagnostics import _HedgingDetectionAccessorsMixin, _pop_state_from_headers


class CosmosItemPaged(_HedgingDetectionAccessorsMixin, ItemPaged[dict[str, Any]]):
    """A custom ItemPaged class that provides access to response headers from query operations.

    This class wraps the standard ItemPaged and provides thread-safe access to response
    headers captured during pagination via a shared list populated by __QueryFeed.

    It also exposes three hedging-detection accessors inherited from
    :class:`~azure.cosmos._diagnostics._HedgingDetectionAccessorsMixin`:
    :meth:`is_hedging_started`, :meth:`get_requested_regions`, and
    :meth:`get_responded_regions`. For paged operations the accessors reflect
    the **most recently fetched** page; pre-fetch they return safe defaults
    (``False`` / empty tuples).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._response_headers_list: Optional[List[CaseInsensitiveDict]] = kwargs.pop('response_headers_list', None)
        super().__init__(*args, **kwargs)
        self._query_iterable: Optional[Any] = None
        # Hedging-detection state — refreshed as pages are fetched (see
        # ``get_response_headers`` below); None until the first page lands.
        self._hedging_state = None

    def by_page(self, continuation_token: Optional[str] = None) -> Iterator[Iterator[dict[str, Any]]]:
        """Get an iterator of pages of objects.

        :param str continuation_token: An opaque continuation token.
        :returns: An iterator of pages (themselves iterator of objects)
        :rtype: iterator[iterator[dict[str, Any]]]
        """
        # Call the parent's by_page to get the QueryIterable and store reference for header access
        self._query_iterable = super().by_page(continuation_token)
        return self._query_iterable

    def get_response_headers(self) -> List[CaseInsensitiveDict]:
        """Returns a list of response headers captured from each page of results.

        Each element in the list corresponds to the headers from one page fetch.
        Headers are captured as pages are fetched during iteration.

        :return: List of response headers from each page
        :rtype: List[~azure.core.utils.CaseInsensitiveDict]
        """
        if self._response_headers_list is not None:
            # Refresh latest hedging state from the most recent page (if attached),
            # then return defensive copies with the sentinel key stripped so
            # customers never see the private state on the headers dict.
            self._refresh_hedging_state_from_pages()
            return [self._copy_headers_stripped(h) for h in self._response_headers_list]
        return []

    def get_last_response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        if self._response_headers_list and len(self._response_headers_list) > 0:
            self._refresh_hedging_state_from_pages()
            return self._copy_headers_stripped(self._response_headers_list[-1])
        return CaseInsensitiveDict()

    def _refresh_hedging_state_from_pages(self) -> None:
        """Internal: scan pages from newest to oldest and update
        ``self._hedging_state`` with the most recent attached state, if any.
        Does not mutate the underlying headers dicts."""
        if not self._response_headers_list:
            return
        for h in reversed(self._response_headers_list):
            from ._diagnostics import HEDGING_STATE_HEADER_KEY
            state = h.get(HEDGING_STATE_HEADER_KEY) if h is not None else None
            if state is not None:
                self._hedging_state = state
                return

    @staticmethod
    def _copy_headers_stripped(headers: Optional[CaseInsensitiveDict]) -> CaseInsensitiveDict:
        """Return a copy of ``headers`` with the private hedging-state sentinel
        key removed so customer code never sees it."""
        if headers is None:
            return CaseInsensitiveDict()
        from ._diagnostics import HEDGING_STATE_HEADER_KEY
        copied = headers.copy()
        try:
            copied.pop(HEDGING_STATE_HEADER_KEY, None)
        except (TypeError, AttributeError):  # pragma: no cover
            pass
        return copied


class CosmosAsyncItemPaged(_HedgingDetectionAccessorsMixin, AsyncItemPaged[dict[str, Any]]):
    """A custom AsyncItemPaged class that provides access to response headers from async query operations.

    This class wraps the standard AsyncItemPaged and provides thread-safe access to response
    headers captured during pagination via a shared list populated by __QueryFeed.

    Also exposes the three hedging-detection accessors inherited from
    :class:`~azure.cosmos._diagnostics._HedgingDetectionAccessorsMixin`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._response_headers_list: Optional[List[CaseInsensitiveDict]] = kwargs.pop('response_headers_list', None)
        super().__init__(*args, **kwargs)
        self._query_iterable: Optional[Any] = None
        self._hedging_state = None

    def by_page(self, continuation_token: Optional[str] = None) -> AsyncIterator[AsyncIterator[dict[str, Any]]]:
        """Get an async iterator of pages of objects.

        :param str continuation_token: An opaque continuation token.
        :returns: An async iterator of pages (themselves async iterator of objects)
        :rtype: AsyncIterator[AsyncIterator[dict[str, Any]]]
        """
        # Call the parent's by_page to get the QueryIterable and store reference for header access
        self._query_iterable = super().by_page(continuation_token)
        return self._query_iterable

    def get_response_headers(self) -> List[CaseInsensitiveDict]:
        """Returns a list of response headers captured from each page of results.

        Each element in the list corresponds to the headers from one page fetch.
        Headers are captured as pages are fetched during iteration.

        :return: List of response headers from each page
        :rtype: List[~azure.core.utils.CaseInsensitiveDict]
        """
        if self._response_headers_list is not None:
            self._refresh_hedging_state_from_pages()
            return [self._copy_headers_stripped(h) for h in self._response_headers_list]
        return []

    def get_last_response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        if self._response_headers_list and len(self._response_headers_list) > 0:
            self._refresh_hedging_state_from_pages()
            return self._copy_headers_stripped(self._response_headers_list[-1])
        return CaseInsensitiveDict()

    def _refresh_hedging_state_from_pages(self) -> None:
        if not self._response_headers_list:
            return
        for h in reversed(self._response_headers_list):
            from ._diagnostics import HEDGING_STATE_HEADER_KEY
            state = h.get(HEDGING_STATE_HEADER_KEY) if h is not None else None
            if state is not None:
                self._hedging_state = state
                return

    @staticmethod
    def _copy_headers_stripped(headers: Optional[CaseInsensitiveDict]) -> CaseInsensitiveDict:
        if headers is None:
            return CaseInsensitiveDict()
        from ._diagnostics import HEDGING_STATE_HEADER_KEY
        copied = headers.copy()
        try:
            copied.pop(HEDGING_STATE_HEADER_KEY, None)
        except (TypeError, AttributeError):  # pragma: no cover
            pass
        return copied


class CosmosDict(_HedgingDetectionAccessorsMixin, dict[str, Any]):
    def __init__(self, original_dict: Optional[Mapping[str, Any]], /, *, response_headers: CaseInsensitiveDict) -> None:
        if original_dict is None:
            original_dict = {}
        super().__init__(original_dict)
        # Pull the hedging-detection state off the headers dict (if attached
        # by the orchestrator) before storing the headers, so customers never
        # see the private sentinel via ``get_response_headers()``.
        self._hedging_state = _pop_state_from_headers(response_headers)
        self._response_headers = response_headers

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers associated to this response

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers.copy()


class CosmosList(_HedgingDetectionAccessorsMixin, list[dict[str, Any]]):
    def __init__(self, original_list: Optional[Iterable[dict[str, Any]]], /, *,
                 response_headers: CaseInsensitiveDict) -> None:
        if original_list is None:
            original_list = []
        super().__init__(original_list)
        self._hedging_state = _pop_state_from_headers(response_headers)
        self._response_headers = response_headers

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers associated to this response

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers.copy()

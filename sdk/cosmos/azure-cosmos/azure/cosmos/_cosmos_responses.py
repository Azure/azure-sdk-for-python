# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from typing import Any, AsyncIterator, Iterator, Iterable, List, Mapping, Optional

from azure.core.async_paging import AsyncItemPaged
from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict


class CosmosItemPaged(ItemPaged[dict[str, Any]]):
    """A custom ItemPaged class that provides access to response headers from query operations.

    This class wraps the standard ItemPaged and provides thread-safe access to response
    headers captured during pagination via a shared list populated by __QueryFeed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._response_headers_list: Optional[List[CaseInsensitiveDict]] = kwargs.pop('response_headers_list', None)
        super().__init__(*args, **kwargs)
        self._query_iterable: Optional[Any] = None

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
            return [h.copy() for h in self._response_headers_list]
        return []

    def get_last_response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        if self._response_headers_list and len(self._response_headers_list) > 0:
            return self._response_headers_list[-1].copy()
        return CaseInsensitiveDict()


class CosmosAsyncItemPaged(AsyncItemPaged[dict[str, Any]]):
    """A custom AsyncItemPaged class that provides access to response headers from async query operations.

    This class wraps the standard AsyncItemPaged and provides thread-safe access to response
    headers captured during pagination via a shared list populated by __QueryFeed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._response_headers_list: Optional[List[CaseInsensitiveDict]] = kwargs.pop('response_headers_list', None)
        super().__init__(*args, **kwargs)
        self._query_iterable: Optional[Any] = None

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
            return [h.copy() for h in self._response_headers_list]
        return []

    def get_last_response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        if self._response_headers_list and len(self._response_headers_list) > 0:
            return self._response_headers_list[-1].copy()
        return CaseInsensitiveDict()


class CosmosDict(dict[str, Any]):
    def __init__(self, original_dict: Optional[Mapping[str, Any]], /, *, response_headers: CaseInsensitiveDict) -> None:
        if original_dict is None:
            original_dict = {}
        super().__init__(original_dict)
        self._response_headers = response_headers

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers associated to this response

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers.copy()


class CosmosList(list[dict[str, Any]]):
    def __init__(self, original_list: Optional[Iterable[dict[str, Any]]], /, *,
                 response_headers: CaseInsensitiveDict) -> None:
        if original_list is None:
            original_list = []
        super().__init__(original_list)
        self._response_headers = response_headers

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers associated to this response

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers.copy()

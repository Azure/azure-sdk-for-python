# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from typing import Any, AsyncIterator, Iterator, Iterable, List, Mapping, Optional

from azure.core.async_paging import AsyncItemPaged
from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict


class CosmosItemPaged(ItemPaged[dict[str, Any]]):
    """A custom ItemPaged class that provides access to response headers from query operations.

    This class wraps the standard ItemPaged and stores a reference to the underlying
    QueryIterable to expose response headers captured during pagination.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
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
        Headers are only available after iterating through the results.

        :return: List of response headers from each page
        :rtype: List[~azure.core.utils.CaseInsensitiveDict]
        """
        if self._query_iterable is None:
            return []
        if hasattr(self._query_iterable, 'get_response_headers'):
            return self._query_iterable.get_response_headers()
        return []

    def get_last_response_headers(self) -> Optional[CaseInsensitiveDict]:
        """Returns the response headers from the most recent page fetch.

        :return: Response headers from the last page, or None if no pages have been fetched
        :rtype: Optional[~azure.core.utils.CaseInsensitiveDict]
        """
        if self._query_iterable is None:
            return None
        if hasattr(self._query_iterable, 'get_last_response_headers'):
            return self._query_iterable.get_last_response_headers()
        return None


class CosmosAsyncItemPaged(AsyncItemPaged[dict[str, Any]]):
    """A custom AsyncItemPaged class that provides access to response headers from async query operations.

    This class wraps the standard AsyncItemPaged and stores a reference to the underlying
    QueryIterable to expose response headers captured during pagination.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
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
        Headers are only available after iterating through the results.

        :return: List of response headers from each page
        :rtype: List[~azure.core.utils.CaseInsensitiveDict]
        """
        if self._query_iterable is None:
            return []
        if hasattr(self._query_iterable, 'get_response_headers'):
            return self._query_iterable.get_response_headers()
        return []

    def get_last_response_headers(self) -> Optional[CaseInsensitiveDict]:
        """Returns the response headers from the most recent page fetch.

        :return: Response headers from the last page, or None if no pages have been fetched
        :rtype: Optional[~azure.core.utils.CaseInsensitiveDict]
        """
        if self._query_iterable is None:
            return None
        if hasattr(self._query_iterable, 'get_last_response_headers'):
            return self._query_iterable.get_last_response_headers()
        return None


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

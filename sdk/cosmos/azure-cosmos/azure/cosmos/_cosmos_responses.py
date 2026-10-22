# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from typing import Any, Iterable, Mapping, Optional

from azure.core.async_paging import AsyncItemPaged
from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict


class CosmosItemPaged(ItemPaged[dict[str, Any]]):
    """A custom ItemPaged class that provides access to response headers from query operations.

    This class wraps the standard ItemPaged and provides access to the most recent
    response headers captured during pagination via a shared dict populated by __QueryFeed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        popped = kwargs.pop('response_headers', None)
        self._response_headers: CaseInsensitiveDict = popped if popped is not None else CaseInsensitiveDict()
        super().__init__(*args, **kwargs)

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        return self._response_headers.copy()


class CosmosAsyncItemPaged(AsyncItemPaged[dict[str, Any]]):
    """A custom AsyncItemPaged class that provides access to response headers from async query operations.

    This class wraps the standard AsyncItemPaged and provides access to the most recent
    response headers captured during pagination via a shared dict populated by __QueryFeed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        popped = kwargs.pop('response_headers', None)
        self._response_headers: CaseInsensitiveDict = popped if popped is not None else CaseInsensitiveDict()
        super().__init__(*args, **kwargs)

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        return self._response_headers.copy()


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

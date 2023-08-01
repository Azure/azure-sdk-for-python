# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Type, Union
from ._generated.models import AutocompleteRequest, SearchRequest, SuggestRequest


class _QueryBase:

    _request_type: Union[Type[AutocompleteRequest], Type[SearchRequest], Type[SuggestRequest]] = None

    def __init__(self, **kwargs) -> None:
        self._request = self._request_type(**kwargs)  # pylint:disable=not-callable

    def __repr__(self) -> str:
        return "<{} [{}]>".format(self.__class__.__name__, self._request.search_text)[:1024]

    def filter(self, expression: str) -> None:
        """Add a `filter` expression for the search results.

        :param expression: An ODate expression of for the query filter.
        :type expression: str
        """
        self._request.filter = expression

    @property
    def request(self) -> Union[Type[AutocompleteRequest], Type[SearchRequest], Type[SuggestRequest]]:
        """The service request for this operation.

        :return: The service request for this operation.
        :rtype: AutocompleteRequest or SearchRequest or SuggestRequest
        """
        return self._request


class AutocompleteQuery(_QueryBase):
    """Represent an autocomplete query again an Azure Search index."""

    _request_type = AutocompleteRequest

    __doc__ = AutocompleteRequest.__doc__


class SearchQuery(_QueryBase):
    """Represent a rich search query again an Azure Search index."""

    _request_type = SearchRequest

    __doc__ = SearchRequest.__doc__

    def order_by(self, *fields: str) -> None:
        """Update the `orderby` property for the search results.

        :param fields: A list of fields for the query result to be ordered by.
        :type fields: str
        :raises: ValueError
        """
        if not fields:
            raise ValueError("At least one field must be provided")

        self._request.order_by = ",".join(fields)

    def select(self, *fields: str) -> None:
        """Update the `select` property for the search results.

        :param fields: A list of fields for the query result to return.
        :type fields: str
        :raises: ValueError
        """
        if not fields:
            raise ValueError("At least one field must be provided")
        selects = []
        for field in fields:
            if isinstance(field, list):
                selects.append(",".join(field))
            else:
                selects.append(field)
        self._request.select = ",".join(selects)


class SuggestQuery(_QueryBase):
    """Represent a search suggestion query again an Azure Search index."""

    _request_type = SuggestRequest

    __doc__ = SuggestRequest.__doc__

    def select(self, *fields: str) -> None:
        """Update the `select` property for the search results.

        :param fields: A list of fields for the query result to return.
        :type fields: str
        :raises: ValueError
        """
        if not fields:
            raise ValueError("At least one field must be provided")

        selects = []
        for field in fields:
            if isinstance(field, list):
                selects.append(",".join(field))
            else:
                selects.append(field)
        self._request.select = ",".join(selects)

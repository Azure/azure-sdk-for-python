# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from ._generated.models import AutocompleteRequest, SearchRequest, SuggestRequest

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, List, Type, Union

__all__ = ("AutocompleteQuery", "SearchQuery", "SuggestQuery")


class _QueryBase(object):

    _request_type = (
        None
    )  # type: Union[Type[AutocompleteRequest], Type[SearchRequest], Type[SuggestRequest]]

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._request = self._request_type(**kwargs)  # pylint:disable=not-callable

    def __repr__(self):
        # type: () -> str
        return "<{} [{}]>".format(self.__class__.__name__, self._request.search_text)[
            :1024
        ]

    def filter(self, expression):
        # type: (str) -> None
        """Add a `filter` expression for the search results.

        """
        self._request.filter = expression

    @property
    def request(self):
        """The service request for this operation.

        """
        return self._request


class AutocompleteQuery(_QueryBase):
    """Represent an autocomplete query again an Azure Search index.

    """

    _request_type = AutocompleteRequest


class SearchQuery(_QueryBase):
    """Represent a rich search query again an Azure Search index.

    """

    _request_type = SearchRequest

    def order_by(self, *fields):
        # type: (*str) -> None
        """Update the `orderby` property for the search results.

        """
        if not fields:
            raise ValueError("At least one field must be provided")

        self._request.order_by = ",".join(fields)

    def select(self, *fields):
        # type: (*str) -> None
        """Update the `select` property for the search results.

        """
        if not fields:
            raise ValueError("At least one field must be provided")

        self._request.select = ",".join(fields)


class SuggestQuery(_QueryBase):
    """Represent an autocomplete query again an Azure Search index.

    """

    _request_type = SuggestRequest

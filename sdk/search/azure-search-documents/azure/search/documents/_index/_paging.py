# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

import base64
import itertools
import json

from azure.core.paging import ItemPaged, PageIterator, ReturnType
from ._generated.models import SearchRequest, SearchDocumentsResult

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Union


def convert_search_result(result):
    ret = result.additional_properties
    ret["@search.score"] = result.score
    ret["@search.highlights"] = result.highlights
    return ret


def pack_continuation_token(response):
    api_version = "2019-05-06-Preview"
    if response.next_page_parameters is not None:
        token = {
            "apiVersion": api_version,
            "nextLink": response.next_link,
            "nextPageParameters": response.next_page_parameters.serialize(),
        }
        return base64.b64encode(json.dumps(token).encode("utf-8"))
    return None


def unpack_continuation_token(token):
    unpacked_token = json.loads(base64.b64decode(token))
    next_link = unpacked_token["nextLink"]
    next_page_parameters = unpacked_token["nextPageParameters"]
    next_page_request = SearchRequest.deserialize(next_page_parameters)
    return next_link, next_page_request


class SearchItemPaged(ItemPaged[ReturnType]):
    def __init__(self, *args, **kwargs):
        super(SearchItemPaged, self).__init__(*args, **kwargs)
        self._first_page_iterator_instance = None

    def __next__(self):
        # type: () -> ReturnType
        if self._page_iterator is None:
            first_iterator = self._first_iterator_instance()
            self._page_iterator = itertools.chain.from_iterable(first_iterator)
        return next(self._page_iterator)

    def _first_iterator_instance(self):
        if self._first_page_iterator_instance is None:
            self._first_page_iterator_instance = self.by_page()
        return self._first_page_iterator_instance

    def get_facets(self):
        # type: () -> Union[dict, None]
        """Return any facet results if faceting was requested.

        """
        page_iterator = self._first_iterator_instance()
        if page_iterator._current_page is None:
            response = page_iterator._get_next(page_iterator.continuation_token)
            _response = SearchDocumentsResult.deserialize(response)
            facets = _response.facets
            if facets is not None:
                _facets = {k: [x.as_dict() for x in v] for k, v in facets.items()}
                return _facets
            return None
        return page_iterator.response.facets


    def get_coverage(self):
        # type: () -> float
        """Return the covereage percentage, if `minimum_coverage` was
        specificied for the query.

        """
        page_iterator = self._first_iterator_instance()
        if page_iterator._current_page is None:
            response = page_iterator._get_next(page_iterator.continuation_token)
            _response = SearchDocumentsResult.deserialize(response)
            return _response.coverage
        return page_iterator.response.coverage

    def get_count(self):
        # type: () -> float
        """Return the count of results if `include_total_result_count` was
        set for the query.

        """
        page_iterator = self._first_iterator_instance()
        if page_iterator._current_page is None:
            response = page_iterator._get_next(page_iterator.continuation_token)
            _response = SearchDocumentsResult.deserialize(response)
            return _response.count
        return page_iterator.response.count


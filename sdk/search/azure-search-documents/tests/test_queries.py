# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from azure.search.documents._generated.models import (
    AutocompleteRequest,
    SearchRequest,
    SuggestRequest,
)

from azure.search.documents._queries import AutocompleteQuery, SuggestQuery, SearchQuery


class TestAutocompleteQuery(object):
    def test_init(self):
        query = AutocompleteQuery(search_text="text", suggester_name="sg")
        assert type(query.request) is AutocompleteRequest
        assert query.request.filter is None

    @mock.patch("azure.search.documents._queries.AutocompleteQuery._request_type")
    def test_kwargs_forwarded(self, mock_request):
        mock_request.return_value = None
        AutocompleteQuery(foo=10, bar=20)
        assert mock_request.called
        assert mock_request.call_args[0] == ()
        assert mock_request.call_args[1] == {"foo": 10, "bar": 20}

    def test_repr(self):
        query = AutocompleteQuery(search_text="foo bar", suggester_name="sg")
        assert repr(query) == "<AutocompleteQuery [foo bar]>"

        query = AutocompleteQuery(search_text="aaaaabbbbb" * 200, suggester_name="sg")
        assert len(repr(query)) == 1024

    def test_filter(self):
        query = AutocompleteQuery(search_text="text", suggester_name="sg")
        assert query.request.filter is None
        query.filter("expr0")
        assert query.request.filter == "expr0"

        query = AutocompleteQuery(
            search_text="text", suggester_name="sg", filter="expr1"
        )
        assert query.request.filter == "expr1"
        query.filter("expr2")
        assert query.request.filter == "expr2"


class TestSearchQuery(object):
    def test_init(self):
        query = SearchQuery()
        assert type(query.request) is SearchRequest
        assert query.request.filter is None
        assert query.request.order_by is None
        assert query.request.select is None

    @mock.patch("azure.search.documents._queries.SearchQuery._request_type")
    def test_kwargs_forwarded(self, mock_request):
        mock_request.return_value = None
        SearchQuery(foo=10, bar=20)
        assert mock_request.called
        assert mock_request.call_args[0] == ()
        assert mock_request.call_args[1] == {"foo": 10, "bar": 20}

    def test_repr(self):
        query = SearchQuery()
        assert repr(query) == "<SearchQuery [None]>"

        query = SearchQuery(search_text="foo bar", suggester_name="sg")
        assert repr(query) == "<SearchQuery [foo bar]>"

        query = SearchQuery(search_text="aaaaabbbbb" * 200)
        assert len(repr(query)) == 1024

    def test_filter(self):
        query = SearchQuery()
        assert query.request.filter is None
        query.filter("expr0")
        assert query.request.filter == "expr0"

        query = SearchQuery(filter="expr0")
        assert query.request.filter == "expr0"
        query.filter("expr1")
        assert query.request.filter == "expr1"

    def test_order_by(self):
        query = SearchQuery()
        assert query.request.order_by is None
        query.order_by("f0")
        assert query.request.order_by == "f0"
        query.order_by("f1,f2")
        assert query.request.order_by == "f1,f2"
        query.order_by("f3", "f4")
        assert query.request.order_by == "f3,f4"

        query = SearchQuery(order_by="f0")
        assert query.request.order_by == "f0"
        query.order_by("f1,f2")
        assert query.request.order_by == "f1,f2"
        query.order_by("f3", "f4")
        assert query.request.order_by == "f3,f4"

        with pytest.raises(ValueError) as e:
            query.order_by()
            assert str(e) == "At least one field must be provided"

    def test_select(self):
        query = SearchQuery()
        assert query.request.select is None
        query.select("f0")
        assert query.request.select == "f0"
        query.select("f1,f2")
        assert query.request.select == "f1,f2"
        query.select("f3", "f4")
        assert query.request.select == "f3,f4"

        query = SearchQuery(select="f0")
        assert query.request.select == "f0"
        query.select("f1,f2")
        assert query.request.select == "f1,f2"
        query.select("f3", "f4")
        assert query.request.select == "f3,f4"

        with pytest.raises(ValueError) as e:
            query.select()
            assert str(e) == "At least one field must be provided"


class TestSuggestQuery(object):
    def test_init(self):
        query = SuggestQuery(search_text="text", suggester_name="sg")
        assert type(query.request) is SuggestRequest
        assert query.request.filter is None

    @mock.patch("azure.search.documents._queries.SuggestQuery._request_type")
    def test_kwargs_forwarded(self, mock_request):
        mock_request.return_value = None
        SuggestQuery(foo=10, bar=20)
        assert mock_request.called
        assert mock_request.call_args[0] == ()
        assert mock_request.call_args[1] == {"foo": 10, "bar": 20}

    def test_repr(self):
        query = SuggestQuery(search_text="foo bar", suggester_name="sg")
        assert repr(query) == "<SuggestQuery [foo bar]>"

        query = SuggestQuery(search_text="aaaaabbbbb" * 200, suggester_name="sg")
        assert len(repr(query)) == 1024

    def test_filter(self):
        query = SuggestQuery(search_text="text", suggester_name="sg")
        assert query.request.filter is None
        query.filter("expr0")
        assert query.request.filter == "expr0"

        query = SuggestQuery(search_text="text", suggester_name="sg", filter="expr1")
        assert query.request.filter == "expr1"
        query.filter("expr2")
        assert query.request.filter == "expr2"

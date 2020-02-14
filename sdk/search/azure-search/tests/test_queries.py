# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.search.index._generated.models import AutocompleteRequest, SearchRequest, SuggestRequest

from azure.search import AutocompleteQuery, SearchQuery, SuggestQuery

class TestAutocompleteQuery(object):

    def test_init(self):
        query = AutocompleteQuery()
        assert type(query.request) is AutocompleteRequest
        assert query.request.filter is None

    def test_repr(self):
        query = AutocompleteQuery()
        assert repr(query) == "<AutocompleteQuery [None]>"

        query = AutocompleteQuery(search_text="foo bar")
        assert repr(query) == "<AutocompleteQuery [foo bar]>"

    def test_filter(self):
        query = AutocompleteQuery()
        assert query.request.filter is None
        query.filter("expr0")
        assert query.request.filter == "expr0"

        query = AutocompleteQuery(filter="expr1")
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

    def test_repr(self):
        query = SearchQuery()
        assert repr(query) == "<SearchQuery [None]>"

        query = SearchQuery(search_text="foo bar")
        assert repr(query) == "<SearchQuery [foo bar]>"

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

class TestSuggestQuery(object):

    def test_init(self):
        query = SuggestQuery()
        assert type(query.request) is SuggestRequest
        assert query.request.filter is None

    def test_repr(self):
        query = SuggestQuery()
        assert repr(query) == "<SuggestQuery [None]>"

        query = SuggestQuery(search_text="foo bar")
        assert repr(query) == "<SuggestQuery [foo bar]>"

    def test_filter(self):
        query = SuggestQuery()
        assert query.request.filter is None
        query.filter("expr0")
        assert query.request.filter == "expr0"

        query = SuggestQuery(filter="expr1")
        assert query.request.filter == "expr1"
        query.filter("expr2")
        assert query.request.filter == "expr2"

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.search.documents.indexes.models import (
    ComplexField,
    SearchableField,
    SimpleField,
    SearchFieldDataType,
)


def test_edm_contents():
    assert SearchFieldDataType.STRING == "Edm.String"
    assert SearchFieldDataType.INT32 == "Edm.Int32"
    assert SearchFieldDataType.INT64 == "Edm.Int64"
    assert SearchFieldDataType.DOUBLE == "Edm.Double"
    assert SearchFieldDataType.BOOLEAN == "Edm.Boolean"
    assert SearchFieldDataType.DATE_TIME_OFFSET == "Edm.DateTimeOffset"
    assert SearchFieldDataType.GEOGRAPHY_POINT == "Edm.GeographyPoint"
    assert SearchFieldDataType.COMPLEX == "Edm.ComplexType"
    assert SearchFieldDataType.Collection("foo") == "Collection(foo)"


class TestComplexField:
    def test_single(self):
        fld = ComplexField(name="foo", fields=[])
        assert fld.name == "foo"
        assert fld.type == SearchFieldDataType.COMPLEX

        assert fld.sortable is None
        assert fld.facetable is None
        assert fld.searchable is None
        assert fld.filterable is None
        assert fld.analyzer_name is None
        assert fld.search_analyzer_name is None
        assert fld.index_analyzer_name is None
        assert fld.synonym_map_names is None

    def test_collection(self):
        fld = ComplexField(name="foo", fields=[], collection=True)
        assert fld.name == "foo"
        assert fld.type == SearchFieldDataType.Collection(SearchFieldDataType.COMPLEX)

        assert fld.sortable is None
        assert fld.facetable is None
        assert fld.searchable is None
        assert fld.filterable is None
        assert fld.analyzer_name is None
        assert fld.search_analyzer_name is None
        assert fld.index_analyzer_name is None
        assert fld.synonym_map_names is None


class TestSimplexField:
    def test_defaults(self):
        fld = SimpleField(name="foo", type=SearchFieldDataType.DOUBLE)
        assert fld.name == "foo"
        assert fld.type == SearchFieldDataType.DOUBLE
        assert fld.retrievable == True
        assert fld.sortable == False
        assert fld.facetable == False
        assert fld.searchable == False
        assert fld.filterable == False

        assert fld.analyzer_name is None
        assert fld.search_analyzer_name is None
        assert fld.index_analyzer_name is None
        assert fld.synonym_map_names is None


class TestSearchableField:
    def test_defaults(self):
        fld = SearchableField(name="foo", collection=True)
        assert fld.name == "foo"
        assert fld.type == SearchFieldDataType.Collection(SearchFieldDataType.STRING)
        assert fld.retrievable == True
        assert fld.sortable == False
        assert fld.facetable == False
        assert fld.searchable == True
        assert fld.filterable == False

        assert fld.analyzer_name is None
        assert fld.search_analyzer_name is None
        assert fld.index_analyzer_name is None
        assert fld.synonym_map_names is None

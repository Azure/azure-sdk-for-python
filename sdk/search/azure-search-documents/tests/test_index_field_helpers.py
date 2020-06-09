# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.search.documents.indexes.models import ComplexField, SearchableField, SimpleField, SearchFieldDataType

def test_edm_contents():
    assert SearchFieldDataType.String == "Edm.String"
    assert SearchFieldDataType.Int32 == "Edm.Int32"
    assert SearchFieldDataType.Int64 == "Edm.Int64"
    assert SearchFieldDataType.Double == "Edm.Double"
    assert SearchFieldDataType.Boolean == "Edm.Boolean"
    assert SearchFieldDataType.DateTimeOffset == "Edm.DateTimeOffset"
    assert SearchFieldDataType.GeographyPoint == "Edm.GeographyPoint"
    assert SearchFieldDataType.ComplexType == "Edm.ComplexType"
    assert SearchFieldDataType.Collection("foo") == "Collection(foo)"

class TestComplexField(object):
    def test_single(self):
        fld = ComplexField(name="foo", fields=[])
        assert fld.name == "foo"
        assert fld.type == SearchFieldDataType.ComplexType

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
        assert fld.type == SearchFieldDataType.Collection(SearchFieldDataType.ComplexType)

        assert fld.sortable is None
        assert fld.facetable is None
        assert fld.searchable is None
        assert fld.filterable is None
        assert fld.analyzer_name is None
        assert fld.search_analyzer_name is None
        assert fld.index_analyzer_name is None
        assert fld.synonym_map_names is None

class TestSimplexField(object):
    def test_defaults(self):
        fld = SimpleField(name="foo", type=SearchFieldDataType.Double)
        assert fld.name == "foo"
        assert fld.type == SearchFieldDataType.Double
        assert fld.hidden == False
        assert fld.sortable == False
        assert fld.facetable == False
        assert fld.searchable == False
        assert fld.filterable == False

        assert fld.analyzer_name is None
        assert fld.search_analyzer_name is None
        assert fld.index_analyzer_name is None
        assert fld.synonym_map_names is None

class TestSearchableField(object):
    def test_defaults(self):
        fld = SearchableField(name="foo", collection=True)
        assert fld.name == "foo"
        assert fld.type == SearchFieldDataType.Collection(SearchFieldDataType.String)
        assert fld.hidden == False
        assert fld.sortable == False
        assert fld.facetable == False
        assert fld.searchable == True
        assert fld.filterable == False

        assert fld.analyzer_name is None
        assert fld.search_analyzer_name is None
        assert fld.index_analyzer_name is None
        assert fld.synonym_map_names is None

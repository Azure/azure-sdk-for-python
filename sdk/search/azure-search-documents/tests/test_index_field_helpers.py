# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.search.documents import ComplexField, SearchableField, SimpleField, edm

def test_edm_contents():
    assert edm.String == "Edm.String"
    assert edm.Int32 == "Edm.Int32"
    assert edm.Int64 == "Edm.Int64"
    assert edm.Double == "Edm.Double"
    assert edm.Boolean == "Edm.Boolean"
    assert edm.DateTimeOffset == "Edm.DateTimeOffset"
    assert edm.GeographyPoint == "Edm.GeographyPoint"
    assert edm.ComplexType == "Edm.ComplexType"
    assert edm.Collection("foo") == "Collection(foo)"

class TestComplexField(object):
    def test_single(self):
        fld = ComplexField(name="foo", fields=[])
        assert fld.name == "foo"
        assert fld.type == edm.ComplexType

        assert fld.sortable is None
        assert fld.facetable is None
        assert fld.searchable is None
        assert fld.filterable is None
        assert fld.analyzer is None
        assert fld.search_analyzer is None
        assert fld.index_analyzer is None
        assert fld.synonym_maps is None

    def test_collection(self):
        fld = ComplexField(name="foo", fields=[], collection=True)
        assert fld.name == "foo"
        assert fld.type == edm.Collection(edm.ComplexType)

        assert fld.sortable is None
        assert fld.facetable is None
        assert fld.searchable is None
        assert fld.filterable is None
        assert fld.analyzer is None
        assert fld.search_analyzer is None
        assert fld.index_analyzer is None
        assert fld.synonym_maps is None

class TestSimplexField(object):
    def test_defaults(self):
        fld = SimpleField(name="foo", type=edm.Double)
        assert fld.name == "foo"
        assert fld.type == edm.Double
        assert fld.retrievable == True
        assert fld.sortable == False
        assert fld.facetable == False
        assert fld.searchable == False
        assert fld.filterable == False

        assert fld.analyzer is None
        assert fld.search_analyzer is None
        assert fld.index_analyzer is None
        assert fld.synonym_maps is None

class TestSearchableField(object):
    def test_defaults(self):
        fld = SearchableField(name="foo", type=edm.Collection(edm.String))
        assert fld.name == "foo"
        assert fld.type == edm.Collection(edm.String)
        assert fld.retrievable == True
        assert fld.sortable == False
        assert fld.facetable == False
        assert fld.searchable == True
        assert fld.filterable == False

        assert fld.analyzer is None
        assert fld.search_analyzer is None
        assert fld.index_analyzer is None
        assert fld.synonym_maps is None

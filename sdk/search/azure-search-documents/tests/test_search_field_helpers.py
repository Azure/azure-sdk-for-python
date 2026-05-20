# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``SearchField`` helper models."""

from __future__ import annotations

import pytest

from azure.search.documents.indexes.models import (
    ComplexField,
    LexicalAnalyzerName,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
)

CANONICAL_FIELD_TYPES = [
    ("STRING", "Edm.String"),
    ("INT32", "Edm.Int32"),
    ("INT64", "Edm.Int64"),
    ("SINGLE", "Edm.Single"),
    ("DOUBLE", "Edm.Double"),
    ("BOOLEAN", "Edm.Boolean"),
    ("DATE_TIME_OFFSET", "Edm.DateTimeOffset"),
    ("GEOGRAPHY_POINT", "Edm.GeographyPoint"),
    ("COMPLEX", "Edm.ComplexType"),
]


def _assert_default_analyzer_settings(field):
    assert field.analyzer_name is None
    assert field.search_analyzer_name is None
    assert field.index_analyzer_name is None
    assert field.synonym_map_names is None


class TestSearchFieldDataType:
    @pytest.mark.parametrize(("name", "value"), CANONICAL_FIELD_TYPES)
    def test_canonical_members_keep_edm_values(self, name, value):
        assert getattr(SearchFieldDataType, name) == value

    @pytest.mark.parametrize(
        ("alias", "canonical"),
        [
            ("String", "STRING"),
            ("Int32", "INT32"),
            ("Int64", "INT64"),
            ("Single", "SINGLE"),
            ("Double", "DOUBLE"),
            ("Boolean", "BOOLEAN"),
            ("DateTimeOffset", "DATE_TIME_OFFSET"),
            ("GeographyPoint", "GEOGRAPHY_POINT"),
            ("ComplexType", "COMPLEX"),
        ],
    )
    def test_legacy_aliases_point_to_generated_enum_members(self, alias, canonical):
        assert getattr(SearchFieldDataType, alias) is getattr(SearchFieldDataType, canonical)

    def test_collection_accepts_raw_strings_and_enum_members(self):
        assert SearchFieldDataType.Collection("Custom.Type") == "Collection(Custom.Type)"
        assert SearchFieldDataType.Collection(SearchFieldDataType.STRING) == "Collection(Edm.String)"
        assert SearchFieldDataType.Collection(SearchFieldDataType.COMPLEX) == "Collection(Edm.ComplexType)"


class TestSearchField:
    def test_hidden_constructor_kwarg_sets_inverse_retrievable_value(self):
        field = SearchField(name="Rating", type=SearchFieldDataType.DOUBLE, hidden=True)

        assert field.hidden is True
        assert field.retrievable is False

    def test_hidden_property_setter_keeps_retrievable_in_sync(self):
        field = SearchField(name="Rating", type=SearchFieldDataType.DOUBLE)

        field.hidden = True
        assert field.retrievable is False

        field.hidden = False
        assert field.retrievable is True

        field.hidden = None
        assert field.hidden is None
        assert field.retrievable is None


class TestSimpleField:
    def test_defaults_create_non_searchable_retrievable_field(self):
        field = SimpleField(name="Rating", type=SearchFieldDataType.DOUBLE)

        assert field.name == "Rating"
        assert field.type == SearchFieldDataType.DOUBLE
        assert field.key is False
        assert field.searchable is False
        assert field.filterable is False
        assert field.sortable is False
        assert field.facetable is False
        assert field.hidden is False
        assert field.retrievable is True
        _assert_default_analyzer_settings(field)

    def test_forwards_boolean_flags_and_accepts_raw_type_string(self):
        field = SimpleField(
            name="HotelId",
            type="Edm.String",
            key=True,
            hidden=True,
            filterable=True,
            sortable=True,
            facetable=True,
        )

        assert field.name == "HotelId"
        assert field.type == SearchFieldDataType.STRING
        assert field.key is True
        assert field.searchable is False
        assert field.filterable is True
        assert field.sortable is True
        assert field.facetable is True
        assert field.hidden is True
        assert field.retrievable is False
        _assert_default_analyzer_settings(field)


class TestSearchableField:
    def test_defaults_create_searchable_string_field(self):
        field = SearchableField(name="Description")

        assert field.name == "Description"
        assert field.type == SearchFieldDataType.STRING
        assert field.key is False
        assert field.searchable is True
        assert field.filterable is False
        assert field.sortable is False
        assert field.facetable is False
        assert field.hidden is False
        assert field.retrievable is True
        _assert_default_analyzer_settings(field)

    def test_collection_field_uses_collection_string_type(self):
        field = SearchableField(name="Tags", collection=True)

        assert field.type == SearchFieldDataType.Collection(SearchFieldDataType.STRING)
        _assert_default_analyzer_settings(field)

    def test_forwards_search_options(self):
        field = SearchableField(
            name="Description",
            searchable=False,
            hidden=True,
            filterable=True,
            sortable=True,
            facetable=True,
            analyzer_name=LexicalAnalyzerName.EN_LUCENE,
            synonym_map_names=["synonyms"],
        )

        assert field.searchable is False
        assert field.hidden is True
        assert field.retrievable is False
        assert field.filterable is True
        assert field.sortable is True
        assert field.facetable is True
        assert field.analyzer_name == LexicalAnalyzerName.EN_LUCENE
        assert field.synonym_map_names == ["synonyms"]


class TestComplexField:
    def test_single_complex_field_defaults_to_complex_type(self):
        subfield = SimpleField(name="City", type=SearchFieldDataType.STRING)
        field = ComplexField(name="Address", fields=[subfield])

        assert field.name == "Address"
        assert field.type == SearchFieldDataType.COMPLEX
        assert field.fields == [subfield]
        assert field.searchable is None
        assert field.filterable is None
        assert field.sortable is None
        assert field.facetable is None
        _assert_default_analyzer_settings(field)

    def test_collection_complex_field_uses_collection_complex_type(self):
        subfield = SearchableField(name="Amenities", collection=True)
        field = ComplexField(name="Rooms", fields=[subfield], collection=True)

        assert field.name == "Rooms"
        assert field.type == SearchFieldDataType.Collection(SearchFieldDataType.COMPLEX)
        assert field.fields == [subfield]
        assert field.searchable is None
        assert field.filterable is None
        assert field.sortable is None
        assert field.facetable is None
        _assert_default_analyzer_settings(field)

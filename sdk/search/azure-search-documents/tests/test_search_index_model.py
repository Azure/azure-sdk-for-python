# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``SearchIndex`` helper serialization."""

from __future__ import annotations

from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
)

INDEX_NAME = "hotels"


def create_hotel_fields():
    return [
        SimpleField(name="HotelId", type=SearchFieldDataType.STRING, key=True),
        SimpleField(name="BaseRate", type=SearchFieldDataType.DOUBLE, filterable=True, sortable=True),
        SearchableField(name="HotelName", analyzer_name="en.lucene"),
        SearchableField(name="Tags", collection=True, facetable=True),
        ComplexField(
            name="Address",
            fields=[
                SimpleField(name="City", type=SearchFieldDataType.STRING, filterable=True),
                SimpleField(name="State", type=SearchFieldDataType.STRING, filterable=True),
            ],
        ),
    ]


def create_search_index(index_name=INDEX_NAME):
    return SearchIndex(
        name=index_name,
        fields=create_hotel_fields(),
        cors_options=CorsOptions(allowed_origins=["https://portal.contoso.example"], max_age_in_seconds=60),
    )


class TestSearchIndexSerialization:
    def test_search_index_serializes_helper_fields_to_wire_names(self):
        index = create_search_index()

        serialized = index.as_dict()

        assert serialized["name"] == INDEX_NAME
        assert [(field["name"], field["type"]) for field in serialized["fields"]] == [
            ("HotelId", "Edm.String"),
            ("BaseRate", "Edm.Double"),
            ("HotelName", "Edm.String"),
            ("Tags", "Collection(Edm.String)"),
            ("Address", "Edm.ComplexType"),
        ]
        assert serialized["fields"][0]["key"] is True
        assert serialized["fields"][1]["filterable"] is True
        assert serialized["fields"][1]["sortable"] is True
        assert serialized["fields"][2]["searchable"] is True
        assert serialized["fields"][2]["analyzer"] == "en.lucene"
        assert serialized["fields"][3]["facetable"] is True
        assert serialized["fields"][4]["fields"] == [
            {
                "name": "City",
                "type": "Edm.String",
                "key": False,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
            {
                "name": "State",
                "type": "Edm.String",
                "key": False,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": False,
                "retrievable": True,
            },
        ]
        assert serialized["corsOptions"] == {
            "allowedOrigins": ["https://portal.contoso.example"],
            "maxAgeInSeconds": 60,
        }

    def test_search_index_round_trips_helper_field_wire_shape(self):
        serialized = create_search_index().as_dict()

        index = SearchIndex(serialized)

        assert index.name == INDEX_NAME
        assert index.fields[0].name == "HotelId"
        assert index.fields[0].key is True
        assert index.fields[1].name == "BaseRate"
        assert index.fields[1].sortable is True
        assert index.fields[2].analyzer_name == "en.lucene"
        assert index.fields[3].type == "Collection(Edm.String)"
        assert index.fields[4].fields[1].name == "State"
        assert index.cors_options.allowed_origins == ["https://portal.contoso.example"]
        assert index.cors_options.max_age_in_seconds == 60

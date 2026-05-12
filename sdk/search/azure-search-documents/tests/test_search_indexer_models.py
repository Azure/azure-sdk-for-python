# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for search indexer model helper serialization."""

from __future__ import annotations

from azure.search.documents.indexes.models import (
    CognitiveServicesAccountKey,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataSourceType,
    SearchIndexerSkillset,
    SplitSkill,
    TextSplitMode,
)

DATA_SOURCE_NAME = "hotel-data-source"
CONNECTION_STRING = (
    "ResourceId=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/search/"
    "providers/Microsoft.Storage/storageAccounts/hotels"
)
CONTAINER_NAME = "hotel-documents"
REPLACEMENT_CONNECTION_STRING = "<unchanged>"
SKILLSET_NAME = "hotel-skillset"
SPLIT_SKILL_NAME = "split-hotel-description"
COGNITIVE_SERVICES_KEY = "00000000000000000000000000000000"
COGNITIVE_SERVICES_DESCRIPTION = "Skillset cognitive services account"


def create_data_source(connection_string=CONNECTION_STRING):
    return SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type=SearchIndexerDataSourceType.AZURE_BLOB,
        connection_string=connection_string,
        container=SearchIndexerDataContainer(name=CONTAINER_NAME),
    )


def create_skillset():
    return SearchIndexerSkillset(
        name=SKILLSET_NAME,
        skills=[
            SplitSkill(
                name=SPLIT_SKILL_NAME,
                inputs=[InputFieldMappingEntry(name="text", source="/document/Description")],
                outputs=[OutputFieldMappingEntry(name="textItems", target_name="pages")],
                context="/document",
                text_split_mode=TextSplitMode.PAGES,
                maximum_page_length=5000,
            )
        ],
        cognitive_services_account=CognitiveServicesAccountKey(
            key=COGNITIVE_SERVICES_KEY,
            description=COGNITIVE_SERVICES_DESCRIPTION,
        ),
    )


class TestSearchIndexerDataSourceConnectionSerialization:
    def test_connection_string_overload_serializes_as_nested_credentials(self):
        data_source = create_data_source()

        serialized = data_source.as_dict()

        assert serialized == {
            "name": DATA_SOURCE_NAME,
            "type": "azureblob",
            "credentials": {"connectionString": CONNECTION_STRING},
            "container": {"name": CONTAINER_NAME},
        }

    def test_connection_string_property_round_trips_through_credentials(self):
        data_source = create_data_source()

        data_source.connection_string = REPLACEMENT_CONNECTION_STRING

        assert data_source.connection_string == REPLACEMENT_CONNECTION_STRING
        assert data_source.credentials.connection_string == REPLACEMENT_CONNECTION_STRING
        assert data_source.as_dict()["credentials"] == {"connectionString": REPLACEMENT_CONNECTION_STRING}


class TestSearchIndexerSkillsetSerialization:
    def test_skillset_round_trips_split_skill_and_cognitive_services(self):
        skillset = create_skillset()

        serialized = skillset.as_dict()
        round_trip = SearchIndexerSkillset(serialized)

        assert serialized["name"] == SKILLSET_NAME
        assert serialized["cognitiveServices"] == {
            "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
            "description": COGNITIVE_SERVICES_DESCRIPTION,
            "key": COGNITIVE_SERVICES_KEY,
        }
        assert serialized["skills"][0]["@odata.type"] == "#Microsoft.Skills.Text.SplitSkill"
        assert serialized["skills"][0]["name"] == SPLIT_SKILL_NAME
        assert serialized["skills"][0]["context"] == "/document"
        assert serialized["skills"][0]["inputs"] == [{"name": "text", "source": "/document/Description"}]
        assert serialized["skills"][0]["outputs"] == [{"name": "textItems", "targetName": "pages"}]
        assert serialized["skills"][0]["textSplitMode"] == "pages"
        assert serialized["skills"][0]["maximumPageLength"] == 5000
        assert round_trip.name == SKILLSET_NAME
        assert round_trip.cognitive_services_account.key == COGNITIVE_SERVICES_KEY
        assert round_trip.cognitive_services_account.description == COGNITIVE_SERVICES_DESCRIPTION
        assert round_trip.skills[0].name == SPLIT_SKILL_NAME
        assert round_trip.skills[0].context == "/document"
        assert round_trip.skills[0].inputs[0].source == "/document/Description"
        assert round_trip.skills[0].outputs[0].target_name == "pages"
        assert round_trip.skills[0].text_split_mode == "pages"
        assert round_trip.skills[0].maximum_page_length == 5000

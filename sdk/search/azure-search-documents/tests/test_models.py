# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import timedelta

from azure.search.documents.indexes.models import (
    ContentUnderstandingSkill,
    ContentUnderstandingSkillChunkingProperties,
    ContentUnderstandingSkillExtractionOptions,
    FreshnessScoringFunction,
    FreshnessScoringParameters,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    ScoringFunctionAggregation,
    ScoringProfile,
    SearchField,
    SearchIndex,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchResourceEncryptionKey,
    SearchIndexerSkillset,
    ShaperSkill,
    SearchIndexer,
)


def test_encryption_key_serialization():
    from azure.search.documents.indexes._generated.models import (
        SearchResourceEncryptionKey as SearchResourceEncryptionKeyGen,
    )

    container = SearchIndexerDataContainer(name="container_name")
    encryption_key = SearchResourceEncryptionKey(
        key_name="key",
        key_version="key_version",
        vault_uri="vault_uri",
    )
    data_source_connection = SearchIndexerDataSourceConnection(
        name="datasource-name",
        type="azureblob",
        connection_string="connection_string",
        container=container,
        encryption_key=encryption_key,
    )
    packed_data_source = data_source_connection._to_generated()
    assert isinstance(packed_data_source.encryption_key, SearchResourceEncryptionKeyGen)

    search_indexer = SearchIndexer(
        name="indexer-name",
        data_source_name="datasource-name",
        target_index_name="target-index-name",
        encryption_key=encryption_key,
    )
    packed_search_indexer = search_indexer._to_generated()
    assert isinstance(packed_search_indexer.encryption_key, SearchResourceEncryptionKeyGen)


def test_search_index_purview_enabled_round_trip():
    fields = [SearchField(name="id", type="Edm.String", key=True)]
    index = SearchIndex(
        name="idx",
        fields=fields,
        purview_enabled=True,
        permission_filter_option="enabled",
    )

    generated = index._to_generated()
    assert generated.purview_enabled is True

    round_tripped = SearchIndex._from_generated(generated)
    assert round_tripped is not None
    assert round_tripped.purview_enabled is True


def test_content_understanding_skill_round_trip():
    skill = ContentUnderstandingSkill(
        name="content-skill",
        description="extract structured signals",
        context="/document",
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/content"),
        ],
        outputs=[
            OutputFieldMappingEntry(name="structured", target_name="structuredContent"),
        ],
        extraction_options=[
            ContentUnderstandingSkillExtractionOptions.IMAGES,
            ContentUnderstandingSkillExtractionOptions.LOCATION_METADATA,
        ],
        chunking_properties=ContentUnderstandingSkillChunkingProperties(
            maximum_length=600,
            overlap_length=50,
        ),
    )
    skillset = SearchIndexerSkillset(name="cu-skillset", skills=[skill])

    generated_skillset = skillset._to_generated()
    assert isinstance(generated_skillset.skills[0], ContentUnderstandingSkill)
    generated_skill = generated_skillset.skills[0]
    assert generated_skill.chunking_properties.maximum_length == 600
    assert generated_skill.chunking_properties.overlap_length == 50
    assert generated_skill.extraction_options == ["images", "locationMetadata"]

    generated_skill.description = "updated description"
    generated_skill.chunking_properties.maximum_length = 700

    round_tripped = SearchIndexerSkillset._from_generated(generated_skillset)
    assert round_tripped is not None
    round_trip_skill = round_tripped.skills[0]
    assert isinstance(round_trip_skill, ContentUnderstandingSkill)
    assert round_trip_skill.description == "updated description"
    assert round_trip_skill.chunking_properties.maximum_length == 700
    assert round_trip_skill.extraction_options == ["images", "locationMetadata"]


def test_content_understanding_skill_payload_shape():
    skill = ContentUnderstandingSkill(
        name="content-skill",
        inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
        outputs=[OutputFieldMappingEntry(name="structured")],
        chunking_properties=ContentUnderstandingSkillChunkingProperties(),
    )
    payload = SearchIndexerSkillset(name="cu-skillset", skills=[skill]).serialize()

    skill_payload = payload["skills"][0]
    assert skill_payload["@odata.type"] == "#Microsoft.Skills.Util.ContentUnderstandingSkill"
    assert skill_payload["chunkingProperties"]["unit"] == "characters"


def test_search_index_scoring_profile_product_round_trip():
    fields = [
        SearchField(name="id", type="Edm.String", key=True),
        SearchField(name="lastUpdated", type="Edm.DateTimeOffset", filterable=True),
    ]
    scoring_profile = ScoringProfile(
        name="product-score",
        function_aggregation=ScoringFunctionAggregation.PRODUCT,
        functions=[
            FreshnessScoringFunction(
                field_name="lastUpdated",
                boost=2.5,
                parameters=FreshnessScoringParameters(boosting_duration=timedelta(days=7)),
            )
        ],
    )
    index = SearchIndex(name="scoring-index", fields=fields, scoring_profiles=[scoring_profile])

    generated = index._to_generated()
    assert generated.scoring_profiles[0].function_aggregation == "product"

    generated.scoring_profiles[0].function_aggregation = "sum"

    round_tripped = SearchIndex._from_generated(generated)
    assert round_tripped is not None
    assert round_tripped.scoring_profiles[0].function_aggregation == "sum"


def test_search_index_scoring_profile_product_payload():
    fields = [
        SearchField(name="id", type="Edm.String", key=True),
        SearchField(name="lastUpdated", type="Edm.DateTimeOffset", filterable=True),
    ]
    scoring_profile = ScoringProfile(
        name="product-score",
        function_aggregation=ScoringFunctionAggregation.PRODUCT,
        functions=[
            FreshnessScoringFunction(
                field_name="lastUpdated",
                boost=2.0,
                parameters=FreshnessScoringParameters(boosting_duration=timedelta(days=3)),
            )
        ],
    )
    payload = SearchIndex(
        name="scoring-index",
        fields=fields,
        scoring_profiles=[scoring_profile],
    ).serialize()

    scoring_payload = payload["scoringProfiles"][0]
    assert scoring_payload["functionAggregation"] == "product"

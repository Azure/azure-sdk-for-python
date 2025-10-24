# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchIndexerSkillset,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ComplexField,
    ScoringProfile,
    CorsOptions,
    CognitiveServicesAccountKey,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SplitSkill,
    TextSplitMode,
)


def test_serialize_search_index():
    new_index_name = "hotels"
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String, collection=True),
        SearchableField(name="hotelName", type=SearchFieldDataType.String),
        ComplexField(
            name="address",
            fields=[
                SimpleField(name="streetAddress", type=SearchFieldDataType.String),
                SimpleField(name="city", type=SearchFieldDataType.String),
                SimpleField(name="state", type=SearchFieldDataType.String),
            ],
            collection=True,
        ),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profile = ScoringProfile(name="MyProfile")
    scoring_profiles = []
    scoring_profiles.append(scoring_profile)
    index = SearchIndex(
        name=new_index_name, fields=fields, scoring_profiles=scoring_profiles, cors_options=cors_options
    )
    search_index_serialized = index.serialize()
    search_index = SearchIndex.deserialize(search_index_serialized)
    assert search_index


def test_serialize_search_indexer_skillset():
    COGNITIVE_KEY = ...
    COGNITIVE_DESCRIPTION = ...

    cognitive_services_account = CognitiveServicesAccountKey(key=COGNITIVE_KEY, description=COGNITIVE_DESCRIPTION)

    inputs = [InputFieldMappingEntry(name="text", source="/document/content")]

    outputs = [OutputFieldMappingEntry(name="textItems", target_name="pages")]

    split_skill = SplitSkill(
        name="SplitSkill",
        inputs=inputs,
        outputs=outputs,
        context="/document",
        text_split_mode=TextSplitMode.PAGES,
        maximum_page_length=5000,
    )

    skills = [split_skill]
    skillset = SearchIndexerSkillset(
        name="Skillset", skills=skills, cognitive_services_account=cognitive_services_account
    )

    serialized_skillset = skillset.serialize()
    skillset = SearchIndexerSkillset.deserialize(serialized_skillset)
    assert skillset


def test_serialize_search_index_dict():
    new_index_name = "hotels"
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String, collection=True),
        SearchableField(name="hotelName", type=SearchFieldDataType.String),
        ComplexField(
            name="address",
            fields=[
                SimpleField(name="streetAddress", type=SearchFieldDataType.String),
                SimpleField(name="city", type=SearchFieldDataType.String),
                SimpleField(name="state", type=SearchFieldDataType.String),
            ],
            collection=True,
        ),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profile = ScoringProfile(name="MyProfile")
    scoring_profiles = []
    scoring_profiles.append(scoring_profile)
    index = SearchIndex(
        name=new_index_name, fields=fields, scoring_profiles=scoring_profiles, cors_options=cors_options
    )
    search_index_serialized_dict = index.as_dict()
    search_index = SearchIndex.from_dict(search_index_serialized_dict)
    assert search_index

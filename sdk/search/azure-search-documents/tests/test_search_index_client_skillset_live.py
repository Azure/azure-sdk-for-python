# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath

import pytest

from devtools_testutils import AzureMgmtTestCase
from azure_devtools.scenario_tests import ReplayableTest
from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    EntityLinkingSkill,
    EntityRecognitionSkill,
    EntityRecognitionSkillVersion,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SentimentSkill,
    SentimentSkillVersion
)
from azure.search.documents.indexes import SearchIndexerClient

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "hotel_schema.json")).read()
try:
    BATCH = json.load(open(join(CWD, "hotel_small.json")))
except UnicodeDecodeError:
    BATCH = json.load(open(join(CWD, "hotel_small.json"), encoding='utf-8'))
TIME_TO_SLEEP = 5

class SearchSkillsetClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        name = "test-ss"

        s1 = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                    outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS1")],
                                    description="Skill Version 1",
                                    include_typeless_entities=True)

        s2 = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                    outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS2")],
                                    skill_version=EntityRecognitionSkillVersion.LATEST,
                                    description="Skill Version 3",
                                    model_version="3")
        s3 = SentimentSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                            outputs=[OutputFieldMappingEntry(name="score", target_name="scoreS3")],
                            skill_version=SentimentSkillVersion.V1,
                            description="Sentiment V1")

        s4 = SentimentSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                            outputs=[OutputFieldMappingEntry(name="confidenceScores", target_name="scoreS4")],
                            skill_version=SentimentSkillVersion.V3,
                            description="Sentiment V3",
                            include_opinion_mining=True)

        s5 = EntityLinkingSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                outputs=[OutputFieldMappingEntry(name="entities", target_name="entitiesS5")],
                                minimum_precision=0.5)

        skillset = SearchIndexerSkillset(name=name, skills=list([s1, s2, s3, s4, s5]), description="desc")

        dict_skills = [skill.as_dict() for skill in skillset.skills]
        skillset.skills = dict_skills

        result = client.create_skillset(skillset)

        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 5
        assert isinstance(result.skills[0], EntityRecognitionSkill)
        assert result.skills[0].skill_version == EntityRecognitionSkillVersion.V1
        assert isinstance(result.skills[1], EntityRecognitionSkill)
        assert result.skills[1].skill_version == EntityRecognitionSkillVersion.V3
        assert isinstance(result.skills[2], SentimentSkill)
        assert result.skills[2].skill_version == SentimentSkillVersion.V1
        assert isinstance(result.skills[3], SentimentSkill)
        assert result.skills[3].skill_version == SentimentSkillVersion.V3
        assert isinstance(result.skills[4], EntityLinkingSkill)
        assert result.skills[4].minimum_precision == 0.5

        assert len(client.get_skillsets()) == 1


    def test_create_skillset_validation(self, **kwargs):
        with pytest.raises(ValueError) as err:
            client = SearchIndexerClient("fake_endpoint", AzureKeyCredential("fake_key"))
            name = "test-ss"

            s1 = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                        outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS1")],
                                        description="Skill Version 1",
                                        model_version="1",
                                        include_typeless_entities=True)

            s2 = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                        outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS2")],
                                        skill_version=EntityRecognitionSkillVersion.LATEST,
                                        description="Skill Version 3",
                                        model_version="3",
                                        include_typeless_entities=True)
            s3 = SentimentSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                outputs=[OutputFieldMappingEntry(name="score", target_name="scoreS3")],
                                skill_version=SentimentSkillVersion.V1,
                                description="Sentiment V1",
                                include_opinion_mining=True)
            skillset = SearchIndexerSkillset(name=name, skills=list([s1, s2, s3]), description="desc")
            client.create_skillset(skillset)
        assert 'include_typeless_entities' in str(err.value)
        assert 'model_version' in str(err.value)
        assert 'include_opinion_mining' in str(err.value)


    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc")

        result = client.create_skillset(skillset)
        assert len(client.get_skillsets()) == 1

        client.delete_skillset("test-ss")
        assert len(client.get_skillsets()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_skillset_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc")

        result = client.create_skillset(skillset)
        etag = result.e_tag

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="updated")
        updated = client.create_or_update_skillset(skillset)
        updated.e_tag = etag

        with pytest.raises(HttpResponseError):
            client.delete_skillset(updated, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc")
        client.create_skillset(skillset)
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_skillsets(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss-1', skills=list([s]), description="desc1")
        client.create_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name='test-ss-2', skills=list([s]), description="desc2")
        client.create_skillset(skillset2)
        result = client.get_skillsets()
        assert isinstance(result, list)
        assert all(isinstance(x, SearchIndexerSkillset) for x in result)
        assert set(x.name for x in result) == {"test-ss-1", "test-ss-2"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc1")
        client.create_or_update_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc2")
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset_inplace(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc1")
        ss = client.create_or_update_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name='test-ss', skills=[s], description="desc2", skillset=ss)
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc1")
        ss = client.create_or_update_skillset(skillset1)
        etag = ss.e_tag
        skillset2 = SearchIndexerSkillset(name='test-ss', skills=[s], description="desc2", skillset=ss)
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == 1

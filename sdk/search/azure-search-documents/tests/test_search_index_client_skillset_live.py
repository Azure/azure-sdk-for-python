# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, get_credential
from search_service_preparer import SearchEnvVarPreparer, search_decorator
from azure.search.documents.indexes.models import (
    EntityLinkingSkill,
    EntityRecognitionSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SentimentSkill,
)
from azure.search.documents.indexes import SearchIndexerClient


class TestSearchSkillset(AzureRecordedTestCase):
    @pytest.mark.skip("The skills are deprecated")
    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_skillset_crud(self, endpoint):
        client = SearchIndexerClient(endpoint, get_credential(), retry_backoff_factor=60)
        self._test_create_skillset_validation()
        self._test_create_skillset(client)
        self._test_get_skillset(client)
        self._test_get_skillsets(client)
        self._test_create_or_update_skillset(client)
        self._test_create_or_update_skillset_if_unchanged(client)
        self._test_create_or_update_skillset_inplace(client)
        self._test_delete_skillset_if_unchanged(client)
        self._test_delete_skillset(client)

    def _test_create_skillset_validation(self):
        name = "test-ss-validation"
        with pytest.raises(ValueError) as err:
            client = SearchIndexerClient("fake_endpoint", AzureKeyCredential("fake_key"))

            s1 = EntityRecognitionSkill(
                inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS1")],
                description="Skill Version 1",
                model_version="1",
                include_typeless_entities=True,
            )

            s2 = EntityRecognitionSkill(
                inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS2")],
                description="Skill Version 3",
                model_version="3",
                include_typeless_entities=True,
            )
            skillset = SearchIndexerSkillset(name=name, skills=list([s1, s2]), description="desc")
            client.create_skillset(skillset)
        assert "include_typeless_entities" in str(err.value)
        assert "model_version" in str(err.value)
        assert "include_opinion_mining" in str(err.value)

    def _test_create_skillset(self, client):
        name = "test-ss-create"
        s1 = EntityRecognitionSkill(
            name="skill1",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS1")],
            description="Skill Version 1",
            include_typeless_entities=True,
        )

        s2 = EntityRecognitionSkill(
            name="skill2",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS2")],
            description="Skill Version 3",
            model_version="3",
        )
        s4 = SentimentSkill(
            name="skill4",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="confidenceScores", target_name="scoreS4")],
            description="Sentiment V3",
            include_opinion_mining=True,
        )

        s5 = EntityLinkingSkill(
            name="skill5",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="entities", target_name="entitiesS5")],
            minimum_precision=0.5,
        )

        skillset = SearchIndexerSkillset(name=name, skills=list([s1, s2, s4, s5]), description="desc")

        dict_skills = [skill.as_dict() for skill in skillset.skills]
        skillset.skills = dict_skills

        result = client.create_skillset(skillset)

        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 5
        assert isinstance(result.skills[0], EntityRecognitionSkill)
        assert isinstance(result.skills[1], EntityRecognitionSkill)
        assert isinstance(result.skills[2], SentimentSkill)
        assert isinstance(result.skills[3], EntityLinkingSkill)
        assert result.skills[3].minimum_precision == 0.5

        assert len(client.get_skillsets()) == 1
        client.reset_skills(result, [x.name for x in result.skills])

    def _test_get_skillset(self, client):
        name = "test-ss-get"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )
        skillset = SearchIndexerSkillset(name=name, skills=list([s]), description="desc")
        client.create_skillset(skillset)
        result = client.get_skillset(name)
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

    def _test_get_skillsets(self, client):
        name1 = "test-ss-list-1"
        name2 = "test-ss-list-2"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name1, skills=list([s]), description="desc1")
        client.create_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name=name2, skills=list([s]), description="desc2")
        client.create_skillset(skillset2)
        result = client.get_skillsets()
        assert isinstance(result, list)
        assert all(isinstance(x, SearchIndexerSkillset) for x in result)
        assert set(x.name for x in result).intersection([name1, name2]) == set([name1, name2])

    def _test_create_or_update_skillset(self, client):
        name = "test-ss-create-or-update"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc1")
        client.create_or_update_skillset(skillset1)
        expected_count = len(client.get_skillsets())
        skillset2 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc2")
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == expected_count

        result = client.get_skillset(name)
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
        assert result.description == "desc2"

    def _test_create_or_update_skillset_inplace(self, client):
        name = "test-ss-create-or-update-inplace"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc1")
        ss = client.create_or_update_skillset(skillset1)
        expected_count = len(client.get_skillsets())
        skillset2 = SearchIndexerSkillset(name=name, skills=[s], description="desc2", skillset=ss)
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == expected_count

        result = client.get_skillset(name)
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
        assert result.description == "desc2"

    def _test_create_or_update_skillset_if_unchanged(self, client):
        name = "test-ss-create-or-update-unchanged"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc1")
        ss = client.create_or_update_skillset(skillset1)

        ss.e_tag = "changed_etag"

        with pytest.raises(HttpResponseError):
            client.create_or_update_skillset(ss, match_condition=MatchConditions.IfNotModified)

    def _test_delete_skillset_if_unchanged(self, client):
        name = "test-ss-deleted-unchanged"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset = SearchIndexerSkillset(name=name, skills=list([s]), description="desc")

        result = client.create_skillset(skillset)
        etag = result.e_tag

        skillset = SearchIndexerSkillset(name=name, skills=list([s]), description="updated")
        updated = client.create_or_update_skillset(skillset)
        updated.e_tag = etag

        with pytest.raises(HttpResponseError):
            client.delete_skillset(updated, match_condition=MatchConditions.IfNotModified)

    def _test_delete_skillset(self, client):
        for skillset in client.get_skillset_names():
            client.delete_skillset(skillset)

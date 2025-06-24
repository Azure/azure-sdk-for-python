# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase
from search_service_preparer import SearchEnvVarPreparer, search_decorator
from azure.search.documents.indexes.models import (
    EntityLinkingSkill,
    EntityRecognitionSkill,
    EntityRecognitionSkillVersion,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SentimentSkill,
    SentimentSkillVersion,
)
from azure.search.documents.indexes.aio import SearchIndexerClient


class TestSearchClientSkillsets(AzureRecordedTestCase):
    @pytest.mark.skip("The skills are deprecated")
    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_skillset_crud(self, api_key, endpoint):
        client = SearchIndexerClient(endpoint, api_key, retry_backoff_factor=60)
        async with client:
            await self._test_create_skillset(client)
            await self._test_get_skillset(client)
            await self._test_get_skillsets(client)
            await self._test_create_or_update_skillset(client)
            await self._test_create_or_update_skillset_if_unchanged(client)
            await self._test_create_or_update_skillset_inplace(client)
            await self._test_delete_skillset_if_unchanged(client)
            await self._test_delete_skillset(client)

    async def _test_create_skillset(self, client):
        name = "test-ss-create"
        s1 = EntityRecognitionSkill(
            name="skill1",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS1")],
            description="Skill Version 1",
            model_version="1",
            include_typeless_entities=True,
        )

        s2 = EntityRecognitionSkill(
            name="skill2",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizationsS2")],
            skill_version=EntityRecognitionSkillVersion.LATEST,
            description="Skill Version 3",
            model_version="3",
            include_typeless_entities=True,
        )
        s3 = SentimentSkill(
            name="skill3",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="score", target_name="scoreS3")],
            skill_version=SentimentSkillVersion.V1,
            description="Sentiment V1",
            include_opinion_mining=True,
        )

        s4 = SentimentSkill(
            name="skill4",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="confidenceScores", target_name="scoreS4")],
            skill_version=SentimentSkillVersion.V3,
            description="Sentiment V3",
            include_opinion_mining=True,
        )

        s5 = EntityLinkingSkill(
            name="skill5",
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="entities", target_name="entitiesS5")],
            minimum_precision=0.5,
        )

        skillset = SearchIndexerSkillset(name=name, skills=list([s1, s2, s3, s4, s5]), description="desc")
        result = await client.create_skillset(skillset)

        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
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

        assert len(await client.get_skillsets()) == 1
        await client.reset_skills(result, [x.name for x in result.skills])

    async def _test_get_skillset(self, client):
        name = "test-ss-get"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )
        skillset = SearchIndexerSkillset(name=name, skills=list([s]), description="desc")
        await client.create_skillset(skillset)
        result = await client.get_skillset(name)
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

    async def _test_get_skillsets(self, client):
        name1 = "test-ss-list-1"
        name2 = "test-ss-list-2"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name1, skills=list([s]), description="desc1")
        await client.create_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name=name2, skills=list([s]), description="desc2")
        await client.create_skillset(skillset2)
        result = await client.get_skillsets()
        assert isinstance(result, list)
        assert all(isinstance(x, SearchIndexerSkillset) for x in result)
        assert set(x.name for x in result).intersection([name1, name2]) == set([name1, name2])

    async def _test_create_or_update_skillset(self, client):
        name = "test-ss-create-or-update"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc1")
        await client.create_or_update_skillset(skillset1)
        expected_count = len(await client.get_skillsets())
        skillset2 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc2")
        await client.create_or_update_skillset(skillset2)
        assert len(await client.get_skillsets()) == expected_count

        result = await client.get_skillset(name)
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
        assert result.description == "desc2"

    async def _test_create_or_update_skillset_inplace(self, client):
        name = "test-ss-create-or-update-inplace"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc1")
        ss = await client.create_or_update_skillset(skillset1)
        expected_count = len(await client.get_skillsets())
        skillset2 = SearchIndexerSkillset(name=name, skills=[s], description="desc2", skillset=ss)
        await client.create_or_update_skillset(skillset2)
        assert len(await client.get_skillsets()) == expected_count

        result = await client.get_skillset(name)
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == name
        assert result.description == "desc2"

    async def _test_create_or_update_skillset_if_unchanged(self, client):
        name = "test-ss-create-or-update-unchanged"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset1 = SearchIndexerSkillset(name=name, skills=list([s]), description="desc1")
        ss = await client.create_or_update_skillset(skillset1)

        ss.e_tag = "changed_etag"

        with pytest.raises(HttpResponseError):
            await client.create_or_update_skillset(ss, match_condition=MatchConditions.IfNotModified)

    async def _test_delete_skillset_if_unchanged(self, client):
        name = "test-ss-deleted-unchanged"
        s = EntityRecognitionSkill(
            inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
            outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")],
        )

        skillset = SearchIndexerSkillset(name=name, skills=list([s]), description="desc")
        result = await client.create_skillset(skillset)
        etag = result.e_tag

        skillset1 = SearchIndexerSkillset(name=name, skills=list([s]), description="updated")
        updated = await client.create_or_update_skillset(skillset1)
        updated.e_tag = etag

        with pytest.raises(HttpResponseError):
            await client.delete_skillset(updated, match_condition=MatchConditions.IfNotModified)

    async def _test_delete_skillset(self, client):
        result = await client.get_skillset_names()
        for skillset in result:
            await client.delete_skillset(skillset)

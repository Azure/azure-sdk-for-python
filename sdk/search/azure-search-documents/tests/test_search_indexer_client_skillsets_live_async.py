# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async live tests for ``SearchIndexerClient`` skillset operations."""

from __future__ import annotations

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import (
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SplitSkill,
    TextSplitMode,
)
from devtools_testutils import AzureRecordedTestCase

from _search_helpers_async import live_test, make_indexer_client, safe_delete

SKILLSET_DESCRIPTION = "Skillset description"
REPLACEMENT_SKILLSET_DESCRIPTION = "Replacement skillset description"
STALE_SKILLSET_ETAG = "stale-skillset-etag"


def _build_split_skill(skill_name: str = "split-skill", target_name: str = "pages") -> SplitSkill:
    return SplitSkill(
        name=skill_name,
        inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
        outputs=[OutputFieldMappingEntry(name="textItems", target_name=target_name)],
        context="/document",
        text_split_mode=TextSplitMode.PAGES,
        maximum_page_length=5000,
    )


def _build_skillset(
    skillset_name: str,
    *,
    description: str = SKILLSET_DESCRIPTION,
    skills: list[SplitSkill] | None = None,
) -> SearchIndexerSkillset:
    return SearchIndexerSkillset(
        name=skillset_name,
        skills=skills or [_build_split_skill()],
        description=description,
    )


class TestSearchIndexerClientSkillsetAsync(AzureRecordedTestCase):
    @live_test()
    async def test_create_skillset_returns_created_resource(self, endpoint):
        skillset_name = self.get_resource_name("skillset-create")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                result = await client.create_skillset(
                    _build_skillset(
                        skillset_name,
                        skills=[
                            _build_split_skill("split-skill-pages", "pages"),
                            _build_split_skill("split-skill-sentences", "sentences"),
                        ],
                    )
                )

                assert isinstance(result, SearchIndexerSkillset)
                assert result.name == skillset_name
                assert result.description == SKILLSET_DESCRIPTION
                assert result.e_tag
                assert len(result.skills) == 2
                assert all(isinstance(skill, SplitSkill) for skill in result.skills)
                assert result.skills[0].maximum_page_length == 5000
            finally:
                await safe_delete(client.delete_skillset, skillset_name)

    @live_test()
    async def test_get_skillset_returns_created_resource(self, endpoint):
        skillset_name = self.get_resource_name("skillset-get")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                await client.create_skillset(_build_skillset(skillset_name))

                result = await client.get_skillset(skillset_name)

                assert isinstance(result, SearchIndexerSkillset)
                assert result.name == skillset_name
                assert result.description == SKILLSET_DESCRIPTION
                assert result.e_tag
                assert len(result.skills) == 1
                assert isinstance(result.skills[0], SplitSkill)
            finally:
                await safe_delete(client.delete_skillset, skillset_name)

    @live_test()
    async def test_get_skillsets_and_names_return_created_resources(self, endpoint):
        first_skillset_name = self.get_resource_name("skillset-list-first")
        second_skillset_name = self.get_resource_name("skillset-list-second")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                await client.create_skillset(_build_skillset(first_skillset_name))
                await client.create_skillset(_build_skillset(second_skillset_name))

                skillsets = await client.get_skillsets()
                skillset_names = await client.get_skillset_names()

                assert isinstance(skillsets, list)
                assert all(isinstance(result, SearchIndexerSkillset) for result in skillsets)
                assert {first_skillset_name, second_skillset_name}.issubset({result.name for result in skillsets})
                assert {first_skillset_name, second_skillset_name}.issubset(set(skillset_names))
            finally:
                await safe_delete(client.delete_skillset, first_skillset_name)
                await safe_delete(client.delete_skillset, second_skillset_name)

    @live_test()
    async def test_create_or_update_skillset_replaces_existing_resource(self, endpoint):
        skillset_name = self.get_resource_name("skillset-create-or-update")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                await client.create_or_update_skillset(_build_skillset(skillset_name))
                result = await client.create_or_update_skillset(
                    _build_skillset(skillset_name, description=REPLACEMENT_SKILLSET_DESCRIPTION)
                )

                assert isinstance(result, SearchIndexerSkillset)
                assert result.name == skillset_name
                assert result.description == REPLACEMENT_SKILLSET_DESCRIPTION
                existing = await client.get_skillset(skillset_name)
                assert existing.description == REPLACEMENT_SKILLSET_DESCRIPTION
            finally:
                await safe_delete(client.delete_skillset, skillset_name)

    @live_test()
    async def test_create_or_update_skillset_accepts_returned_model(self, endpoint):
        skillset_name = self.get_resource_name("skillset-create-or-update-inplace")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                skillset = await client.create_or_update_skillset(_build_skillset(skillset_name))
                skillset.description = REPLACEMENT_SKILLSET_DESCRIPTION

                result = await client.create_or_update_skillset(skillset)

                assert isinstance(result, SearchIndexerSkillset)
                assert result.name == skillset_name
                assert result.description == REPLACEMENT_SKILLSET_DESCRIPTION
            finally:
                await safe_delete(client.delete_skillset, skillset_name)

    @live_test()
    async def test_create_or_update_skillset_if_unchanged_uses_model_etag(self, endpoint):
        skillset_name = self.get_resource_name("skillset-create-or-update-if-unchanged")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                skillset = await client.create_or_update_skillset(_build_skillset(skillset_name))
                skillset.description = REPLACEMENT_SKILLSET_DESCRIPTION
                skillset.e_tag = STALE_SKILLSET_ETAG

                with pytest.raises(HttpResponseError):
                    await client.create_or_update_skillset(skillset, match_condition=MatchConditions.IfNotModified)
            finally:
                await safe_delete(client.delete_skillset, skillset_name)

    @live_test()
    async def test_delete_skillset_accepts_name(self, endpoint):
        skillset_name = self.get_resource_name("skillset-delete")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                await client.create_skillset(_build_skillset(skillset_name))

                await client.delete_skillset(skillset_name)

                assert skillset_name not in await client.get_skillset_names()
            finally:
                await safe_delete(client.delete_skillset, skillset_name)

    @live_test()
    async def test_delete_skillset_if_unchanged_uses_model_etag(self, endpoint):
        skillset_name = self.get_resource_name("skillset-delete-if-unchanged")
        client = make_indexer_client(endpoint)

        async with client:
            try:
                skillset = await client.create_skillset(_build_skillset(skillset_name))
                skillset.e_tag = STALE_SKILLSET_ETAG

                with pytest.raises(HttpResponseError):
                    await client.delete_skillset(skillset, match_condition=MatchConditions.IfNotModified)

                assert skillset_name in await client.get_skillset_names()
            finally:
                await safe_delete(client.delete_skillset, skillset_name)

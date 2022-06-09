# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import SynonymMap
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchClientSynonymMaps(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_synonym_map(self, **kwargs):
        endpoint = kwargs.pop("endpoint")
        api_key = kwargs.pop("api_key")
        client = SearchIndexClient(endpoint, api_key)
        async with client:
            await self._test_create_synonym_map(client)
            await self._test_delete_synonym_map(client)
            await self._test_delete_synonym_map_if_unchanged(client)
            await self._test_get_synonym_map(client)
            await self._test_get_synonym_maps(client)
            await self._test_create_or_update_synonym_map(client)

    async def _test_create_synonym_map(self, client):
        expected = len(await client.get_synonym_maps()) + 1
        name = "synmap-create"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        result = await client.create_synonym_map(synonym_map)
        assert isinstance(result, SynonymMap)
        assert result.name == name
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        assert len(await client.get_synonym_maps()) == expected
        await client.delete_synonym_map(name)

    async def _test_delete_synonym_map(self, client):
        name = "synmap-del"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        result = await client.create_synonym_map(synonym_map)
        expected = len(await client.get_synonym_maps()) - 1
        await client.delete_synonym_map(name)
        assert len(await client.get_synonym_maps()) == expected

    async def _test_delete_synonym_map_if_unchanged(self, client):
        name = "synmap-delunch"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        result = await client.create_synonym_map(synonym_map)
        etag = result.e_tag

        synonym_map.synonyms = "\n".join([
            "Washington, Wash. => WA",
        ])
        await client.create_or_update_synonym_map(synonym_map)

        result.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.delete_synonym_map(result, match_condition=MatchConditions.IfNotModified)
        await client.delete_synonym_map(name)

    async def _test_get_synonym_map(self, client):
        expected = len(await client.get_synonym_maps()) + 1
        name = "synmap-get"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        await client.create_synonym_map(synonym_map)
        assert len(await client.get_synonym_maps()) == expected
        result = await client.get_synonym_map(name)
        assert isinstance(result, SynonymMap)
        assert result.name == name
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        await client.delete_synonym_map(name)

    async def _test_get_synonym_maps(self, client):
        name1 = "synmap-list1"
        name2 = "synmap-list2"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map_1 = SynonymMap(name=name1, synonyms=synonyms)
        await client.create_synonym_map(synonym_map_1)
        synonyms = [
            "Washington, Wash. => WA",
        ]
        synonym_map_2 = SynonymMap(name=name2, synonyms=synonyms)
        await client.create_synonym_map(synonym_map_2)
        result = await client.get_synonym_maps()
        assert isinstance(result, list)
        assert all(isinstance(x, SynonymMap) for x in result)
        expected = set([name1, name2])
        assert set(x.name for x in result).intersection(expected) == expected
        await client.delete_synonym_map(name1)
        await client.delete_synonym_map(name2)

    async def _test_create_or_update_synonym_map(self, client):
        expected = len(await client.get_synonym_maps()) + 1
        name = "synmap-cou"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        await client.create_synonym_map(synonym_map)
        assert len(await client.get_synonym_maps()) == expected
        synonym_map.synonyms = [
            "Washington, Wash. => WA",
        ]
        await client.create_or_update_synonym_map(synonym_map)
        assert len(await client.get_synonym_maps()) == expected
        result = await client.get_synonym_map(name)
        assert isinstance(result, SynonymMap)
        assert result.name == name
        assert result.synonyms == [
            "Washington, Wash. => WA",
        ]
        await client.delete_synonym_map(name)

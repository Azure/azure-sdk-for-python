# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unicodedata import name
import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.aio import SearchIndexClient
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase
from azure.search.documents.indexes.models import (
    AnalyzeTextOptions,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SimpleField,
    SearchFieldDataType,
    SearchAlias,
)

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchClientAlias(AzureRecordedTestCase):
    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_alias(self, endpoint, api_key):
        client = SearchIndexClient(endpoint, api_key)
        aliases = ["resort", "motel"]

        async with client:
            index_name = await client.list_index_names().__anext__()
            await self._test_list_aliases_empty(client)
            await self._test_create_alias(client, aliases[0], index_name)

            await self._test_create_or_update_alias(client, aliases[1], index_name)

            # point an old alias to a new index
            new_index_name = "hotel"
            await self._test_update_alias_to_new_index(client, aliases[1], new_index_name, index_name)

            await self._test_get_alias(client, aliases)

            await self._test_list_aliases(client, aliases)
            await self._test_delete_aliases(client)

    async def _test_list_aliases_empty(self, client):
        result = client.list_aliases()
        with pytest.raises(StopAsyncIteration):
            await result.__anext__()

    async def _test_create_alias(self, client, alias_name, index_name):
        alias = SearchAlias(name=alias_name, indexes=[index_name])
        result = await client.create_alias(alias)
        assert result.name == alias_name
        assert set(result.indexes) == {index_name}

    async def _test_create_or_update_alias(self, client, alias_name, index_name):
        alias = SearchAlias(name=alias_name, indexes=[index_name])
        result = await client.create_or_update_alias(alias)
        assert result.name == alias_name
        assert set(result.indexes) == {index_name}

    async def _test_update_alias_to_new_index(self, client, alias_name, new_index, old_index):
        await self._create_index(client, new_index)
        alias = SearchAlias(name=alias_name, indexes=[new_index])
        result = await client.create_or_update_alias(alias)

        assert result.name == alias_name
        assert result.indexes[0] != old_index
        assert result.indexes[0] == new_index

    async def _test_get_alias(self, client, aliases):
        for alias in aliases:
            result = await client.get_alias(alias)
            assert result
            assert result.name == alias

    async def _test_list_aliases(self, client, aliases):
        result = {alias async for alias in client.list_alias_names()}
        assert result == set(aliases)

    async def _test_delete_aliases(self, client):
        aliases = [alias async for alias in client.list_aliases()]

        for alias in aliases:
            await client.delete_alias(alias)
            with pytest.raises(HttpResponseError):
                result = await client.get_alias(alias)

    async def _create_index(self, client, index_name):
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
            SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        ]
        scoring_profile = ScoringProfile(name="MyProfile")
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        index = SearchIndex(
            name=index_name, fields=fields, scoring_profiles=scoring_profiles, cors_options=cors_options
        )
        result = await client.create_index(index)

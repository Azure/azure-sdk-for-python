# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unicodedata import name
import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
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
    @recorded_by_proxy
    def test_alias(self, **kwargs):
        endpoint = kwargs.pop("endpoint")
        api_key = kwargs.pop("api_key")
        client = SearchIndexClient(endpoint, api_key)
        aliases = ["resort", "motel"]
        index_name = next(client.list_index_names())
        self._test_list_aliases_empty(client)
        self._test_create_alias(client, aliases[0], index_name)

        self._test_create_or_update_alias(client, aliases[1], index_name)

        # point an old alias to a new index
        new_index_name = "hotel"
        self._test_update_alias_to_new_index(client, aliases[1], new_index_name, index_name)

        self._test_get_alias(client, aliases)

        self._test_list_aliases(client, aliases)
        self._test_delete_aliases(client)

    def _test_list_aliases_empty(self, client):
        result = client.list_aliases()
        with pytest.raises(StopIteration):
            next(result)

    def _test_create_alias(self, client, alias_name, index_name):
        alias = SearchAlias(name=alias_name, indexes=[index_name])
        result = client.create_alias(alias)
        assert result.name == alias_name
        assert set(result.indexes) == {index_name}

    def _test_create_or_update_alias(self, client, alias_name, index_name):
        alias = SearchAlias(name=alias_name, indexes=[index_name])
        result = client.create_or_update_alias(alias)
        assert result.name == alias_name
        assert set(result.indexes) == {index_name}

    def _test_update_alias_to_new_index(self, client, alias_name, new_index, old_index):
        self._create_index(client, new_index)
        alias = SearchAlias(name=alias_name, indexes=[new_index])
        result = client.create_or_update_alias(alias)

        assert result.name == alias_name
        assert result.indexes[0] != old_index
        assert result.indexes[0] == new_index

    def _test_get_alias(self, client, aliases):
        for alias in aliases:
            result = client.get_alias(alias)
            assert result
            assert result.name == alias

    def _test_list_aliases(self, client, aliases):
        result = {alias for alias in client.list_alias_names()}
        assert result == set(aliases)

    def _test_delete_aliases(self, client):
        aliases = client.list_aliases()

        for alias in aliases:
            client.delete_alias(alias)
            with pytest.raises(HttpResponseError):
                result = client.get_alias(alias)

    def _create_index(self, client, index_name):
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
        result = client.create_index(index)

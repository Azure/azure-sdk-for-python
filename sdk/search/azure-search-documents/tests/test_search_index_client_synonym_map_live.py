# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import random
import string

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SynonymMap
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchSynonymMapsClient(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_synonym_map_crud(self, endpoint, api_key):

        client = SearchIndexClient(endpoint, api_key)
        map_name = "test-map"

        # test create
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=map_name, synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        original_result = result
        assert isinstance(result, SynonymMap)
        assert result.name == map_name
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        assert len(client.get_synonym_maps()) == 1

        # test create_or_update if unchanged
        client.create_or_update_synonym_map(synonym_map)
        with pytest.raises(HttpResponseError):
            client.create_or_update_synonym_map(result, match_condition=MatchConditions.IfNotModified)
        
        # test create_or_update if changed
        synonym_map.synonyms = ["Washington, Wash. => WA",]
        result = client.create_or_update_synonym_map(synonym_map)

        # test get_synonym_maps
        result = client.get_synonym_maps()
        assert isinstance(result, list)
        assert all(isinstance(x, SynonymMap) for x in result)
        assert all(x.name.startswith("test-map") for x in result)

        # test get_synonym_map
        result = client.get_synonym_map(map_name)
        assert isinstance(result, SynonymMap)
        assert result.name == map_name
        assert result.synonyms == [
            "Washington, Wash. => WA",
        ]

        # test delete_synonym_map if unchanged
        with pytest.raises(HttpResponseError):
            client.delete_synonym_map(original_result, match_condition=MatchConditions.IfNotModified)

        # test delete_synonym_map
        client.delete_synonym_map(map_name)
        assert len(client.get_synonym_maps()) == 0

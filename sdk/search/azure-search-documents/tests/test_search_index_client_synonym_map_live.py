# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SynonymMap
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator


class TestSearchClientSynonymMaps(AzureRecordedTestCase):

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy
    def test_synonym_map(self, endpoint, api_key):
        client = SearchIndexClient(endpoint, api_key)
        self._test_create_synonym_map(client)
        self._test_delete_synonym_map(client)
        self._test_delete_synonym_map_if_unchanged(client)
        self._test_get_synonym_map(client)
        self._test_get_synonym_maps(client)
        self._test_create_or_update_synonym_map(client)

    def _test_create_synonym_map(self, client):
        expected = len(client.get_synonym_maps()) + 1
        name = "synmap-create"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        assert isinstance(result, SynonymMap)
        assert result.name == name
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        assert len(client.get_synonym_maps()) == expected
        client.delete_synonym_map(name)

    def _test_delete_synonym_map(self, client):
        name = "synmap-del"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        expected = len(client.get_synonym_maps()) - 1
        client.delete_synonym_map(name)
        assert len(client.get_synonym_maps()) == expected

    def _test_delete_synonym_map_if_unchanged(self, client):
        name = "synmap-delunch"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        etag = result.e_tag

        synonym_map.synonyms = "\n".join([
            "Washington, Wash. => WA",
        ])
        client.create_or_update_synonym_map(synonym_map)

        result.e_tag = etag
        with pytest.raises(HttpResponseError):
            client.delete_synonym_map(result, match_condition=MatchConditions.IfNotModified)
        client.delete_synonym_map(name)

    def _test_get_synonym_map(self, client):
        expected = len(client.get_synonym_maps()) + 1
        name = "synmap-get"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        client.create_synonym_map(synonym_map)
        assert len(client.get_synonym_maps()) == expected
        result = client.get_synonym_map(name)
        assert isinstance(result, SynonymMap)
        assert result.name == name
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        client.delete_synonym_map(name)

    def _test_get_synonym_maps(self, client):
        name1 = "synmap-list1"
        name2 = "synmap-list2"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map_1 = SynonymMap(name=name1, synonyms=synonyms)
        client.create_synonym_map(synonym_map_1)
        synonyms = [
            "Washington, Wash. => WA",
        ]
        synonym_map_2 = SynonymMap(name=name2, synonyms=synonyms)
        client.create_synonym_map(synonym_map_2)
        result = client.get_synonym_maps()
        assert isinstance(result, list)
        assert all(isinstance(x, SynonymMap) for x in result)
        expected = set([name1, name2])
        assert set(x.name for x in result).intersection(expected) == expected
        client.delete_synonym_map(name1)
        client.delete_synonym_map(name2)

    def _test_create_or_update_synonym_map(self, client):
        expected = len(client.get_synonym_maps()) + 1
        name = "synmap-cou"
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=name, synonyms=synonyms)
        client.create_synonym_map(synonym_map)
        assert len(client.get_synonym_maps()) == expected
        synonym_map.synonyms = [
            "Washington, Wash. => WA",
        ]
        client.create_or_update_synonym_map(synonym_map)
        assert len(client.get_synonym_maps()) == expected
        result = client.get_synonym_map(name)
        assert isinstance(result, SynonymMap)
        assert result.name == name
        assert result.synonyms == [
            "Washington, Wash. => WA",
        ]
        client.delete_synonym_map(name)

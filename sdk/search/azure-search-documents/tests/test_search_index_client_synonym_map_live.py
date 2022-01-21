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

from tests.search_service_preparer import search_decorator


class TestSearchSynonymMapsClient(AzureRecordedTestCase):

    def _parse_kwargs(self, **kwargs):
        search_endpoint = kwargs.pop('search_service_endpoint')
        search_api_key = kwargs.pop('search_service_api_key')
        return (search_endpoint, search_api_key)

    def _update_variables(self, variables):
        if self.is_live:
            variables["map_name"] = self._random_tag("synmap-")
        return variables

    def _random_tag(self, prefix="", length=10):
        allowed_chars = string.ascii_letters
        random_tag = "".join(random.choice(allowed_chars) for x in range(length)).lower()
        return "{}{}".format(prefix, random_tag)

    @search_decorator
    @recorded_by_proxy
    def test_synonym_map_crud(self, variables, **kwargs):
        search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
        variables = self._update_variables(variables)
        map_name = variables["map_name"]

        client = SearchIndexClient(search_endpoint, search_api_key)

        # test create
        synonyms = [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        synonym_map = SynonymMap(name=map_name, synonyms=synonyms)
        result = client.create_synonym_map(synonym_map)
        assert isinstance(result, SynonymMap)
        assert result.name == map_name
        assert result.synonyms == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        assert len(client.get_synonym_maps()) == 1

        # test create_or_update
        client.create_or_update_synonym_map(synonym_map)
        with pytest.raises(HttpResponseError):
            client.create_or_update_synonym_map(result, match_condition=MatchConditions.IfNotModified)

        return variables


    # @search_decorator
    # @recorded_by_proxy
    # def test_delete_synonym_map(self, variables, **kwargs):
    #     search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
    #     variables = self._update_variables(variables)
    #     map_name = variables["map_name"]
    #     client = SearchIndexClient(search_endpoint, search_api_key)
    #     synonyms = [
    #         "USA, United States, United States of America",
    #         "Washington, Wash. => WA",
    #     ]
    #     synonym_map = SynonymMap(name=map_name, synonyms=synonyms)
    #     result = client.create_synonym_map(synonym_map)
    #     assert len(client.get_synonym_maps()) == 1
    #     client.delete_synonym_map(map_name)
    #     assert len(client.get_synonym_maps()) == 0
    #     return variables

    # @search_decorator
    # @recorded_by_proxy
    # def test_delete_synonym_map_if_unchanged(self, variables, **kwargs):
    #     search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
    #     variables = self._update_variables(variables)
    #     map_name = variables["map_name"]
    #     client = SearchIndexClient(search_endpoint, search_api_key)
    #     synonyms = [
    #         "USA, United States, United States of America",
    #         "Washington, Wash. => WA",
    #     ]
    #     synonym_map = SynonymMap(name=map_name, synonyms=synonyms)
    #     result = client.create_synonym_map(synonym_map)
    #     etag = result.e_tag

    #     synonym_map.synonyms = "\n".join([
    #         "Washington, Wash. => WA",
    #     ])
    #     client.create_or_update_synonym_map(synonym_map)

    #     result.e_tag = etag
    #     with pytest.raises(HttpResponseError):
    #         client.delete_synonym_map(result, match_condition=MatchConditions.IfNotModified)
    #         assert len(client.get_synonym_maps()) == 1
    #     return variables

    # @search_decorator
    # @recorded_by_proxy
    # def test_get_synonym_map(self, variables, **kwargs):
    #     search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
    #     variables = self._update_variables(variables)
    #     map_name = variables["map_name"]
    #     client = SearchIndexClient(search_endpoint, search_api_key)
    #     synonyms = [
    #         "USA, United States, United States of America",
    #         "Washington, Wash. => WA",
    #     ]
    #     synonym_map = SynonymMap(name=map_name, synonyms=synonyms)
    #     client.create_synonym_map(synonym_map)
    #     assert len(client.get_synonym_maps()) == 1
    #     result = client.get_synonym_map(map_name)
    #     assert isinstance(result, SynonymMap)
    #     assert result.name == map_name
    #     assert result.synonyms == [
    #         "USA, United States, United States of America",
    #         "Washington, Wash. => WA",
    #     ]
    #     return variables

    # @search_decorator
    # @recorded_by_proxy
    # def test_get_synonym_maps(self, variables, **kwargs):
    #     search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
    #     variables = self._update_variables(variables)
    #     map_name = variables["map_name"]
    #     client = SearchIndexClient(search_endpoint, search_api_key)
    #     synonyms = [
    #         "USA, United States, United States of America",
    #     ]
    #     synonym_map_1 = SynonymMap(name="test-syn-map-1", synonyms=synonyms)
    #     client.create_synonym_map(synonym_map_1)
    #     synonyms = [
    #         "Washington, Wash. => WA",
    #     ]
    #     synonym_map_2 = SynonymMap(name="test-syn-map-2", synonyms=synonyms)
    #     client.create_synonym_map(synonym_map_2)
    #     result = client.get_synonym_maps()
    #     assert isinstance(result, list)
    #     assert all(isinstance(x, SynonymMap) for x in result)
    #     assert set(x.name for x in result) == {"test-syn-map-1", "test-syn-map-2"}
    #     return variables

    # @search_decorator
    # @recorded_by_proxy
    # def test_create_or_update_synonym_map(self, variables, **kwargs):
    #     search_endpoint, search_api_key = self._parse_kwargs(**kwargs)
    #     variables = self._update_variables(variables)
    #     map_name = variables["map_name"]
    #     client = SearchIndexClient(search_endpoint, search_api_key)
    #     synonyms = [
    #         "USA, United States, United States of America",
    #         "Washington, Wash. => WA",
    #     ]
    #     synonym_map = SynonymMap(name=map_name, synonyms=synonyms)
    #     client.create_synonym_map(synonym_map)
    #     assert len(client.get_synonym_maps()) == 1
    #     synonym_map.synonyms = ["Washington, Wash. => WA",]
    #     client.create_or_update_synonym_map(synonym_map)
    #     assert len(client.get_synonym_maps()) == 1
    #     result = client.get_synonym_map(map_name)
    #     assert isinstance(result, SynonymMap)
    #     assert result.name == map_name
    #     assert result.synonyms == [
    #         "Washington, Wash. => WA",
    #     ]
    #     return variables

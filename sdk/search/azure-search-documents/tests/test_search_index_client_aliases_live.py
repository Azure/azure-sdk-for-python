# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live tests for ``SearchIndexClient`` alias operations."""
from __future__ import annotations

import pytest

from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import SearchAlias
from devtools_testutils import AzureRecordedTestCase

from _search_helpers import build_index, live_test, make_index_client, safe_delete

ALIAS_NAME = "alias-create"
MODEL_ALIAS_NAME = "alias-create-or-update"


class TestSearchIndexClientAlias(AzureRecordedTestCase):
    @live_test()
    def test_create_get_list_and_delete_alias(self, endpoint):
        client = make_index_client(endpoint)
        index_name = self.get_resource_name("index-create-alias")
        alias_name = self.get_resource_name(ALIAS_NAME)
        try:
            client.create_index(build_index(index_name))
            created_alias = client.create_alias(SearchAlias(name=alias_name, indexes=[index_name]))

            assert created_alias.name == alias_name
            assert created_alias.indexes == [index_name]

            retrieved_alias = client.get_alias(alias_name)
            assert retrieved_alias.name == alias_name
            assert retrieved_alias.indexes == [index_name]

            assert alias_name in {alias.name for alias in client.list_aliases()}
            assert alias_name in set(client.list_alias_names())

            client.delete_alias(alias_name)
            with pytest.raises(HttpResponseError):
                client.get_alias(alias_name)
        finally:
            safe_delete(client.delete_alias, alias_name)
            safe_delete(client.delete_index, index_name)
            client.close()

    @live_test()
    def test_create_or_update_alias_accepts_model_and_mapping(self, endpoint):
        client = make_index_client(endpoint)
        first_index_name = self.get_resource_name("index-create-or-update-alias-first")
        second_index_name = self.get_resource_name("index-create-or-update-alias-second")
        model_alias_name = self.get_resource_name(MODEL_ALIAS_NAME)
        mapping_alias_name = self.get_resource_name("alias-create-or-update-mapping")
        try:
            client.create_index(build_index(first_index_name))
            client.create_index(build_index(second_index_name))

            model_alias = SearchAlias(name=model_alias_name, indexes=[first_index_name])
            model_result = client.create_or_update_alias(model_alias)
            assert model_result.name == model_alias_name
            assert model_result.indexes == [first_index_name]

            model_result.indexes = [second_index_name]
            model_result = client.create_or_update_alias(model_result)
            assert model_result.indexes == [second_index_name]

            mapping_alias = SearchAlias(name=mapping_alias_name, indexes=[first_index_name]).as_dict()
            mapping_result = client.create_or_update_alias(mapping_alias)
            assert mapping_result.name == mapping_alias_name
            assert mapping_result.indexes == [first_index_name]
        finally:
            safe_delete(client.delete_alias, model_alias_name)
            safe_delete(client.delete_alias, mapping_alias_name)
            safe_delete(client.delete_index, first_index_name)
            safe_delete(client.delete_index, second_index_name)
            client.close()

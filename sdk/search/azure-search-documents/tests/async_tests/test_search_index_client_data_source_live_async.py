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
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
)
from azure.search.documents.indexes.aio import SearchIndexerClient


class TestSearchClientDataSourcesAsync(AzureRecordedTestCase):
    def _create_data_source_connection(self, cs, name):
        container = SearchIndexerDataContainer(name="searchcontainer")
        data_source_connection = SearchIndexerDataSourceConnection(
            name=name, type="azureblob", connection_string=cs, container=container
        )
        return data_source_connection

    @SearchEnvVarPreparer()
    @search_decorator(schema="hotel_schema.json", index_batch="hotel_small.json")
    @recorded_by_proxy_async
    async def test_data_source(self, endpoint, api_key, **kwargs):
        storage_cs = kwargs.get("search_storage_connection_string")
        client = SearchIndexerClient(endpoint, api_key, retry_backoff_factor=60)
        async with client:
            await self._test_create_datasource(client, storage_cs)
            await self._test_delete_datasource(client, storage_cs)
            await self._test_get_datasource(client, storage_cs)
            await self._test_list_datasources(client, storage_cs)
            await self._test_create_or_update_datasource(client, storage_cs)
            await self._test_create_or_update_datasource_if_unchanged(client, storage_cs)
            await self._test_delete_datasource_if_unchanged(client, storage_cs)

    async def _test_create_datasource(self, client, storage_cs):
        ds_name = "create"
        data_source_connection = self._create_data_source_connection(storage_cs, ds_name)
        result = await client.create_data_source_connection(data_source_connection)
        assert result.name == ds_name
        assert result.type == "azureblob"

    async def _test_delete_datasource(self, client, storage_cs):
        ds_name = "delete"
        data_source_connection = self._create_data_source_connection(storage_cs, ds_name)
        await client.create_data_source_connection(data_source_connection)
        expected_count = len(await client.get_data_source_connections()) - 1
        await client.delete_data_source_connection(ds_name)
        assert len(await client.get_data_source_connections()) == expected_count

    async def _test_get_datasource(self, client, storage_cs):
        ds_name = "get"
        data_source_connection = self._create_data_source_connection(storage_cs, ds_name)
        await client.create_data_source_connection(data_source_connection)
        result = await client.get_data_source_connection(ds_name)
        assert result.name == ds_name

    async def _test_list_datasources(self, client, storage_cs):
        data_source_connection1 = self._create_data_source_connection(storage_cs, "list")
        data_source_connection2 = self._create_data_source_connection(storage_cs, "list2")
        await client.create_data_source_connection(data_source_connection1)
        await client.create_data_source_connection(data_source_connection2)
        result = await client.get_data_source_connections()
        assert isinstance(result, list)
        assert set(x.name for x in result).intersection(set(["list", "list2"])) == set(["list", "list2"])

    async def _test_create_or_update_datasource(self, client, storage_cs):
        ds_name = "cou"
        data_source_connection = self._create_data_source_connection(storage_cs, ds_name)
        await client.create_data_source_connection(data_source_connection)
        expected_count = len(await client.get_data_source_connections())
        data_source_connection.description = "updated"
        await client.create_or_update_data_source_connection(data_source_connection)
        assert len(await client.get_data_source_connections()) == expected_count
        result = await client.get_data_source_connection(ds_name)
        assert result.name == ds_name
        assert result.description == "updated"

    async def _test_create_or_update_datasource_if_unchanged(self, client, storage_cs):
        ds_name = "couunch"
        data_source_connection = self._create_data_source_connection(storage_cs, ds_name)
        created = await client.create_data_source_connection(data_source_connection)
        etag = created.e_tag

        # Now update the data source connection
        data_source_connection.description = "updated"
        await client.create_or_update_data_source_connection(data_source_connection)

        # prepare data source connection
        data_source_connection.e_tag = etag  # reset to the original data source connection
        data_source_connection.description = "changed"
        with pytest.raises(HttpResponseError):
            await client.create_or_update_data_source_connection(
                data_source_connection, match_condition=MatchConditions.IfNotModified
            )

    async def _test_delete_datasource_if_unchanged(self, client, storage_cs):
        ds_name = "delunch"
        data_source_connection = self._create_data_source_connection(storage_cs, ds_name)
        created = await client.create_data_source_connection(data_source_connection)
        etag = created.e_tag

        # Now update the data source connection
        data_source_connection.description = "updated"
        await client.create_or_update_data_source_connection(data_source_connection)

        # prepare data source connection
        data_source_connection.e_tag = etag  # reset to the original data source connection
        with pytest.raises(HttpResponseError):
            await client.delete_data_source_connection(
                data_source_connection, match_condition=MatchConditions.IfNotModified
            )

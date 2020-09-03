# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath

import pytest

from devtools_testutils import AzureMgmtTestCase

from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer
from azure_devtools.scenario_tests import ReplayableTest

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
)
from azure.search.documents.indexes import SearchIndexerClient

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "hotel_schema.json")).read()
try:
    BATCH = json.load(open(join(CWD, "hotel_small.json")))
except UnicodeDecodeError:
    BATCH = json.load(open(join(CWD, "hotel_small.json"), encoding='utf-8'))
TIME_TO_SLEEP = 5
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net'

class SearchDataSourcesClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    def _create_data_source_connection(self, name="sample-datasource"):
        container = SearchIndexerDataContainer(name='searchcontainer')
        data_source_connection = SearchIndexerDataSourceConnection(
            name=name,
            type="azureblob",
            connection_string=CONNECTION_STRING,
            container=container
        )
        return data_source_connection

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        result = client.create_data_source_connection(data_source_connection)
        assert result.name == "sample-datasource"
        assert result.type == "azureblob"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        result = client.create_data_source_connection(data_source_connection)
        assert len(client.get_data_source_connections()) == 1
        client.delete_data_source_connection("sample-datasource")
        assert len(client.get_data_source_connections()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = client.create_data_source_connection(data_source_connection)
        result = client.get_data_source_connection("sample-datasource")
        assert result.name == "sample-datasource"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_list_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection1 = self._create_data_source_connection()
        data_source_connection2 = self._create_data_source_connection(name="another-sample")
        created1 = client.create_data_source_connection(data_source_connection1)
        created2 = client.create_data_source_connection(data_source_connection2)
        result = client.get_data_source_connections()
        assert isinstance(result, list)
        assert set(x.name for x in result) == {"sample-datasource", "another-sample"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = client.create_data_source_connection(data_source_connection)
        assert len(client.get_data_source_connections()) == 1
        data_source_connection.description = "updated"
        client.create_or_update_data_source_connection(data_source_connection)
        assert len(client.get_data_source_connections()) == 1
        result = client.get_data_source_connection("sample-datasource")
        assert result.name == "sample-datasource"
        assert result.description == "updated"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_datasource_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = client.create_data_source_connection(data_source_connection)
        etag = created.e_tag

        # Now update the data source connection
        data_source_connection.description = "updated"
        client.create_or_update_data_source_connection(data_source_connection)

        # prepare data source connection
        data_source_connection.e_tag = etag # reset to the original data source connection
        data_source_connection.description = "changed"
        with pytest.raises(HttpResponseError):
            client.create_or_update_data_source_connection(data_source_connection, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_datasource_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = client.create_data_source_connection(data_source_connection)
        etag = created.e_tag

        # Now update the data source connection
        data_source_connection.description = "updated"
        client.create_or_update_data_source_connection(data_source_connection)

        # prepare data source connection
        data_source_connection.e_tag = etag # reset to the original data source connection
        with pytest.raises(HttpResponseError):
            client.delete_data_source_connection(data_source_connection, match_condition=MatchConditions.IfNotModified)
            assert len(client.get_data_source_connections()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_datasource_string_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        data_source_connection = self._create_data_source_connection()
        created = client.create_data_source_connection(data_source_connection)
        etag = created.e_tag

        # Now update the data source connection
        data_source_connection.description = "updated"
        client.create_or_update_data_source_connection(data_source_connection)

        # prepare data source connection
        data_source_connection.e_tag = etag # reset to the original data source connection
        with pytest.raises(ValueError):
            client.delete_data_source_connection(data_source_connection.name, match_condition=MatchConditions.IfNotModified)

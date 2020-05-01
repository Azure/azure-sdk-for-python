# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
import json
from os.path import dirname, join, realpath
import time

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureMgmtTestCase

from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function

from azure.core.exceptions import HttpResponseError
from azure.search.documents import(
    AnalyzeRequest,
    AnalyzeResult,
    CorsOptions,
    EntityRecognitionSkill,
    Field,
    Index,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchServiceClient,
    ScoringProfile,
    Skillset,
    DataSourceCredentials,
    DataSource,
    DataContainer,
    Indexer,
    SynonymMap,
    SimpleField,
    edm
)
from azure.search.documents.aio import SearchServiceClient
from _test_utils import build_synonym_map_from_dict

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "..", "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "..", "hotel_small.json"), encoding='utf-8'))
TIME_TO_SLEEP = 5
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net'

def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
    upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        trim_kwargs_from_test_function(test_fn, kwargs)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

    return run

class SearchClientTest(AzureMgmtTestCase):
    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    async def test_get_service_statistics(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = await client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}

class SearchIndexesClientTest(AzureMgmtTestCase):

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    async def test_list_indexes_empty(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        result = await client.list_indexes()

        with pytest.raises(StopAsyncIteration):
            await result.__anext__()

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_list_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        result = await client.list_indexes()

        first = await result.__anext__()
        assert first.name == index_name

        with pytest.raises(StopAsyncIteration):
            await result.__anext__()

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_index(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        result = await client.get_index(index_name)
        assert result.name == index_name

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_index_statistics(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        result = await client.get_index_statistics(index_name)
        assert set(result.keys()) == {'document_count', 'storage_size'}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        await client.delete_index(index_name)
        import time
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)
        result = await client.list_indexes()
        with pytest.raises(StopAsyncIteration):
            await result.__anext__()

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_indexes_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()

        # First create an index
        name = "hotels"
        fields = [
        {
          "name": "hotelId",
          "type": "Edm.String",
          "key": True,
          "searchable": False
        },
        {
          "name": "baseRate",
          "type": "Edm.Double"
        }]
        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = await client.create_index(index)
        etag = result.e_tag
        # get e tag  nd update
        index.scoring_profiles = []
        await client.create_or_update_index(index.name, index)

        index.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.delete_index(index, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_index(self, api_key, endpoint, index_name, **kwargs):
        name = "hotels"
        fields = fields = [
            SimpleField(name="hotelId", type=edm.String, key=True),
            SimpleField(name="baseRate", type=edm.Double)
        ]

        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        result = await client.create_index(index)
        assert result.name == "hotels"
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_index(self, api_key, endpoint, index_name, **kwargs):
        name = "hotels"
        fields = fields = [
            SimpleField(name="hotelId", type=edm.String, key=True),
            SimpleField(name="baseRate", type=edm.Double)
        ]

        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        scoring_profiles = []
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        result = await client.create_or_update_index(index_name=index.name, index=index)
        assert len(result.scoring_profiles) == 0
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds
        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = await client.create_or_update_index(index_name=index.name, index=index)
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_indexes_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()

        # First create an index
        name = "hotels"
        fields = [
        {
          "name": "hotelId",
          "type": "Edm.String",
          "key": True,
          "searchable": False
        },
        {
          "name": "baseRate",
          "type": "Edm.Double"
        }]
        scoring_profile = ScoringProfile(
            name="MyProfile"
        )
        scoring_profiles = []
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        result = await client.create_index(index)
        etag = result.e_tag
        # get e tag  nd update
        index.scoring_profiles = []
        await client.create_or_update_index(index.name, index)

        index.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.create_or_update_index(index.name, index, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_analyze_text(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexes_client()
        analyze_request = AnalyzeRequest(text="One's <two/>", analyzer="standard.lucene")
        result = await client.analyze_text(index_name, analyze_request)
        assert len(result.tokens) == 2

class SearchSynonymMapsClientTest(AzureMgmtTestCase):
    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_synonym_maps_client()
        result = await client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ])
        assert isinstance(result, dict)
        assert result["name"] == "test-syn-map"
        assert result["synonyms"] == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        assert len(await client.get_synonym_maps()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_synonym_maps_client()
        result = await client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ])
        assert len(await client.get_synonym_maps()) == 1
        await client.delete_synonym_map("test-syn-map")
        assert len(await client.get_synonym_maps()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_synonym_map_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_synonym_maps_client()
        result = await client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ])
        sm_result = build_synonym_map_from_dict(result)
        etag = sm_result.e_tag

        await client.create_or_update_synonym_map("test-syn-map", [
                    "Washington, Wash. => WA",
                ])

        sm_result.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.delete_synonym_map(sm_result, match_condition=MatchConditions.IfNotModified)
            assert len(client.get_synonym_maps()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_synonym_maps_client()
        await client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ])
        assert len(await client.get_synonym_maps()) == 1
        result = await client.get_synonym_map("test-syn-map")
        assert isinstance(result, dict)
        assert result["name"] == "test-syn-map"
        assert result["synonyms"] == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_synonym_maps(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_synonym_maps_client()
        await client.create_synonym_map("test-syn-map-1", [
            "USA, United States, United States of America",
        ])
        await client.create_synonym_map("test-syn-map-2", [
            "Washington, Wash. => WA",
        ])
        result = await client.get_synonym_maps()
        assert isinstance(result, list)
        assert all(isinstance(x, dict) for x in result)
        assert set(x['name'] for x in result) == {"test-syn-map-1", "test-syn-map-2"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_synonym_maps_client()
        await client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
        ])
        assert len(await client.get_synonym_maps()) == 1
        await client.create_or_update_synonym_map("test-syn-map", [
            "Washington, Wash. => WA",
        ])
        assert len(await client.get_synonym_maps()) == 1
        result = await client.get_synonym_map("test-syn-map")
        assert isinstance(result, dict)
        assert result["name"] == "test-syn-map"
        assert result["synonyms"] == [
            "Washington, Wash. => WA",
        ]

class SearchSkillsetClientTest(AzureMgmtTestCase):

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()

        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        result = await client.create_skillset(name='test-ss', skills=[s], description="desc")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

        assert len(await client.get_skillsets()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        result = await client.create_skillset(name='test-ss', skills=[s], description="desc")
        assert len(await client.get_skillsets()) == 1

        await client.delete_skillset("test-ss")
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)
        assert len(await client.get_skillsets()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_skillset_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        result = await client.create_skillset(name='test-ss', skills=[s], description="desc")
        etag = result.e_tag

        updated = await client.create_or_update_skillset(name='test-ss', skills=[s], description="updated")
        updated.e_tag = etag

        with pytest.raises(HttpResponseError):
            await client.delete_skillset(updated, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        await client.create_skillset(name='test-ss', skills=[s], description="desc")
        assert len(await client.get_skillsets()) == 1

        result = await client.get_skillset("test-ss")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_skillsets(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        await client.create_skillset(name='test-ss-1', skills=[s], description="desc1")
        await client.create_skillset(name='test-ss-2', skills=[s], description="desc2")
        result = await client.get_skillsets()
        assert isinstance(result, list)
        assert all(isinstance(x, Skillset) for x in result)
        assert set(x.name for x in result) == {"test-ss-1", "test-ss-2"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        await client.create_or_update_skillset(name='test-ss', skills=[s], description="desc1")
        await client.create_or_update_skillset(name='test-ss', skills=[s], description="desc2")
        assert len(await client.get_skillsets()) == 1

        result = await client.get_skillset("test-ss")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_skillset_inplace(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        ss = await client.create_or_update_skillset(name='test-ss', skills=[s], description="desc1")
        await client.create_or_update_skillset(name='test-ss', skills=[s], description="desc2", skillset=ss)
        assert len(await client.get_skillsets()) == 1

        result = await client.get_skillset("test-ss")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_skillset_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_skillsets_client()
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        ss = await client.create_or_update_skillset(name='test-ss', skills=[s], description="desc1")
        etag = ss.e_tag

        await client.create_or_update_skillset(name='test-ss', skills=[s], description="desc2", skillset=ss)
        assert len(await client.get_skillsets()) == 1

        ss.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.create_or_update_skillset(name='test-ss', skills=[s], skillset=ss, match_condition=MatchConditions.IfNotModified)


class SearchDataSourcesClientTest(AzureMgmtTestCase):

    def _create_datasource(self, name="sample-datasource"):
        credentials = DataSourceCredentials(connection_string=CONNECTION_STRING)
        container = DataContainer(name='searchcontainer')
        data_source = DataSource(
            name=name,
            type="azureblob",
            credentials=credentials,
            container=container
        )
        return data_source

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        result = await client.create_datasource(data_source)
        assert result.name == "sample-datasource"
        assert result.type == "azureblob"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        result = await client.create_datasource(data_source)
        assert len(await client.get_datasources()) == 1
        await client.delete_datasource("sample-datasource")
        assert len(await client.get_datasources()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        created = await client.create_datasource(data_source)
        result = await client.get_datasource("sample-datasource")
        assert result.name == "sample-datasource"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_list_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source1 = self._create_datasource()
        data_source2 = self._create_datasource(name="another-sample")
        created1 = await client.create_datasource(data_source1)
        created2 = await client.create_datasource(data_source2)
        result = await client.get_datasources()
        assert isinstance(result, list)
        assert set(x.name for x in result) == {"sample-datasource", "another-sample"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_datasource_async(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        created = await client.create_datasource(data_source)
        assert len(await client.get_datasources()) == 1
        data_source.description = "updated"
        await client.create_or_update_datasource(data_source)
        assert len(await client.get_datasources()) == 1
        result = await client.get_datasource("sample-datasource")
        assert result.name == "sample-datasource"
        assert result.description == "updated"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_datasource_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        created = await client.create_datasource(data_source)
        etag = created.e_tag

        # Now update the data source
        data_source.description = "updated"
        await client.create_or_update_datasource(data_source)

        # prepare data source
        data_source.e_tag = etag # reset to the original datasource
        data_source.description = "changed"
        with pytest.raises(HttpResponseError):
            await client.create_or_update_datasource(data_source, match_condition=MatchConditions.IfNotModified)
            assert len(await client.get_datasources()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_datasource_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        created = await client.create_datasource(data_source)
        etag = created.e_tag

        # Now update the data source
        data_source.description = "updated"
        await client.create_or_update_datasource(data_source)

        # prepare data source
        data_source.e_tag = etag # reset to the original datasource
        with pytest.raises(HttpResponseError):
            await client.delete_datasource(data_source, match_condition=MatchConditions.IfNotModified)
            assert len(await client.get_datasources()) == 1

class SearchIndexersClientTest(AzureMgmtTestCase):

    async def _prepare_indexer(self, endpoint, api_key, name="sample-indexer", ds_name="sample-datasource", id_name="hotels"):
        con_str = self.settings.AZURE_STORAGE_CONNECTION_STRING
        self.scrubber.register_name_pair(con_str, 'connection_string')
        credentials = DataSourceCredentials(connection_string=con_str)
        container = DataContainer(name='searchcontainer')
        data_source = DataSource(
            name=ds_name,
            type="azureblob",
            credentials=credentials,
            container=container
        )
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        ds_client = client.get_datasources_client()
        ds = await ds_client.create_datasource(data_source)

        index_name = id_name
        fields = [
        {
          "name": "hotelId",
          "type": "Edm.String",
          "key": True,
          "searchable": False
        }]
        index = Index(name=index_name, fields=fields)
        ind_client = client.get_indexes_client()
        ind = await ind_client.create_index(index)
        return Indexer(name=name, data_source_name=ds.name, target_index_name=ind.name)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert result.name == "sample-indexer"
        assert result.target_index_name == "hotels"
        assert result.data_source_name == "sample-datasource"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        await client.delete_indexer("sample-indexer")
        assert len(await client.get_indexers()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        created = await client.create_indexer(indexer)
        result = await client.get_indexer("sample-indexer")
        assert result.name == "sample-indexer"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_list_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer1 = await self._prepare_indexer(endpoint, api_key)
        indexer2 = await self._prepare_indexer(endpoint, api_key, name="another-indexer", ds_name="another-datasource", id_name="another-index")
        created1 = await client.create_indexer(indexer1)
        created2 = await client.create_indexer(indexer2)
        result = await client.get_indexers()
        assert isinstance(result, list)
        assert set(x.name for x in result) == {"sample-indexer", "another-indexer"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        created = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        indexer.description = "updated"
        await client.create_or_update_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        result = await client.get_indexer("sample-indexer")
        assert result.name == "sample-indexer"
        assert result.description == "updated"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_reset_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        await client.reset_indexer("sample-indexer")
        assert (await client.get_indexer_status("sample-indexer")).last_result.status in ('InProgress', 'reset')

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_run_indexer(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        assert len(await client.get_indexers()) == 1
        start = time.time()
        await client.run_indexer("sample-indexer")
        assert (await client.get_indexer_status("sample-indexer")).status == 'running'

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_get_indexer_status(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        status = await client.get_indexer_status("sample-indexer")
        assert status.status is not None

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_create_or_update_indexer_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        created = await client.create_indexer(indexer)
        etag = created.e_tag


        indexer.description = "updated"
        await client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.create_or_update_indexer(indexer, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    async def test_delete_indexer_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_indexers_client()
        indexer = await self._prepare_indexer(endpoint, api_key)
        result = await client.create_indexer(indexer)
        etag = result.e_tag

        indexer.description = "updated"
        await client.create_or_update_indexer(indexer)

        indexer.e_tag = etag
        with pytest.raises(HttpResponseError):
            await client.delete_indexer(indexer, match_condition=MatchConditions.IfNotModified)

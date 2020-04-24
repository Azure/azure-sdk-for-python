# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath
import time

import pytest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

from search_service_preparer import SearchServicePreparer

from azure.core.credentials import AzureKeyCredential
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
    DataContainer
)

CWD = dirname(realpath(__file__))
SCHEMA = open(join(CWD, "hotel_schema.json")).read()
BATCH = json.load(open(join(CWD, "hotel_small.json")))
TIME_TO_SLEEP = 5
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net'

class SearchClientTest(AzureMgmtTestCase):

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    def test_get_service_statistics(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_service_statistics()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"counters", "limits"}

    # Index operations

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer()
    def test_get_indexes_empty(self, api_key, endpoint, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_indexes()
        assert len(result) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_indexes()
        assert len(result) == 1
        assert result[0].name == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_index(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_index(index_name)
        assert result.name == index_name

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_index_statistics(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.get_index_statistics(index_name)
        assert set(result.keys()) == {'document_count', 'storage_size'}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_indexes(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        client.delete_index(index_name)
        import time
        if self.is_live:
            time.sleep(TIME_TO_SLEEP)
        result = client.get_indexes()
        assert len(result) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_index(self, api_key, endpoint, index_name, **kwargs):
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
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.create_index(index)
        assert result.name == "hotels"
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_index(self, api_key, endpoint, index_name, **kwargs):
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
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        scoring_profiles = []
        index = Index(
            name=name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options)
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.create_or_update_index(index_name=index.name, index=index)
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
        result = client.create_or_update_index(index_name=index.name, index=index)
        assert result.scoring_profiles[0].name == scoring_profile.name
        assert result.cors_options.allowed_origins == cors_options.allowed_origins
        assert result.cors_options.max_age_in_seconds == cors_options.max_age_in_seconds

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_analyze_text(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        analyze_request = AnalyzeRequest(text="One's <two/>", analyzer="standard.lucene")
        result = client.analyze_text(index_name, analyze_request)
        assert len(result.tokens) == 2

    # Synonym Map operations

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ])
        assert isinstance(result, dict)
        assert result["name"] == "test-syn-map"
        assert result["synonyms"] == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]
        assert len(client.get_synonym_maps()) == 1

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        result = client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ])
        assert len(client.get_synonym_maps()) == 1
        client.delete_synonym_map("test-syn-map")
        assert len(client.get_synonym_maps()) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ])
        assert len(client.get_synonym_maps()) == 1
        result = client.get_synonym_map("test-syn-map")
        assert isinstance(result, dict)
        assert result["name"] == "test-syn-map"
        assert result["synonyms"] == [
            "USA, United States, United States of America",
            "Washington, Wash. => WA",
        ]

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_synonym_maps(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        client.create_synonym_map("test-syn-map-1", [
            "USA, United States, United States of America",
        ])
        client.create_synonym_map("test-syn-map-2", [
            "Washington, Wash. => WA",
        ])
        result = client.get_synonym_maps()
        assert isinstance(result, list)
        assert all(isinstance(x, dict) for x in result)
        assert set(x['name'] for x in result) == {"test-syn-map-1", "test-syn-map-2"}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_synonym_map(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        client.create_synonym_map("test-syn-map", [
            "USA, United States, United States of America",
        ])
        assert len(client.get_synonym_maps()) == 1
        client.create_or_update_synonym_map("test-syn-map", [
            "Washington, Wash. => WA",
        ])
        assert len(client.get_synonym_maps()) == 1
        result = client.get_synonym_map("test-syn-map")
        assert isinstance(result, dict)
        assert result["name"] == "test-syn-map"
        assert result["synonyms"] == [
            "Washington, Wash. => WA",
        ]

    # Skillset operations

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))

        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        result = client.create_skillset(name='test-ss', skills=[s], description="desc")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

        assert len(client.get_skillsets()) == 1

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        result = client.create_skillset(name='test-ss', skills=[s], description="desc")
        assert len(client.get_skillsets()) == 1

        client.delete_skillset("test-ss")
        assert len(client.get_skillsets()) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        client.create_skillset(name='test-ss', skills=[s], description="desc")
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_skillsets(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        client.create_skillset(name='test-ss-1', skills=[s], description="desc1")
        client.create_skillset(name='test-ss-2', skills=[s], description="desc2")
        result = client.get_skillsets()
        assert isinstance(result, list)
        assert all(isinstance(x, Skillset) for x in result)
        assert set(x.name for x in result) == {"test-ss-1", "test-ss-2"}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        client.create_or_update_skillset(name='test-ss', skills=[s], description="desc1")
        client.create_or_update_skillset(name='test-ss', skills=[s], description="desc2")
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset_inplace(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        ss = client.create_or_update_skillset(name='test-ss', skills=[s], description="desc1")
        client.create_or_update_skillset(name='test-ss', skills=[s], description="desc2", skillset=ss)
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, Skillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

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

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        result = client.create_datasource(data_source)
        assert result.name == "sample-datasource"
        assert result.type == "azureblob"

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        result = client.create_datasource(data_source)
        assert len(client.get_datasources()) == 1
        client.delete_datasource("sample-datasource")
        assert len(client.get_datasources()) == 0

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        created = client.create_datasource(data_source)
        result = client.get_datasource("sample-datasource")
        assert result.name == "sample-datasource"

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_list_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source1 = self._create_datasource()
        data_source2 = self._create_datasource(name="another-sample")
        created1 = client.create_datasource(data_source1)
        created2 = client.create_datasource(data_source2)
        result = client.get_datasources()
        assert isinstance(result, list)
        assert set(x.name for x in result) == {"sample-datasource", "another-sample"}

    @ResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_datasource(self, api_key, endpoint, index_name, **kwargs):
        client = SearchServiceClient(endpoint, AzureKeyCredential(api_key)).get_datasources_client()
        data_source = self._create_datasource()
        created = client.create_datasource(data_source)
        assert len(client.get_datasources()) == 1
        data_source.description = "updated"
        client.create_or_update_datasource(data_source)
        assert len(client.get_datasources()) == 1
        result = client.get_datasource("sample-datasource")
        assert result.name == "sample-datasource"
        assert result.description == "updated"

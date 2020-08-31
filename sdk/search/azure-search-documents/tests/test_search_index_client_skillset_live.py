# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from os.path import dirname, join, realpath

import pytest

from devtools_testutils import AzureMgmtTestCase
from azure_devtools.scenario_tests import ReplayableTest
from search_service_preparer import SearchServicePreparer, SearchResourceGroupPreparer

from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.search.documents.indexes.models import(
    EntityRecognitionSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
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

class SearchSkillsetClientTest(AzureMgmtTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['api-key']

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))

        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc")

        result = client.create_skillset(skillset)
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

        assert len(client.get_skillsets()) == 1

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc")

        result = client.create_skillset(skillset)
        assert len(client.get_skillsets()) == 1

        client.delete_skillset("test-ss")
        assert len(client.get_skillsets()) == 0

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_delete_skillset_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc")

        result = client.create_skillset(skillset)
        etag = result.e_tag

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="updated")
        updated = client.create_or_update_skillset(skillset)
        updated.e_tag = etag

        with pytest.raises(HttpResponseError):
            client.delete_skillset(updated, match_condition=MatchConditions.IfNotModified)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc")
        client.create_skillset(skillset)
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc"
        assert result.e_tag
        assert len(result.skills) == 1
        assert isinstance(result.skills[0], EntityRecognitionSkill)

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_get_skillsets(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss-1', skills=list([s]), description="desc1")
        client.create_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name='test-ss-2', skills=list([s]), description="desc2")
        client.create_skillset(skillset2)
        result = client.get_skillsets()
        assert isinstance(result, list)
        assert all(isinstance(x, SearchIndexerSkillset) for x in result)
        assert set(x.name for x in result) == {"test-ss-1", "test-ss-2"}

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc1")
        client.create_or_update_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc2")
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset_inplace(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc1")
        ss = client.create_or_update_skillset(skillset1)
        skillset2 = SearchIndexerSkillset(name='test-ss', skills=[s], description="desc2", skillset=ss)
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == 1

        result = client.get_skillset("test-ss")
        assert isinstance(result, SearchIndexerSkillset)
        assert result.name == "test-ss"
        assert result.description == "desc2"

    @SearchResourceGroupPreparer(random_name_enabled=True)
    @SearchServicePreparer(schema=SCHEMA, index_batch=BATCH)
    def test_create_or_update_skillset_if_unchanged(self, api_key, endpoint, index_name, **kwargs):
        client = SearchIndexerClient(endpoint, AzureKeyCredential(api_key))
        s = EntityRecognitionSkill(inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                                   outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")])

        skillset1 = SearchIndexerSkillset(name='test-ss', skills=list([s]), description="desc1")
        ss = client.create_or_update_skillset(skillset1)
        etag = ss.e_tag
        skillset2 = SearchIndexerSkillset(name='test-ss', skills=[s], description="desc2", skillset=ss)
        client.create_or_update_skillset(skillset2)
        assert len(client.get_skillsets()) == 1

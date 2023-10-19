import random
import string
import pytest

from azure.ai.generative import AIClient
from azure.ai.generative.entities.mlindex import MLIndex

test_mlindex_properties = {
    "azureml.mlIndexAssetKind": "acs",
    "azureml.mlIndexAsset": "true",
    "azureml.mlIndexAssetSource": "AzureML Data",
    "azureml.mlIndexAssetPipelineRunId": "Local",
}

@pytest.mark.e2etest
class TestBasic:
    def test_basic(self, ai_client: AIClient):
        index_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        mlindex = MLIndex(name=index_name, path="./tests/test_data/test_mlindex/", version="1", properties=test_mlindex_properties)
        index = ai_client.mlindexes.create_or_update(mlindex)
        return_index = ai_client.mlindexes.get(index_name, version="1")
        assert index.name == index_name
        assert return_index.name == index_name

    def test_passes_with_name_version_override(self, ai_client: AIClient):
        index_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        mlindex = MLIndex(name=index_name, path="./tests/test_data/test_mlindex/", version="1", properties=test_mlindex_properties)
        index_name_modified = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        index = ai_client.mlindexes.create_or_update(mlindex, name=index_name_modified, version="2")
        return_index = ai_client.mlindexes.get(index_name_modified, version="2")
        assert index.name == index_name_modified
        assert return_index.name == index_name_modified

    def test_passes_with_version(self, ai_client: AIClient):
        index_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        mlindex = MLIndex(name=index_name, path="./tests/test_data/test_mlindex/", version="1", properties=test_mlindex_properties)
        ai_client.mlindexes.create_or_update(mlindex, name=index_name, version="2", description="test")
        return_index = ai_client.mlindexes.get(index_name, version="2")
        assert return_index.name == index_name

    def test_passes_with_label(self, ai_client: AIClient):
        index_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        mlindex = MLIndex(name=index_name, path="./tests/test_data/test_mlindex/", version="1", properties=test_mlindex_properties)
        ai_client.mlindexes.create_or_update(mlindex, name=index_name, version="2", description="test")
        ai_client.mlindexes.create_or_update(mlindex, name=index_name, version="99", description="test")
        return_index = ai_client.mlindexes.get(index_name, label="latest")
        assert return_index.name == index_name and return_index.version == "99"

import random
import string
import pytest

from azure.ai.generative import AIClient
from azure.ai.generative.entities.data import Data

@pytest.mark.e2etest
class TestBasic:
    def test_create_new_dataset(self, ai_client: AIClient):
        dataset_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        dataset = Data(name=dataset_name, path="./test_data/test_dataset/", version="1", type="uri_folder")
        created_dataset = ai_client.data.create_or_update(dataset)
        returned_dataset = ai_client.data.get(dataset_name, version="1")
        assert created_dataset.name == dataset_name
        assert returned_dataset.name == dataset_name

    def test_create_with_version(self, ai_client: AIClient):
        dataset_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        dataset = Data(name=dataset_name, path="./test_data/test_dataset/", version="1")
        ai_client.data.create_or_update(dataset, name=dataset_name, version="2", description="test")
        returned_dataset = ai_client.data.get(dataset_name, version="2")
        assert returned_dataset.name == dataset_name

    def test_create_with_label(self, ai_client: AIClient):
        dataset_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        dataset = Data(name=dataset_name, path="./test_data/test_dataset/", version="1")
        ai_client.data.create_or_update(dataset, name=dataset_name, version="2", description="test")
        ai_client.data.create_or_update(dataset, name=dataset_name, version="99", description="test")
        returned_dataset = ai_client.data.get(dataset_name, label="latest")
        assert returned_dataset.name == dataset_name and returned_dataset.version == "99"

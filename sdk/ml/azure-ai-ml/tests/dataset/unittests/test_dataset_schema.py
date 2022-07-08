from azure.ai.ml.entities._assets import Dataset
from marshmallow.exceptions import ValidationError
import pytest
import yaml


@pytest.mark.unittest
class TestDataset:
    def test_deserialize_folder(self):
        test_path = "./tests/test_configs/dataset/dataset_folder_test.yml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            dataset: Dataset = Dataset.load(path=test_path)
        assert dataset.name == target["name"]
        source = dataset._to_rest_object()
        assert source.properties.paths[0].folder == target["paths"][0]["folder"]
        assert not source.properties.paths[0].file

    def test_deserialize_file(self):
        test_path = "./tests/test_configs/dataset/dataset_file_test.yml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            dataset: Dataset = Dataset.load(path=test_path)
        assert dataset.name == target["name"]
        source = dataset._to_rest_object()
        assert source.properties.paths[0].file == target["paths"][0]["file"]
        assert not source.properties.paths[0].folder

    def test_deserialize_no_paths_and_local_path_should_get_validation_error(self):
        test_path = "./tests/test_configs/dataset/dataset_no_paths_and_local_path_test.yml"
        with open(test_path, "r") as f:
            yaml.safe_load(f)
        with open(test_path, "r"):
            with pytest.raises(Exception) as e:
                dataset = Dataset.load(path=test_path)
                dataset._validate()

        assert "Either paths or local_path need to be provided." in str(e)

    def test_deserialize_empty_paths_should_get_validation_error(self):
        test_path = "./tests/test_configs/dataset/dataset_empty_paths_test.yml"
        with open(test_path, "r") as f:
            yaml.safe_load(f)
        with open(test_path, "r"):
            with pytest.raises(ValidationError) as e:
                Dataset.load(path=test_path)
        assert "Please provide one folder path or one file path" in e.value.messages[0]

    def test_deserialize_with_folder_and_file_validation_error(self):
        test_path = "./tests/test_configs/dataset/dataset_with_file_and_folder.yml"
        with open(test_path, "r") as f:
            yaml.safe_load(f)
        with open(test_path, "r"):
            with pytest.raises(ValidationError) as e:
                Dataset.load(path=test_path)
        assert "Please provide only one folder or one file" in e.value.messages[0]

    def test_deserialize_whitespace_folder_validation_error(self):
        test_path = "./tests/test_configs/dataset/dataset_whitespace_folder_test.yml"
        with open(test_path, "r") as f:
            yaml.safe_load(f)
        with open(test_path, "r"):
            with pytest.raises(ValidationError) as e:
                Dataset.load(path=test_path)
        assert "Please provide valid path for one folder, whitespace is not allowed" in e.value.messages[0]

    def test_deserialize_whitespace_file_validation_error(self):
        test_path = "./tests/test_configs/dataset/dataset_whitespace_file_test.yml"
        with open(test_path, "r") as f:
            yaml.safe_load(f)
        with open(test_path, "r"):
            with pytest.raises(ValidationError) as e:
                Dataset.load(path=test_path)
        assert "Please provide valid path for one file, whitespace is not allowed" in e.value.messages[0]

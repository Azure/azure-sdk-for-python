import os
from pathlib import Path
from azure.ai.ml.entities._assets import Data
from marshmallow.exceptions import ValidationError
import pytest
import yaml
from azure.ai.ml import load_data


@pytest.mark.unittest
class TestData:
    def test_deserialize_file(self):
        test_path = "./tests/test_configs/dataset/data_file.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            data: Data = load_data(path=test_path)
        assert data.name == target["name"]
        source = data._to_rest_object()
        assert os.path.normpath(source.properties.data_uri) == os.path.normpath(
            Path(Path(test_path).parent, target["path"]).resolve()
        )
        assert source.properties.data_type == "uri_file"

    def test_deserialize_folder(self):
        test_path = "./tests/test_configs/dataset/data_local_path.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            data: Data = load_data(path=test_path)
        assert data.name == target["name"]
        source = data._to_rest_object()
        assert os.path.normpath(source.properties.data_uri) == os.path.normpath(
            Path(Path(test_path).parent, target["path"]).resolve()
        )
        assert source.properties.data_type == "uri_folder"

    def test_deserialize_mltable(self):
        test_path = "./tests/test_configs/dataset/data_local_path_mltable.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            dataset: Data = load_data(path=test_path)
        assert dataset.name == target["name"]
        source = dataset._to_rest_object()
        assert os.path.normpath(source.properties.data_uri) == os.path.normpath(
            Path(Path(test_path).parent, target["path"]).resolve()
        )
        assert source.properties.data_type == "mltable"

    def test_deserialize_empty_paths_should_get_validation_error(self):
        test_path = "./tests/test_configs/dataset/data_missing_path_test.yml"
        with open(test_path, "r") as f:
            yaml.safe_load(f)
        with open(test_path, "r"):
            with pytest.raises(ValidationError) as e:
                load_data(path=test_path)
        assert "Missing data for required field" in e.value.messages[0]

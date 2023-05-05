import os
from pathlib import Path

import pytest
import yaml
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_data
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities._assets.auto_delete_setting import AutoDeleteSetting, AutoDeleteCondition


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestData:
    def test_deserialize_file(self):
        test_path = "./tests/test_configs/dataset/data_file.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            data: Data = load_data(source=test_path)
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
            data: Data = load_data(source=test_path)
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
            dataset: Data = load_data(source=test_path)
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
                load_data(source=test_path)
        assert "Missing data for required field" in e.value.messages[0]

    def test_asset_eq(self):
        auto_delete_setting = AutoDeleteSetting(condition=AutoDeleteCondition.CREATED_GREATER_THAN, value="30d")
        # with auto delete setting
        targetAsset = Data(
            name="testDataAssetfolder",
            version="1",
            description="this is a test data asset with auto delete setting",
            path="azureml://datastores/workspacemanageddatastore/",
            auto_delete_setting=auto_delete_setting,
        )
        test_path = "./tests/test_configs/dataset/data_with_auto_delete_setting.yml"
        with open(test_path, "r") as f:
            asset: Data = load_data(source=test_path)

            # the path types are different in load_data and raw Data
            targetAsset._base_path = asset.base_path
            assert Asset.__eq__(asset, targetAsset) is True

        # without auto delete setting
        targetAsset = Data(
            name="testDataAssetfolder",
            version="1",
            description="this is a test data asset without auto delete setting",
            path="azureml://datastores/workspacemanageddatastore/",
            auto_delete_setting=auto_delete_setting,
        )
        test_path = "./tests/test_configs/dataset/data_without_auto_delete_setting.yml"
        with open(test_path, "r") as f:
            asset: Data = load_data(source=test_path)

            # the path types are different in load_data and raw Data
            targetAsset._base_path = asset.base_path
            assert Asset.__eq__(asset, targetAsset) is False

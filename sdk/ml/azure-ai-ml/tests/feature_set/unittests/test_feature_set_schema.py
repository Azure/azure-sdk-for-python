# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import yaml

from azure.ai.ml.entities._assets._artifacts.feature_set import FeatureSet
from azure.ai.ml.entities._load_functions import load_feature_set


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureSetSchema:
    def test_feature_set_load(self) -> None:
        test_path = "./tests/test_configs/feature_set/feature_set_full.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            featureset: FeatureSet = load_feature_set(source=test_path)
        assert featureset.name == target["name"]
        assert featureset.version == target["version"]
        assert featureset.description == target["description"]
        assert featureset.entities is not None
        assert featureset.specification is not None
        assert featureset.specification.path is not None
        assert featureset.tags is not None
        assert featureset.properties is not None

    def test_feature_set_load_minimal_with_mat(self) -> None:
        test_path = "./tests/test_configs/feature_set/feature_set_minimal.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            featureset: FeatureSet = load_feature_set(source=test_path)
        assert featureset.name == target["name"]
        assert featureset.version == target["version"]
        assert featureset.entities is not None
        assert featureset.specification is not None
        assert featureset.specification.path is not None
        assert featureset.stage is not None
        assert featureset.properties is not None
        assert featureset.materialization_settings is not None
        assert featureset.materialization_settings.spark_configuration is not None
        assert featureset.materialization_settings.offline_enabled is None

    def test_feature_set_load_and_dump(self) -> None:
        import os
        import uuid
        from pathlib import Path
        from tempfile import gettempdir

        # test from yaml
        feature_set_path = "./tests/test_configs/feature_set/sample_feature_set/feature_set_asset.yaml"
        loaded_fs = load_feature_set(source=feature_set_path)
        temp_folder = uuid.uuid4().hex
        temp_folder = os.path.join(gettempdir(), temp_folder)
        os.makedirs(temp_folder)
        dump_path = os.path.join(temp_folder, "feature_set_asset.yaml")
        loaded_fs.dump(dest=dump_path)
        dumped_fs = load_feature_set(source=dump_path)
        assert loaded_fs._to_dict() == dumped_fs._to_dict()

        # test from constructor
        from azure.ai.ml.entities._feature_set.feature_set_specification import FeatureSetSpecification

        fs = FeatureSet(
            name="transactions",
            version="1",
            description="7-day and 3-day rolling aggregation of transactions featureset",
            entities=["azureml:account:1"],
            stage="Development",
            specification=FeatureSetSpecification(path="./tests/test_configs/feature_set/sample_feature_set/spec"),
            tags={"data_type": "nonPII"},
        )
        temp_folder = uuid.uuid4().hex
        temp_folder = os.path.join(gettempdir(), temp_folder)
        os.makedirs(temp_folder)
        dump_path = os.path.join(temp_folder, "feature_set_asset.yaml")
        fs.dump(dest=dump_path)
        with pytest.raises(FileExistsError):
            fs.dump(dest=dump_path)

        dumped_fs = load_feature_set(source=dump_path)

        assert fs.name == dumped_fs.name
        assert fs.version == dumped_fs.version
        assert fs.description == dumped_fs.description
        assert fs.specification.path == "./tests/test_configs/feature_set/sample_feature_set/spec"
        assert dumped_fs.entities is not None
        assert dumped_fs.specification is not None
        assert dumped_fs.specification.path == str(Path(".", "spec"))

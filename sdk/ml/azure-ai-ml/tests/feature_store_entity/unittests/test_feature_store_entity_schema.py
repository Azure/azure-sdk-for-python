# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
import pytest

from azure.ai.ml.entities._feature_store_entity.feature_store_entity import FeatureStoreEntity

from azure.ai.ml.entities._load_functions import load_feature_store_entity


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureStoreEntitySchema:
    def test_feature_store_entity_load(self) -> None:
        test_path = "./tests/test_configs/feature_store_entity/feature_store_entity_full.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            feature_store_entity: FeatureStoreEntity = load_feature_store_entity(source=test_path)
        assert feature_store_entity.name == target["name"]
        assert feature_store_entity.version == target["version"]
        assert feature_store_entity.description == target["description"]
        assert feature_store_entity.index_columns is not None
        assert feature_store_entity.tags is not None
        assert feature_store_entity.properties is not None

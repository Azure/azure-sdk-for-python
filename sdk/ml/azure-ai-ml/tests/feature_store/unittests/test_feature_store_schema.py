# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
import pytest


from azure.ai.ml.entities._feature_store.feature_store import FeatureStore
from azure.ai.ml.entities._load_functions import load_feature_store


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureStoreSchema:
    def test_feature_store_load(self) -> None:
        test_path = "./tests/test_configs/feature_store/feature_store_full.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            feature_store: FeatureStore = load_feature_store(source=test_path)
        assert feature_store.name == target["name"]
        assert feature_store.description == target["description"]
        assert feature_store.materialization_identity is not None
        assert feature_store.offline_store is not None
        assert feature_store.tags is not None
        assert feature_store.properties is not None

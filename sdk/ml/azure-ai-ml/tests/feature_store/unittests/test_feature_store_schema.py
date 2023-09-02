# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import yaml

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
        assert feature_store.managed_network is not None
        assert feature_store.managed_network.outbound_rules is not None

    def test_materialization_store(self):
        from azure.ai.ml.entities._feature_store._constants import (
            OFFLINE_MATERIALIZATION_STORE_TYPE,
            ONLINE_MATERIALIZATION_STORE_TYPE,
        )
        from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore
        from azure.ai.ml.exceptions import ValidationException

        with pytest.raises(ValidationException) as ve:
            FeatureStore(
                name="name",
                description="description",
                offline_store=MaterializationStore(
                    type=OFFLINE_MATERIALIZATION_STORE_TYPE, target="offline_store_resource_id"
                ),
            )
        assert "Invalid ARM Id" in str(ve.exception)

        with pytest.raises(ValidationException) as ve:
            FeatureStore(
                name="name",
                description="description",
                online_store=MaterializationStore(
                    type=ONLINE_MATERIALIZATION_STORE_TYPE, target="online_store_resource_id"
                ),
            )
        assert "Invalid ARM Id" in str(ve.exception)

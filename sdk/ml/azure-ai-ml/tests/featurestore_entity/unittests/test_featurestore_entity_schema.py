# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
import pytest

from azure.ai.ml.entities._featurestore_entity.featurestore_entity import FeaturestoreEntity

from azure.ai.ml import load_featurestore_entity


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeaturestoreEntitySchema:
    def test_featurestore_entity_load(self) -> None:
        test_path = "./tests/test_configs/featurestore_entity/featurestore_entity_full.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            featurestore_entity: FeaturestoreEntity = load_featurestore_entity(source=test_path)
        assert featurestore_entity.name == target["name"]
        assert featurestore_entity.version == target["version"]
        assert featurestore_entity.description == target["description"]
        assert featurestore_entity.index_columns is not None
        assert featurestore_entity.tags is not None
        assert featurestore_entity.properties is not None

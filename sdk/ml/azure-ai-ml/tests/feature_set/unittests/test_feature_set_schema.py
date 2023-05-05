# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
import pytest

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

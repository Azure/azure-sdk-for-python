# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
import pytest

from azure.ai.ml.entities._assets._artifacts.featureset import Featureset
from azure.ai.ml import load_featureset


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeaturesetSchema:
    def test_featureset_load(self) -> None:
        test_path = "./tests/test_configs/featureset/featureset_full.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            featureset: Featureset = load_featureset(source=test_path)
        assert featureset.name == target["name"]
        assert featureset.version == target["version"]
        assert featureset.description == target["description"]
        assert featureset.entities is not None
        assert featureset.specification is not None
        assert featureset.specification.path is not None
        assert featureset.tags is not None
        assert featureset.properties is not None

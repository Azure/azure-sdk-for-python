# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import yaml

from azure.ai.ml.entities._feature_set.feature_set_backfill_request import FeatureSetBackfillRequest
from azure.ai.ml.entities._load_functions import load_feature_set_backfill_request


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureSetBackfillRequestSchema:
    def test_feature_set_backfill_request_load(self) -> None:
        test_path = "./tests/test_configs/feature_set/feature_set_backfill_request.yml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            backfill_request: FeatureSetBackfillRequest = load_feature_set_backfill_request(source=test_path)
        assert backfill_request.name == target["name"]
        assert backfill_request.version == target["version"]
        assert backfill_request.description == target["description"]
        assert backfill_request.data_status == target["data_status"]
        assert backfill_request.job_id == target["job_id"]
        assert backfill_request.tags is not None
        assert backfill_request.resource is not None
        assert backfill_request.spark_configuration is not None
        assert backfill_request.feature_window is not None

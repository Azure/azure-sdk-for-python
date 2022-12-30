# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.ml import UserIdentityConfiguration
from azure.ai.ml._restclient.v2022_10_01_preview.models import MLTableJobInput
from azure.ai.ml._restclient.v2022_10_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml.automl import RegressionModels, RegressionPrimaryMetrics, regression
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.tabular import RegressionJob


@pytest.mark.automl_test
@pytest.mark.unittest
class TestAutoMLRegression:
    def test_regression_task(self):
        # Create AutoML Regression Task
        identity = UserIdentityConfiguration()
        regression_job = regression(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            primary_metric="spearman_correlation",
            enable_model_explainability=True,
            test_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/test.csv"),
            validation_data_size=0.2,
            # Job attributes
            compute="cluster-regression",
            name="regression_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            identity=identity,
        )  # type: RegressionJob
        regression_job.set_limits(timeout_minutes=60, max_trials=100, max_concurrent_trials=4)
        regression_job.set_training(
            enable_onnx_compatible_models=True, blocked_training_algorithms=[RegressionModels.RANDOM_FOREST]
        )
        regression_job.set_featurization(enable_dnn_featurization=True)
        regression_job.training.allowed_training_algorithms = [
            RegressionModels.RANDOM_FOREST,
            RegressionModels.LIGHT_GBM,
        ]

        # check the rest object
        rest_obj = regression_job._to_rest_object()  # serialize to rest object
        assert isinstance(rest_obj.properties.identity, RestUserIdentity)
        assert isinstance(
            rest_obj.properties.task_details.training_data, MLTableJobInput
        ), "Training data is not MLTableJobInput"
        assert isinstance(
            rest_obj.properties.task_details.test_data, MLTableJobInput
        ), "Test data is not MLTableJobInput"

        original_obj = RegressionJob._from_rest_object(rest_obj)  # deserialize from rest object
        assert regression_job == original_obj, "Conversion to/from rest object failed"
        assert (
            original_obj.primary_metric == RegressionPrimaryMetrics.SPEARMAN_CORRELATION
        ), "Primary metric is not correct"
        assert original_obj.compute == "cluster-regression", "Compute not set correctly"
        assert original_obj.name == "regression_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        # check if the original job inputs were restored
        assert isinstance(original_obj.training_data, Input), "Training data is not Input"
        assert original_obj.training_data.type == AssetTypes.MLTABLE, "Training data type not set correctly"
        assert original_obj.identity == identity
        assert original_obj.training_data.path == "https://foo/bar/train.csv", "Training data path not set correctly"
        assert isinstance(original_obj.test_data, Input), "Training data is not Input"
        assert original_obj.test_data.type == AssetTypes.MLTABLE, "Test data type not set correctly"
        assert original_obj.test_data.path == "https://foo/bar/test.csv", "Test data path not set correctly"
        assert original_obj.training.allowed_training_algorithms == [
            RegressionModels.RANDOM_FOREST,
            RegressionModels.LIGHT_GBM,
        ], "Allowed models not set correctly"

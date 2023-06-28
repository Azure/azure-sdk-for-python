# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Tuple

import pytest

from azure.ai.ml import UserIdentityConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import CustomNCrossValidations, MLTableJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml.automl import ClassificationModels, ClassificationPrimaryMetrics, classification
from azure.ai.ml.constants import TabularTrainingMode
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.tabular import ClassificationJob


@pytest.mark.automl_test
@pytest.mark.unittest
class TestAutoMLClassification:
    def test_classification_task(self):
        # Create AutoML Classification Task
        identity = UserIdentityConfiguration()
        classification_job = classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            positive_label="label",
            enable_model_explainability=True,
            test_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/test.csv"),
            validation_data_size=0.2,
            # Job attributes
            compute="cpucluster",
            name="classifier_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"_automl_internal_some_flag": True},
            identity=identity,
        )  # type: ClassificationJob
        # classification_task.set_limits(timeout=60, max_trials=100, max_concurrent_trials=4)
        classification_job.limits = {"timeout_minutes": 60, "max_trials": 100, "max_concurrent_trials": 4}
        classification_job.set_training(
            enable_onnx_compatible_models=True, blocked_training_algorithms=[ClassificationModels.LOGISTIC_REGRESSION]
        )
        classification_job.set_featurization(enable_dnn_featurization=True)

        rest_obj = classification_job._to_rest_object()
        assert isinstance(rest_obj.properties.identity, RestUserIdentity)
        assert isinstance(
            rest_obj.properties.task_details.training_data, MLTableJobInput
        ), "Training data is not MLTableJobInput"
        assert isinstance(
            rest_obj.properties.task_details.test_data, MLTableJobInput
        ), "Test data is not MLTableJobInput"

        original_obj = ClassificationJob._from_rest_object(rest_obj)
        assert classification_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.compute == "cpucluster", "Compute not set correctly"
        assert original_obj.name == "classifier_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        assert original_obj.properties == {"_automl_internal_some_flag": True}, "Properties not set correctly"
        assert original_obj.identity == identity
        # check if the original job inputs were restored
        assert original_obj.primary_metric == ClassificationPrimaryMetrics.ACCURACY, "Primary metric is not ACCURACY"
        assert original_obj.positive_label == "label", "Positive label is not label"
        assert isinstance(original_obj.training_data, Input), "Training data is not Input"
        assert original_obj.training_data.type == AssetTypes.MLTABLE, "Training data type not set correctly"
        assert original_obj.training_data.path == "https://foo/bar/train.csv", "Training data path not set correctly"
        assert isinstance(original_obj.test_data, Input), "Test data is not Input"
        assert original_obj.test_data.type == AssetTypes.MLTABLE, "Test data type not set correctly"
        assert original_obj.test_data.path == "https://foo/bar/test.csv", "Test data path not set correctly"
        assert original_obj.training.blocked_training_algorithms == [
            ClassificationModels.LOGISTIC_REGRESSION
        ], "Blocked models not set correctly"
        assert original_obj.training.training_mode == None, "Training mode not set correctly"
        assert original_obj.limits.max_nodes == None, "Max nodes not set correctly"

    def test_classification_task_distributed_mode(self):
        # Create AutoML Classification Task
        classification_job = classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            positive_label="label",
            enable_model_explainability=True,
            test_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/test.csv"),
            validation_data_size=0.2,
            # Job attributes
            compute="cpucluster",
            name="classifier_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"_automl_internal_some_flag": True},
        )  # type: ClassificationJob
        # classification_task.set_limits(timeout=60, max_trials=100, max_concurrent_trials=4)
        classification_job.limits = {
            "timeout_minutes": 60,
            "max_trials": 100,
            "max_concurrent_trials": 4,
            "max_nodes": 4,
        }
        classification_job.set_training(
            allowed_training_algorithms=[ClassificationModels.LIGHT_GBM],
            training_mode=TabularTrainingMode.DISTRIBUTED,
        )
        classification_job.set_featurization(enable_dnn_featurization=True)

        rest_obj = classification_job._to_rest_object()
        original_obj = ClassificationJob._from_rest_object(rest_obj)

        assert classification_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.training.allowed_training_algorithms == [
            ClassificationModels.LIGHT_GBM
        ], "Allowed models not set correctly"
        assert original_obj.training.training_mode == TabularTrainingMode.DISTRIBUTED, "Training mode not set correctly"
        assert original_obj.limits.max_nodes == 4, "Max nodes not set correctly"

    def test_classification_task_non_distributed_mode(self):
        # Create AutoML Classification Task
        classification_job = classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            positive_label="label",
            enable_model_explainability=True,
            test_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/test.csv"),
            validation_data_size=0.2,
            # Job attributes
            compute="cpucluster",
            name="classifier_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"_automl_internal_some_flag": True},
        )  # type: ClassificationJob
        # classification_task.set_limits(timeout=60, max_trials=100, max_concurrent_trials=4)
        classification_job.limits = {"timeout_minutes": 60, "max_trials": 100, "max_concurrent_trials": 4}
        classification_job.set_training(
            allowed_training_algorithms=[ClassificationModels.LIGHT_GBM],
            training_mode=TabularTrainingMode.NON_DISTRIBUTED,
        )
        classification_job.set_featurization(enable_dnn_featurization=True)

        rest_obj = classification_job._to_rest_object()
        original_obj = ClassificationJob._from_rest_object(rest_obj)

        assert classification_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.training.allowed_training_algorithms == [
            ClassificationModels.LIGHT_GBM
        ], "Allowed models not set correctly"
        assert (
            original_obj.training.training_mode == TabularTrainingMode.NON_DISTRIBUTED
        ), "Training mode not set correctly"
        assert original_obj.limits.max_nodes == None, "Max nodes not set correctly"

    def test_classification_task_auto_mode(self):
        # Create AutoML Classification Task
        classification_job = classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            positive_label="label",
            enable_model_explainability=True,
            test_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/test.csv"),
            validation_data_size=0.2,
            # Job attributes
            compute="cpucluster",
            name="classifier_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            properties={"_automl_internal_some_flag": True},
        )  # type: ClassificationJob
        # classification_task.set_limits(timeout=60, max_trials=100, max_concurrent_trials=4)
        classification_job.limits = {
            "timeout_minutes": 60,
            "max_trials": 100,
            "max_concurrent_trials": 4,
            "max_nodes": 4,
        }
        classification_job.set_training(
            allowed_training_algorithms=[ClassificationModels.LIGHT_GBM],
            training_mode=TabularTrainingMode.AUTO,
        )
        classification_job.set_featurization(enable_dnn_featurization=True)

        rest_obj = classification_job._to_rest_object()
        original_obj = ClassificationJob._from_rest_object(rest_obj)

        assert classification_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.training.allowed_training_algorithms == [
            ClassificationModels.LIGHT_GBM
        ], "Allowed models not set correctly"
        assert original_obj.training.training_mode == TabularTrainingMode.AUTO, "Training mode not set correctly"
        assert original_obj.limits.max_nodes == 4, "Max nodes not set correctly"

    @pytest.mark.parametrize(
        "n_cross_validations",
        [
            (5, CustomNCrossValidations(value=5)),
            (None, None),
        ],
    )
    def test_n_cross_validations_to_rest(self, n_cross_validations: Tuple[int, Any]):
        # Create AutoML Classification Task
        classification_job = classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
            n_cross_validations=n_cross_validations[0],
        )

        rest_obj = classification_job._to_rest_object()
        assert isinstance(
            rest_obj.properties.task_details.n_cross_validations,
            type(n_cross_validations[1]),
        ), "Validation data is not CustomNCrossValidations"
        if n_cross_validations[0] is not None:
            assert (
                rest_obj.properties.task_details.n_cross_validations.value == 5
            ), "N cross validations not set correctly"

    def test_training_settings_model_explainability(self):
        # Create AutoML Classification Task
        classification_job = classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="target",
        )
        rest_obj = classification_job._to_rest_object()
        # make sure by default enable_model_explainability is set to None
        assert classification_job.training.enable_model_explainability == None
        assert rest_obj.properties.task_details.training_settings.enable_model_explainability == None

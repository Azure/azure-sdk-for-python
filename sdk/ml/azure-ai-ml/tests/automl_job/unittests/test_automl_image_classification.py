# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.ml import UserIdentityConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ClassificationPrimaryMetrics,
    LearningRateScheduler,
    MLTableJobInput,
    SamplingAlgorithmType,
    StochasticOptimizer,
)
from azure.ai.ml.automl import image_classification
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl import SearchSpace
from azure.ai.ml.entities._job.automl.image import ImageClassificationJob, ImageModelSettingsClassification
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


@pytest.mark.automl_test
@pytest.mark.unittest
class TestAutoMLImageClassification:
    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_image_classification_task(self, run_type):
        identity = UserIdentityConfiguration()
        # Create AutoML Image Classification task
        image_classification_job = image_classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            primary_metric=ClassificationPrimaryMetrics.ACCURACY,
            validation_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/valid.csv"),
            # Job attributes
            compute="gpu_cluster",
            name="image_classifier_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            identity=identity,
        )  # type: ImageClassificationJob

        if run_type == "single":
            image_classification_job.set_limits(timeout_minutes=60)
        elif run_type == "sweep":
            image_classification_job.set_limits(timeout_minutes=60, max_concurrent_trials=4, max_trials=20)
        elif run_type == "automode":
            image_classification_job.set_limits(timeout_minutes=60, max_trials=2, max_concurrent_trials=1)

        # image_classification_job.training_parameters = {
        #     "checkpoint_frequency": 1,
        #     "early_stopping": True,
        #     "early_stopping_delay": 2,
        #     "early_stopping_patience": 2,
        #     "evaluation_frequency": 1,
        # }
        image_classification_job.set_training_parameters(
            checkpoint_frequency=1,
            early_stopping=True,
            early_stopping_delay=2,
            early_stopping_patience=2,
            evaluation_frequency=1,
        )

        if run_type == "sweep":
            """
            image_classification_job.search_space = [
                {
                    "model_name": Choice(['vitb16r224', 'vits16r224']),
                    "learning_rate": Uniform(0.001, 0.01),
                    "number_of_epochs": Choice([15, 30]),
                },
                {
                    "model_name": Choice(['seresnext', 'resnest50']),
                    "learning_rate": Uniform(0.001, 0.01),
                    "layers_to_freeze": Choice([0, 2]),
                },
            ]
            """
            search_sub_space_1 = SearchSpace(
                model_name=Choice(["vitb16r224", "vits16r224"]),
                learning_rate=Uniform(0.001, 0.01),
                number_of_epochs=Choice([15, 30]),
            )
            search_sub_space_2 = SearchSpace(
                model_name=Choice(["seresnext", "resnest50"]),
                learning_rate=Uniform(0.001, 0.01),
                layers_to_freeze=Choice([0, 2]),
            )
            image_classification_job.extend_search_space([search_sub_space_1, search_sub_space_2])

            early_termination_policy = BanditPolicy(evaluation_interval=10, slack_factor=0.2)
            # image_classification_job.sweep = {
            #     "max_concurrent_trials": 4,
            #     "max_trials": 20,
            #     "sampling_algorithm": SamplingAlgorithmType.GRID,
            #     "early_termination": early_termination_policy,
            # }
            image_classification_job.set_sweep(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                early_termination=early_termination_policy,
            )

        # check the rest object
        rest_obj = image_classification_job._to_rest_object()
        assert isinstance(rest_obj.properties.identity, RestUserIdentity)

        def _check_data_type(data, expected_type, expected_path, msg):
            if expected_type == MLTableJobInput:
                assert isinstance(data, MLTableJobInput), "{} data is not MLTableJobInput".format(msg)
            elif expected_type == Input:
                assert isinstance(data, Input), "{} data is not Input".format(msg)
                assert data.type == AssetTypes.MLTABLE, "{} data type not set correctly".format(msg)
                assert data.path == expected_path, "{} data path not set correctly".format(msg)

        _check_data_type(rest_obj.properties.task_details.training_data, MLTableJobInput, None, "Training")
        _check_data_type(rest_obj.properties.task_details.validation_data, MLTableJobInput, None, "Validation")

        original_obj = ImageClassificationJob._from_rest_object(rest_obj)
        assert image_classification_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.compute == "gpu_cluster", "Compute not set correctly"
        assert original_obj.name == "image_classifier_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        assert original_obj.identity == identity
        # check if the original job inputs were restored
        _check_data_type(original_obj.training_data, Input, "https://foo/bar/train.csv", "Training")
        _check_data_type(original_obj.validation_data, Input, "https://foo/bar/valid.csv", "Validation")

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (("adam", "warmup_cosine"), (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE)),
            (("Adam", "WarmupCosine"), (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE)),
            ((None, None), (None, None)),
        ],
        ids=["snake case", "camel case", "none values"],
    )
    def test_image_set_training_parameters_with_valid_values(self, settings, expected):
        image_classification_job = image_classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
        )  # type: ImageClassificationJob
        image_classification_job.set_training_parameters(
            optimizer=settings[0],
            learning_rate_scheduler=settings[1],
        )
        assert image_classification_job.training_parameters.optimizer == expected[0]
        assert image_classification_job.training_parameters.learning_rate_scheduler == expected[1]

    @pytest.mark.parametrize(
        "settings, expected",
        [(("adamW", None), pytest.raises(KeyError)), ((None, "Warmup_Cosine"), pytest.raises(KeyError))],
        ids=["optimizer_invalid", "learning_rate_scheduler_invalid"],
    )
    def test_image_set_training_parameters_with_invalid_values(self, settings, expected):
        with expected:
            image_classification_job = image_classification(
                training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
                target_column_name="label",
            )  # type: ImageClassificationJob
            image_classification_job.set_training_parameters(optimizer=settings[0], learning_rate_scheduler=settings[1])

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (("adam", "warmup_cosine"), (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE)),
            (
                ("Adam", "WarmupCosine"),
                (StochasticOptimizer.ADAM, LearningRateScheduler.WARMUP_COSINE),
            ),
            (
                (None, None),
                (None, None),
            ),
        ],
        ids=["snake case", "camel case", "none values"],
    )
    def test_image_set_training_parameters_with_settings_object(self, settings, expected):
        image_model_settings = ImageModelSettingsClassification(
            optimizer=settings[0], learning_rate_scheduler=settings[1]
        )

        image_classification_job = image_classification(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            training_parameters=image_model_settings,
        )  # type: ImageClassificationJob

        assert image_classification_job.training_parameters.optimizer == expected[0]
        assert image_classification_job.training_parameters.learning_rate_scheduler == expected[1]

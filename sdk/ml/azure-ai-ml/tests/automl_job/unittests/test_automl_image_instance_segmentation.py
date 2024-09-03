# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest

from azure.ai.ml import UserIdentityConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import UserIdentity as RestUserIdentity
from azure.ai.ml._restclient.v2023_04_01_preview.models import ValidationMetricType
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    InstanceSegmentationPrimaryMetrics,
    LearningRateScheduler,
    LogTrainingMetrics,
    LogValidationLoss,
    MLTableJobInput,
    ModelSize,
    SamplingAlgorithmType,
    StochasticOptimizer,
)
from azure.ai.ml.automl import image_instance_segmentation
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl import SearchSpace
from azure.ai.ml.entities._job.automl.image import ImageInstanceSegmentationJob, ImageModelSettingsObjectDetection
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


@pytest.mark.automl_test
@pytest.mark.unittest
class TestAutoMLImageInstanceSegmentation:
    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_image_instance_segmentation_task(self, run_type):
        # Create AutoML Image Object Detection task
        identity = UserIdentityConfiguration()
        image_instance_segmentation_job = image_instance_segmentation(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            primary_metric=InstanceSegmentationPrimaryMetrics.MEAN_AVERAGE_PRECISION,
            validation_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/valid.csv"),
            # Job attributes
            compute="gpu_cluster",
            name="image_instance_segmentation_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            identity=identity,
        )  # type: ImageInstanceSegmentationJob

        if run_type == "single":
            image_instance_segmentation_job.set_limits(timeout_minutes=60)
        elif run_type == "sweep":
            image_instance_segmentation_job.set_limits(timeout_minutes=60, max_concurrent_trials=4, max_trials=20)
        elif run_type == "automode":
            image_instance_segmentation_job.set_limits(timeout_minutes=60, max_trials=2, max_concurrent_trials=1)

        # image_instance_segmentation_job.training_parameters = {
        #     "checkpoint_frequency": 1,
        #     "early_stopping": True,
        #     "early_stopping_delay": 2,
        #     "early_stopping_patience": 2,
        #     "evaluation_frequency": 1,
        # }
        image_instance_segmentation_job.set_training_parameters(
            checkpoint_frequency=1,
            early_stopping=True,
            early_stopping_delay=2,
            early_stopping_patience=2,
            evaluation_frequency=1,
        )

        if run_type == "sweep":
            """
            image_instance_segmentation_job.search_space = [
                {
                    "model_name": 'maskrcnn_resnet50_fpn',
                    "learning_rate": Uniform(0.0001, 0.001),
                    "warmup_cosine_lr_warmup_epochs": Choice([0, 3]),
                    "optimizer": Choice(['sgd', 'adam', 'adamw']),
                    "min_size": Choice([600, 800]),
                },
            ]
            """
            search_sub_space = SearchSpace(
                model_name="maskrcnn_resnet50_fpn",
                learning_rate=Uniform(0.0001, 0.001),
                warmup_cosine_lr_warmup_epochs=Choice([0, 3]),
                optimizer=Choice(["sgd", "adam", "adamw"]),
                min_size=Choice([600, 800]),
            )
            image_instance_segmentation_job.extend_search_space(search_sub_space)

            early_termination_policy = BanditPolicy(evaluation_interval=10, slack_factor=0.2)
            # image_instance_segmentation_job.sweep = {
            #     "max_concurrent_trials": 4,
            #     "max_trials": 20,
            #     "sampling_algorithm": SamplingAlgorithmType.GRID,
            #     "early_termination": early_termination_policy,
            # }
            image_instance_segmentation_job.set_sweep(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                early_termination=early_termination_policy,
            )

        # check the rest object
        rest_obj = image_instance_segmentation_job._to_rest_object()
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

        original_obj = ImageInstanceSegmentationJob._from_rest_object(rest_obj)
        assert image_instance_segmentation_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.compute == "gpu_cluster", "Compute not set correctly"
        assert original_obj.identity == identity
        assert original_obj.name == "image_instance_segmentation_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        # check if the original job inputs were restored
        _check_data_type(original_obj.training_data, Input, "https://foo/bar/train.csv", "Training")
        _check_data_type(original_obj.validation_data, Input, "https://foo/bar/valid.csv", "Validation")

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (
                ("adam", "warmup_cosine", "coco_voc", "large", "enable", "enable"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                    LogTrainingMetrics.ENABLE,
                    LogValidationLoss.ENABLE,
                ),
            ),
            (
                ("Adam", "WarmupCosine", "CocoVoc", "Large", "Enable", "Enable"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                    LogTrainingMetrics.ENABLE,
                    LogValidationLoss.ENABLE,
                ),
            ),
            (
                (None, None, "coco_voc", "large", "enable", "enable"),
                (
                    None,
                    None,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                    LogTrainingMetrics.ENABLE,
                    LogValidationLoss.ENABLE,
                ),
            ),
        ],
        ids=["snake case", "camel case", "with None"],
    )
    def test_image_set_training_parameters_with_valid_values(self, settings, expected):
        image_instance_segmentation_job = image_instance_segmentation(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
        )
        image_instance_segmentation_job.set_training_parameters(
            optimizer=settings[0],
            learning_rate_scheduler=settings[1],
            validation_metric_type=settings[2],
            model_size=settings[3],
            log_training_metrics=settings[4],
            log_validation_loss=settings[5],
        )
        assert image_instance_segmentation_job.training_parameters.optimizer == expected[0]
        assert image_instance_segmentation_job.training_parameters.learning_rate_scheduler == expected[1]
        assert image_instance_segmentation_job.training_parameters.validation_metric_type == expected[2]
        assert image_instance_segmentation_job.training_parameters.model_size == expected[3]
        assert image_instance_segmentation_job.training_parameters.log_training_metrics == expected[4]
        assert image_instance_segmentation_job.training_parameters.log_validation_loss == expected[5]

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (("adamW", None, None, None, "Enable", "Enable"), pytest.raises(KeyError)),
            ((None, "Warmup_Cosine", None, None, "Enable", "Enable"), pytest.raises(KeyError)),
            ((None, None, "Coco_Voc", "large", "Enable", "Enable"), pytest.raises(KeyError)),
            ((None, None, None, "Extra_Large", "Enable", "Enable"), pytest.raises(KeyError)),
            ((None, None, None, None, "false", "Enable"), pytest.raises(KeyError)),
            ((None, None, None, None, "Enable", "false"), pytest.raises(KeyError)),
        ],
        ids=[
            "optimizer invalid",
            "learning rate scheduler invalid",
            "validation metric type invalid",
            "model size invalid",
            "log_training_metrics invalid",
            "log_validation_loss invalid",
        ],
    )
    def test_image_set_training_parameters_with_invalid_values(self, settings, expected):
        with expected:
            image_instance_segmentation_job = image_instance_segmentation(
                training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
                target_column_name="label",
            )  # type: ImageClassificationJob
            image_instance_segmentation_job.set_training_parameters(
                optimizer=settings[0],
                learning_rate_scheduler=settings[1],
                validation_metric_type=settings[2],
                model_size=settings[3],
                log_training_metrics=settings[4],
                log_validation_loss=settings[5],
            )

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (
                ("adam", "warmup_cosine", "coco_voc", "large", "enable", "enable"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                    LogTrainingMetrics.ENABLE,
                    LogValidationLoss.ENABLE,
                ),
            ),
            (
                ("Adam", "WarmupCosine", "CocoVoc", "Large", "Enable", "Enable"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                    LogTrainingMetrics.ENABLE,
                    LogValidationLoss.ENABLE,
                ),
            ),
            (
                (None, None, "coco_voc", "large", "enable", "enable"),
                (
                    None,
                    None,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                    LogTrainingMetrics.ENABLE,
                    LogValidationLoss.ENABLE,
                ),
            ),
        ],
        ids=["snake case", "camel case", "with None"],
    )
    def test_image_set_training_parameters_with_settings_object(self, settings, expected):
        image_model_settings = ImageModelSettingsObjectDetection(
            optimizer=settings[0],
            learning_rate_scheduler=settings[1],
            validation_metric_type=settings[2],
            model_size=settings[3],
            log_training_metrics=settings[4],
            log_validation_loss=settings[5],
        )
        image_instance_segmentation_job = image_instance_segmentation(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            training_parameters=image_model_settings,
        )

        assert image_instance_segmentation_job.training_parameters.optimizer == expected[0]
        assert image_instance_segmentation_job.training_parameters.learning_rate_scheduler == expected[1]
        assert image_instance_segmentation_job.training_parameters.validation_metric_type == expected[2]
        assert image_instance_segmentation_job.training_parameters.model_size == expected[3]
        assert image_instance_segmentation_job.training_parameters.log_training_metrics == expected[4]
        assert image_instance_segmentation_job.training_parameters.log_validation_loss == expected[5]

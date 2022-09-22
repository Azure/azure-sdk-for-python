# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    MLTableJobInput,
    ObjectDetectionPrimaryMetrics,
    SamplingAlgorithmType,
    UserIdentity,
    StochasticOptimizer,
    LearningRateScheduler,
    ModelSize,
    ValidationMetricType,
    ImageModelSettingsObjectDetection,
)
from azure.ai.ml.automl import image_object_detection
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.sweep import (
    BanditPolicy,
    Choice,
    Uniform,
)
from azure.ai.ml.entities._job.automl.image import (
    ImageObjectDetectionJob,
    ImageObjectDetectionSearchSpace,
)


@pytest.mark.unittest
class TestAutoMLImageObjectDetection:
    @pytest.mark.parametrize("run_type", ["single", "sweep", "automode"])
    def test_image_object_detection_task(self, run_type):
        # Create AutoML Image Object Detection task
        identity = UserIdentity()
        image_object_detection_job = image_object_detection(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            primary_metric=ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION,
            validation_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/valid.csv"),
            # Job attributes
            compute="gpu_cluster",
            name="image_object_detection_job",
            experiment_name="foo_exp",
            tags={"foo_tag": "bar"},
            identity=identity,
        )  # type: ImageObjectDetectionJob

        if (run_type == "single") or (run_type == "sweep"):
            # image_object_detection_job.limits = {"timeout": 60, "max_trials": 1, "max_concurrent_trials": 1}
            image_object_detection_job.set_limits(timeout_minutes=60)
        elif run_type == "automode":
            # image_object_detection_job.limits = {"timeout": 60, "max_trials": 2, "max_concurrent_trials": 1}
            image_object_detection_job.set_limits(timeout_minutes=60, max_trials=2, max_concurrent_trials=1)

        # image_object_detection_job.image_model = {
        #     "checkpoint_frequency": 1,
        #     "early_stopping": True,
        #     "early_stopping_delay": 2,
        #     "early_stopping_patience": 2,
        #     "evaluation_frequency": 1,
        # }
        image_object_detection_job.set_image_model(
            checkpoint_frequency=1,
            early_stopping=True,
            early_stopping_delay=2,
            early_stopping_patience=2,
            evaluation_frequency=1,
        )

        if run_type == "sweep":
            """
            image_object_detection_job.search_space = [
                {
                    "model_name": 'yolov5',
                    "learning_rate": Uniform(0.0001, 0.01),
                    "model_size": Choice(['small', 'medium']),
                },
                {
                    "model_name": 'fasterrcnn_resnet50_fpn',
                    "learning_rate": Uniform(0.0001, 0.01),
                    "optimizer": Choice(['sgd', 'adam', 'adamw']),
                    "min_size": Choice([600, 800]),
                },
            ]
            """
            search_sub_space_1 = ImageObjectDetectionSearchSpace(
                model_name="yolov5",
                learning_rate=Uniform(0.0001, 0.01),
                model_size=Choice(["small", "medium"]),
            )
            search_sub_space_2 = ImageObjectDetectionSearchSpace(
                model_name="fasterrcnn_resnet50_fpn",
                learning_rate=Uniform(0.0001, 0.01),
                optimizer=Choice(["sgd", "adam", "adamw"]),
                min_size=Choice([600, 800]),
            )
            image_object_detection_job.extend_search_space([search_sub_space_1, search_sub_space_2])

            early_termination_policy = BanditPolicy(evaluation_interval=10, slack_factor=0.2)
            # image_object_detection_job.sweep = {
            #     "max_concurrent_trials": 4,
            #     "max_trials": 20,
            #     "sampling_algorithm": SamplingAlgorithmType.GRID,
            #     "early_termination": early_termination_policy,
            # }
            image_object_detection_job.set_sweep(
                sampling_algorithm=SamplingAlgorithmType.GRID,
                max_concurrent_trials=4,
                max_trials=20,
                early_termination=early_termination_policy,
            )

        # check the rest object
        rest_obj = image_object_detection_job._to_rest_object()
        assert rest_obj.properties.identity == identity

        def _check_data_type(data, expected_type, expected_path, msg):
            if expected_type == MLTableJobInput:
                assert isinstance(data, MLTableJobInput), "{} data is not MLTableJobInput".format(msg)
            elif expected_type == Input:
                assert isinstance(data, Input), "{} data is not Input".format(msg)
                assert data.type == AssetTypes.MLTABLE, "{} data type not set correctly".format(msg)
                assert data.path == expected_path, "{} data path not set correctly".format(msg)

        _check_data_type(
            rest_obj.properties.task_details.data_settings.training_data.data, MLTableJobInput, None, "Training"
        )
        _check_data_type(
            rest_obj.properties.task_details.data_settings.validation_data.data, MLTableJobInput, None, "Validation"
        )

        original_obj = ImageObjectDetectionJob._from_rest_object(rest_obj)
        assert image_object_detection_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.compute == "gpu_cluster", "Compute not set correctly"
        assert original_obj.name == "image_object_detection_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        assert original_obj.identity == identity
        # check if the original job inputs were restored
        _check_data_type(original_obj._data.training_data.data, Input, "https://foo/bar/train.csv", "Training")
        _check_data_type(original_obj._data.validation_data.data, Input, "https://foo/bar/valid.csv", "Validation")

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (
                ("adam", "warmup_cosine", "coco_voc", "large"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                ),
            ),
            (
                ("Adam", "WarmupCosine", "CocoVoc", "Large"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                ),
            ),
            ((None, None, "coco_voc", "large"), (None, None, ValidationMetricType.COCO_VOC, ModelSize.LARGE)),
        ],
        ids=["snake case", "camel case", "with None"],
    )
    def test_set_image_model_with_valid_values(self, settings, expected):
        image_object_detection_job = image_object_detection(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
        )
        image_object_detection_job.set_image_model(
            optimizer=settings[0],
            learning_rate_scheduler=settings[1],
            validation_metric_type=settings[2],
            model_size=settings[3],
        )
        assert image_object_detection_job.image_model.optimizer == expected[0]
        assert image_object_detection_job.image_model.learning_rate_scheduler == expected[1]
        assert image_object_detection_job.image_model.validation_metric_type == expected[2]
        assert image_object_detection_job.image_model.model_size == expected[3]

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (("adamW", None, None, None), pytest.raises(KeyError)),
            ((None, "Warmup_Cosine", None, None), pytest.raises(KeyError)),
            ((None, None, "Coco_Voc", "large"), pytest.raises(KeyError)),
            ((None, None, None, "Extra_Large"), pytest.raises(KeyError)),
        ],
        ids=[
            "optimizer invalid",
            "learning rate scheduler invalid",
            "validation metric type invalid",
            "model size invalid",
        ],
    )
    def test_set_image_model_with_invalid_values(self, settings, expected):
        with expected:
            image_object_detection_job = image_object_detection(
                training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
                target_column_name="label",
            )  # type: ImageClassificationJob
            image_object_detection_job.set_image_model(
                optimizer=settings[0],
                learning_rate_scheduler=settings[1],
                validation_metric_type=settings[2],
                model_size=settings[3],
            )

    @pytest.mark.parametrize(
        "settings, expected",
        [
            (
                ("adam", "warmup_cosine", "coco_voc", "large"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                ),
            ),
            (
                ("Adam", "WarmupCosine", "CocoVoc", "Large"),
                (
                    StochasticOptimizer.ADAM,
                    LearningRateScheduler.WARMUP_COSINE,
                    ValidationMetricType.COCO_VOC,
                    ModelSize.LARGE,
                ),
            ),
            ((None, None, "coco_voc", "large"), (None, None, ValidationMetricType.COCO_VOC, ModelSize.LARGE)),
        ],
        ids=["snake case", "camel case", "with None"],
    )
    def test_set_image_model_with_settings_object(self, settings, expected):
        image_model_settings = ImageModelSettingsObjectDetection(
            optimizer=settings[0],
            learning_rate_scheduler=settings[1],
            validation_metric_type=settings[2],
            model_size=settings[3],
        )
        image_object_detection_job = image_object_detection(
            training_data=Input(type=AssetTypes.MLTABLE, path="https://foo/bar/train.csv"),
            target_column_name="label",
            image_model=image_model_settings,
        )
        assert image_object_detection_job.image_model.optimizer == expected[0]
        assert image_object_detection_job.image_model.learning_rate_scheduler == expected[1]
        assert image_object_detection_job.image_model.validation_metric_type == expected[2]
        assert image_object_detection_job.image_model.model_size == expected[3]

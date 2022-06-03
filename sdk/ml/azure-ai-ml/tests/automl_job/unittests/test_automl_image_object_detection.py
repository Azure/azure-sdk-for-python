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
    def test_image_object_detection_task(self):
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
            identity = identity,
        )  # type: ImageObjectDetectionJob

        # image_object_detection_job.limits = {"timeout": 60, "max_trials": 1, "max_concurrent_trials": 1}
        image_object_detection_job.set_limits(timeout_minutes=60)

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

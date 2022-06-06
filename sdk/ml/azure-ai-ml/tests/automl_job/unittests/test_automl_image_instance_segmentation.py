# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    MLTableJobInput,
    InstanceSegmentationPrimaryMetrics,
    SamplingAlgorithmType,
    UserIdentity,
)
from azure.ai.ml.automl import image_instance_segmentation
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.sweep import (
    BanditPolicy,
    Choice,
    Uniform,
)
from azure.ai.ml.entities._job.automl.image import (
    ImageInstanceSegmentationJob,
    ImageObjectDetectionSearchSpace,
)


@pytest.mark.unittest
class TestAutoMLImageInstanceSegmentation:
    def test_image_instance_segmentation_task(self):
        # Create AutoML Image Object Detection task
        identity = UserIdentity()
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
            identity = identity,
        )  # type: ImageInstanceSegmentationJob

        # image_instance_segmentation_job.limits = {"timeout": 60, "max_trials": 1, "max_concurrent_trials": 1}
        image_instance_segmentation_job.set_limits(timeout_minutes=60)

        early_termination_policy = BanditPolicy(evaluation_interval=10, slack_factor=0.2)
        # image_instance_segmentation_job.sweep = {
        #     "max_concurrent_trials": 4,
        #     "max_trials": 20,
        #     "sampling_algorithm": SamplingAlgorithmType.GRID,
        #     "early_termination": early_termination_policy,
        # }
        image_instance_segmentation_job.set_sweep(
            sampling_algorithm=SamplingAlgorithmType.GRID,
            max_concurrent_trials=4,
            max_trials=20,
            early_termination=early_termination_policy,
        )

        # image_instance_segmentation_job.image_model = {
        #     "checkpoint_frequency": 1,
        #     "early_stopping": True,
        #     "early_stopping_delay": 2,
        #     "early_stopping_patience": 2,
        #     "evaluation_frequency": 1,
        # }
        image_instance_segmentation_job.set_image_model(
            checkpoint_frequency=1,
            early_stopping=True,
            early_stopping_delay=2,
            early_stopping_patience=2,
            evaluation_frequency=1,
        )

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

        search_sub_space = ImageObjectDetectionSearchSpace(
            model_name="maskrcnn_resnet50_fpn",
            learning_rate=Uniform(0.0001, 0.001),
            warmup_cosine_lr_warmup_epochs=Choice([0, 3]),
            optimizer=Choice(["sgd", "adam", "adamw"]),
            min_size=Choice([600, 800]),
        )
        image_instance_segmentation_job.extend_search_space(search_sub_space)

        # check the rest object
        rest_obj = image_instance_segmentation_job._to_rest_object()
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

        original_obj = ImageInstanceSegmentationJob._from_rest_object(rest_obj)
        assert image_instance_segmentation_job == original_obj, "Conversion to/from rest object failed"
        assert original_obj.compute == "gpu_cluster", "Compute not set correctly"
        assert original_obj.identity == identity
        assert original_obj.name == "image_instance_segmentation_job", "Name not set correctly"
        assert original_obj.experiment_name == "foo_exp", "Experiment name not set correctly"
        assert original_obj.tags == {"foo_tag": "bar"}, "Tags not set correctly"
        # check if the original job inputs were restored
        _check_data_type(original_obj._data.training_data.data, Input, "https://foo/bar/train.csv", "Training")
        _check_data_type(original_obj._data.validation_data.data, Input, "https://foo/bar/valid.csv", "Validation")

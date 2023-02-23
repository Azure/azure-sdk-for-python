# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import platform
from typing import Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import assert_final_job_status, get_automl_job_properties

from azure.ai.ml import MLClient, automl
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import Data
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl import SearchSpace
from azure.ai.ml.entities._job.automl.image import ImageInstanceSegmentationJob, ImageObjectDetectionSearchSpace
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(
    condition=not is_live() or platform.python_implementation() == "PyPy",
    reason="Datasets downloaded by test are too large to record reliably",
)
class TestAutoMLImageSegmentation(AzureRecordedTestCase):
    def _create_jsonl_segmentation(self, client, train_path, val_path):
        fridge_data = Data(
            path="./odFridgeObjectsMask",
            type=AssetTypes.URI_FOLDER,
        )
        data_path_uri = client.data.create_or_update(fridge_data)

        import os

        train_annotations_file = os.path.join(train_path, "train_annotations.jsonl")
        validation_annotations_file = os.path.join(val_path, "validation_annotations.jsonl")

        self._update_jsonl_path(data_path_uri.path, train_annotations_file)
        self._update_jsonl_path(data_path_uri.path, validation_annotations_file)

    def _update_jsonl_path(self, remote_path, file_path):
        import json

        jsonl_file = open(file_path, "r")
        lines = jsonl_file.readlines()
        jsonl_file.close()

        data_path = "odFridgeObjectsMask/"

        with open(file_path, "w") as jsonl_file_write:
            for i in lines:
                json_line = eval(i)
                old_url = json_line["image_url"]
                result = old_url.find(data_path)

                # Update image url
                json_line["image_url"] = remote_path + old_url[result + len(data_path) :]
                jsonl_file_write.write(json.dumps(json_line) + "\n")

    def test_image_segmentation_run(self, image_segmentation_dataset: Tuple[Input, Input], client: MLClient) -> None:
        # Note: this test launches two jobs in order to avoid calling the dataset fixture more than once. Ideally, it
        # would have sufficed to mark the fixture with session scope, but pytest-xdist breaks this functionality:
        # https://github.com/pytest-dev/pytest-xdist/issues/271.

        # Get training and validation data
        train_path, val_path = image_segmentation_dataset

        # Create jsonl file
        self._create_jsonl_segmentation(client=client, train_path=train_path, val_path=val_path)

        training_data = Input(type=AssetTypes.MLTABLE, path=train_path)
        validation_data = Input(type=AssetTypes.MLTABLE, path=val_path)

        # Make generic segmentation job
        image_instance_segmentation_job = automl.image_instance_segmentation(
            compute="gpu-cluster",
            experiment_name="image-e2e-tests",
            training_data=training_data,
            validation_data=validation_data,
            target_column_name="label",
            primary_metric="MeanAveragePrecision",
            properties=get_automl_job_properties(),
        )

        # Configure regular sweep job
        image_instance_segmentation_job_sweep = copy.deepcopy(image_instance_segmentation_job)
        image_instance_segmentation_job_sweep.set_training_parameters(early_stopping=True, evaluation_frequency=1)
        image_instance_segmentation_job_sweep.extend_search_space(
            [
                SearchSpace(
                    model_name=Choice(["maskrcnn_resnet50_fpn"]),
                    learning_rate=Uniform(0.0001, 0.001),
                    optimizer=Choice(["sgd", "adam", "adamw"]),
                    min_size=Choice([600, 800]),
                ),
            ]
        )
        image_instance_segmentation_job_sweep.set_limits(max_trials=1, max_concurrent_trials=1)
        image_instance_segmentation_job_sweep.set_sweep(
            sampling_algorithm="Random",
            early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
        )

        # Configure AutoMode job
        image_instance_segmentation_job_automode = copy.deepcopy(image_instance_segmentation_job)
        # TODO: after shipping the AutoMode feature, do not set flag and call `set_limits()` instead of changing
        # the limits object directly.
        image_instance_segmentation_job_automode.properties["enable_automode"] = True
        image_instance_segmentation_job_automode.limits.max_trials = 2
        image_instance_segmentation_job_automode.limits.max_concurrent_trials = 2

        # Trigger regular sweep and then AutoMode job
        submitted_job_sweep = client.jobs.create_or_update(image_instance_segmentation_job_sweep)
        submitted_job_automode = client.jobs.create_or_update(image_instance_segmentation_job_automode)

        # Assert completion of regular sweep job
        assert_final_job_status(
            submitted_job_sweep, client, ImageInstanceSegmentationJob, JobStatus.COMPLETED, deadline=3600
        )

        # Assert completion of Automode job
        assert_final_job_status(
            submitted_job_automode, client, ImageInstanceSegmentationJob, JobStatus.COMPLETED, deadline=3600
        )

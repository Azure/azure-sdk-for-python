# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import json
import os
from typing import Tuple

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import assert_final_job_status, get_automl_job_properties

from azure.ai.ml import MLClient, automl
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.entities import Data
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl import SearchSpace
from azure.ai.ml.entities._job.automl.image import ImageClassificationJob, ImageClassificationSearchSpace
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestAutoMLImageClassification(AzureRecordedTestCase):
    def _create_jsonl_multiclass(self, client, train_path, val_path):
        src_images = "./fridgeObjects/"
        train_validation_ratio = 5

        # Path to the training and validation files
        train_annotations_file = os.path.join(train_path, "train_annotations.jsonl")
        validation_annotations_file = os.path.join(val_path, "validation_annotations.jsonl")

        fridge_data = Data(
            path="./fridgeObjects",
            type=AssetTypes.URI_FOLDER,
        )
        data_path_uri = client.data.create_or_update(fridge_data)

        # Baseline of json line dictionary
        json_line_sample = {
            "image_url": data_path_uri.path,
            "label": "",
        }

        index = 0
        # Scan each sub directary and generate a jsonl line per image, distributed on train and valid JSONL files
        with open(train_annotations_file, "w") as train_f:
            with open(validation_annotations_file, "w") as validation_f:
                for className in os.listdir(src_images):
                    subDir = src_images + className
                    if not os.path.isdir(subDir):
                        continue
                    # Scan each sub directary
                    print("Parsing " + subDir)
                    for image in os.listdir(subDir):
                        json_line = dict(json_line_sample)
                        json_line["image_url"] += f"{className}/{image}"
                        json_line["label"] = className

                        if index % train_validation_ratio == 0:
                            # validation annotation
                            validation_f.write(json.dumps(json_line) + "\n")
                        else:
                            # train annotation
                            train_f.write(json.dumps(json_line) + "\n")
                        index += 1

    def test_image_classification_multiclass_run(
        self, image_classification_dataset: Tuple[Input, Input], client: MLClient
    ) -> None:
        # Note: this test launches two jobs in order to avoid calling the dataset fixture more than once. Ideally, it
        # would have sufficed to mark the fixture with session scope, but pytest-xdist breaks this functionality:
        # https://github.com/pytest-dev/pytest-xdist/issues/271.

        # Get training and validation data paths
        train_path, val_path = image_classification_dataset

        # Create jsonl file
        self._create_jsonl_multiclass(client=client, train_path=train_path, val_path=val_path)

        training_data = Input(type=AssetTypes.MLTABLE, path=train_path)
        validation_data = Input(type=AssetTypes.MLTABLE, path=val_path)

        # Make generic classification job
        image_classification_job = automl.image_classification(
            training_data=training_data,
            target_column_name="label",
            validation_data=validation_data,
            primary_metric="accuracy",
            compute="gpu-cluster",
            experiment_name="image-e2e-tests",
            properties=get_automl_job_properties(),
        )

        # Configure regular sweep job
        image_classification_job_sweep = copy.deepcopy(image_classification_job)
        image_classification_job_sweep.set_training_parameters(early_stopping=True, evaluation_frequency=1)
        image_classification_job_sweep.extend_search_space(
            [
                SearchSpace(
                    model_name=Choice(["vitb16r224"]),
                    learning_rate=Uniform(0.001, 0.01),
                    number_of_epochs=Choice([15, 30]),
                ),
                SearchSpace(
                    model_name=Choice(["seresnext"]),
                    layers_to_freeze=Choice([0, 2]),
                ),
            ]
        )
        image_classification_job_sweep.set_limits(max_trials=1, max_concurrent_trials=1)
        image_classification_job_sweep.set_sweep(
            sampling_algorithm="Random",
            early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
        )

        # Configure AutoMode job
        image_classification_job_automode = copy.deepcopy(image_classification_job)
        # TODO: after shipping the AutoMode feature, do not set flag and call `set_limits()` instead of changing
        # the limits object directly.
        image_classification_job_automode.properties["enable_automode"] = True
        image_classification_job_automode.limits.max_trials = 2
        image_classification_job_automode.limits.max_concurrent_trials = 2

        # Trigger regular sweep and then AutoMode job
        submitted_job_sweep = client.jobs.create_or_update(image_classification_job_sweep)
        submitted_job_automode = client.jobs.create_or_update(image_classification_job_automode)

        # Assert completion of regular sweep job
        assert_final_job_status(submitted_job_sweep, client, ImageClassificationJob, JobStatus.COMPLETED, deadline=3600)

        # Assert completion of Automode job
        assert_final_job_status(
            submitted_job_automode, client, ImageClassificationJob, JobStatus.COMPLETED, deadline=3600
        )

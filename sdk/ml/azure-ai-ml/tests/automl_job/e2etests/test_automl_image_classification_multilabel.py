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
from azure.ai.ml.entities._job.automl.image import ImageClassificationMultilabelJob, ImageClassificationSearchSpace
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


@pytest.mark.automl_test
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_asset_name",
    "mock_code_hash",
)
@pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestAutoMLImageClassificationMultilabel(AzureRecordedTestCase):
    def _create_jsonl_multilabel(self, client: MLClient, train_path: str, val_path: str):
        src_images = "./multilabelFridgeObjects/"

        train_validation_ratio = 5

        # Path to the training and validation files
        train_annotations_file = os.path.join(train_path, "train_annotations.jsonl")
        validation_annotations_file = os.path.join(val_path, "validation_annotations.jsonl")

        multilabel_data = Data(path="./multilabelFridgeObjects", type=AssetTypes.URI_FOLDER)
        uri_folder_data_asset = client.data.create_or_update(multilabel_data)

        # Baseline of json line dictionary
        json_line_sample = {
            "image_url": uri_folder_data_asset.path,
            "label": [],
        }

        # Path to the labels file.
        labelFile = os.path.join(src_images, "labels.csv")

        # Read each annotation and convert it to jsonl line
        with open(train_annotations_file, "w") as train_f:
            with open(validation_annotations_file, "w") as validation_f:
                with open(labelFile, "r") as labels:
                    for i, line in enumerate(labels):
                        # Skipping the title line and any empty lines.
                        if i == 0 or len(line.strip()) == 0:
                            continue
                        line_split = line.strip().split(",")
                        if len(line_split) != 2:
                            print("Skipping the invalid line: {}".format(line))
                            continue
                        json_line = dict(json_line_sample)
                        json_line["image_url"] += f"images/{line_split[0]}"
                        json_line["label"] = line_split[1].strip().split(" ")

                        if i % train_validation_ratio == 0:
                            # validation annotation
                            validation_f.write(json.dumps(json_line) + "\n")
                        else:
                            # train annotation
                            train_f.write(json.dumps(json_line) + "\n")

    @pytest.mark.parametrize("components", [(False), (True)])
    def test_image_classification_multilabel_run(
        self,
        image_classification_multilabel_dataset: Tuple[Input, Input],
        client: MLClient,
        components: bool,
    ) -> None:
        # Note: this test launches two jobs in order to avoid calling the dataset fixture more than once. Ideally, it
        # would have sufficed to mark the fixture with session scope, but pytest-xdist breaks this functionality:
        # https://github.com/pytest-dev/pytest-xdist/issues/271.

        # Get training and validation data paths
        train_path, val_path = image_classification_multilabel_dataset

        # Create jsonl file
        self._create_jsonl_multilabel(client=client, train_path=train_path, val_path=val_path)

        training_data = Input(type=AssetTypes.MLTABLE, path=train_path)
        validation_data = Input(type=AssetTypes.MLTABLE, path=val_path)

        # Make generic multilabel classification job
        image_classification_multilabel_job = automl.image_classification_multilabel(
            compute="gpu-cluster",
            experiment_name="image-e2e-tests",
            training_data=training_data,
            validation_data=validation_data,
            target_column_name="label",
            primary_metric="iou",
            # These are temporal properties needed in Private Preview
            properties=get_automl_job_properties(),
        )

        # Configure sweep job
        image_classification_multilabel_job_sweep = copy.deepcopy(image_classification_multilabel_job)
        image_classification_multilabel_job_sweep.set_training_parameters(early_stopping=True, evaluation_frequency=1)
        image_classification_multilabel_job_sweep.set_limits(max_trials=2, max_concurrent_trials=2)

        if components:
            # Configure components sweep job search space
            image_classification_multilabel_job_sweep.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["microsoft/beit-base-patch16-224"]),
                        number_of_epochs=Choice([1]),
                        gradient_accumulation_step=Choice([1]),
                        learning_rate=Choice([0.005]),
                    ),
                    SearchSpace(
                        model_name=Choice(["seresnext"]),
                        # model-specific, valid_resize_size should be larger or equal than valid_crop_size
                        validation_resize_size=Choice([288]),
                        validation_crop_size=Choice([224]),  # model-specific
                        training_crop_size=Choice([224]),  # model-specific
                        number_of_epochs=Choice([1]),
                    ),
                ]
            )
            image_classification_multilabel_job_sweep.set_sweep(
                sampling_algorithm="Grid",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

            image_classification_multilabel_job_individual = copy.deepcopy(image_classification_multilabel_job)
            image_classification_multilabel_job_individual.set_training_parameters(
                model_name="microsoft/beit-base-patch16-224", number_of_epochs=1
            )
            image_classification_multilabel_job_reuse = copy.deepcopy(image_classification_multilabel_job_individual)
        else:
            # Configure runtime sweep job search space
            image_classification_multilabel_job_sweep.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["vitb16r224"]),
                        learning_rate=Uniform(0.005, 0.05),
                        number_of_epochs=Choice([1]),
                        gradient_accumulation_step=Choice([1, 2]),
                    ),
                    SearchSpace(
                        model_name=Choice(["seresnext"]),
                        learning_rate=Uniform(0.005, 0.05),
                        # model-specific, valid_resize_size should be larger or equal than valid_crop_size
                        validation_resize_size=Choice([288, 320, 352]),
                        validation_crop_size=Choice([224, 256]),  # model-specific
                        training_crop_size=Choice([224, 256]),  # model-specific
                        number_of_epochs=Choice([1]),
                    ),
                ]
            )
            image_classification_multilabel_job_sweep.set_sweep(
                sampling_algorithm="Random",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

            # Configure AutoMode job
            image_classification_multilabel_job_automode = copy.deepcopy(image_classification_multilabel_job)
            image_classification_multilabel_job_automode.set_limits(max_trials=2, max_concurrent_trials=2)

        # Trigger sweep job and then AutoMode job
        submitted_job_sweep = client.jobs.create_or_update(image_classification_multilabel_job_sweep)
        if components:
            submitted_job_individual_components = client.jobs.create_or_update(
                image_classification_multilabel_job_individual
            )
            submitted_job_components_reuse = client.jobs.create_or_update(image_classification_multilabel_job_reuse)
        else:
            submitted_job_automode = client.jobs.create_or_update(image_classification_multilabel_job_automode)

        # Assert completion of sweep job
        assert_final_job_status(
            submitted_job_sweep, client, ImageClassificationMultilabelJob, JobStatus.COMPLETED, deadline=3600
        )

        if components:
            assert_final_job_status(
                submitted_job_individual_components,
                client,
                ImageClassificationMultilabelJob,
                JobStatus.COMPLETED,
                deadline=3600,
            )
            assert_final_job_status(
                submitted_job_components_reuse,
                client,
                ImageClassificationMultilabelJob,
                JobStatus.COMPLETED,
                deadline=3600,
            )
        else:
            # Assert completion of Automode job
            assert_final_job_status(
                submitted_job_automode, client, ImageClassificationMultilabelJob, JobStatus.COMPLETED, deadline=3600
            )

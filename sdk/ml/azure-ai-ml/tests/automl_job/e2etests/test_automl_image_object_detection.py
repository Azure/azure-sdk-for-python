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
from azure.ai.ml.entities._job.automl.image import ImageObjectDetectionJob, ImageObjectDetectionSearchSpace
from azure.ai.ml.operations._run_history_constants import JobStatus
from azure.ai.ml.sweep import BanditPolicy, Choice, Uniform


@pytest.mark.automl_test
@pytest.mark.usefixtures("recorded_test")
@pytest.mark.skipif(condition=not is_live(), reason="Datasets downloaded by test are too large to record reliably")
class TestAutoMLImageObjectDetection(AzureRecordedTestCase):
    def _create_jsonl_object_detection(self, client, train_path, val_path):
        import xml.etree.ElementTree as ET

        src_images = "./odFridgeObjects/"
        train_validation_ratio = 5

        # Path to the training and validation files
        train_annotations_file = os.path.join(train_path, "train_annotations.jsonl")
        validation_annotations_file = os.path.join(val_path, "validation_annotations.jsonl")

        fridge_data = Data(
            path="./odFridgeObjects",
            type=AssetTypes.URI_FOLDER,
        )
        data_path_uri = client.data.create_or_update(fridge_data)

        # Baseline of json line dictionary
        json_line_sample = {
            "image_url": data_path_uri.path,
            "image_details": {"format": None, "width": None, "height": None},
            "label": [],
        }

        # Path to the annotations
        annotations_folder = os.path.join(src_images, "annotations")

        # Read each annotation and convert it to jsonl line
        with open(train_annotations_file, "w") as train_f:
            with open(validation_annotations_file, "w") as validation_f:
                for i, filename in enumerate(os.listdir(annotations_folder)):
                    if filename.endswith(".xml"):
                        print("Parsing " + os.path.join(src_images, filename))

                        root = ET.parse(os.path.join(annotations_folder, filename)).getroot()

                        width = int(root.find("size/width").text)
                        height = int(root.find("size/height").text)

                        labels = []
                        for object in root.findall("object"):
                            name = object.find("name").text
                            xmin = object.find("bndbox/xmin").text
                            ymin = object.find("bndbox/ymin").text
                            xmax = object.find("bndbox/xmax").text
                            ymax = object.find("bndbox/ymax").text
                            isCrowd = int(object.find("difficult").text)
                            labels.append(
                                {
                                    "label": name,
                                    "topX": float(xmin) / width,
                                    "topY": float(ymin) / height,
                                    "bottomX": float(xmax) / width,
                                    "bottomY": float(ymax) / height,
                                    "isCrowd": isCrowd,
                                }
                            )
                        # build the jsonl file
                        image_filename = root.find("filename").text
                        _, file_extension = os.path.splitext(image_filename)
                        json_line = dict(json_line_sample)
                        json_line["image_url"] = json_line["image_url"] + "images/" + image_filename
                        json_line["image_details"]["format"] = file_extension[1:]
                        json_line["image_details"]["width"] = width
                        json_line["image_details"]["height"] = height
                        json_line["label"] = labels

                        if i % train_validation_ratio == 0:
                            # validation annotation
                            validation_f.write(json.dumps(json_line) + "\n")
                        else:
                            # train annotation
                            train_f.write(json.dumps(json_line) + "\n")
                    else:
                        print("Skipping unknown file: {}".format(filename))

    @pytest.mark.parametrize("components", [(False), (True)])
    def test_image_object_detection_run(
        self, image_object_detection_dataset: Tuple[Input, Input], client: MLClient, components: bool
    ) -> None:
        # Note: this test launches two jobs in order to avoid calling the dataset fixture more than once. Ideally, it
        # would have sufficed to mark the fixture with session scope, but pytest-xdist breaks this functionality:
        # https://github.com/pytest-dev/pytest-xdist/issues/271.

        # Get training and validation data
        train_path, val_path = image_object_detection_dataset

        # Create jsonl file
        self._create_jsonl_object_detection(client=client, train_path=train_path, val_path=val_path)

        training_data = Input(type=AssetTypes.MLTABLE, path=train_path)
        validation_data = Input(type=AssetTypes.MLTABLE, path=val_path)

        # Make generic detection job
        image_object_detection_job = automl.image_object_detection(
            compute="gpu-cluster",
            experiment_name="image-e2e-tests",
            training_data=training_data,
            validation_data=validation_data,
            target_column_name="label",
            primary_metric="MeanAveragePrecision",
            # These are temporal properties needed in Private Preview
            properties=get_automl_job_properties(),
        )

        image_object_detection_job_sweep = copy.deepcopy(image_object_detection_job)
        image_object_detection_job_sweep.set_training_parameters(early_stopping=True, evaluation_frequency=1)
        image_object_detection_job_sweep.set_limits(max_trials=2, max_concurrent_trials=2)
        if components:
            # Configure component sweep job search space
            image_object_detection_job_sweep.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["atss_r50_fpn_1x_coco"]),
                        number_of_epochs=Choice([1]),
                        gradient_accumulation_step=Choice([1]),
                        learning_rate=Choice([0.005]),
                    ),
                    SearchSpace(
                        model_name=Choice(["fasterrcnn_resnet50_fpn"]),
                        learning_rate=Choice([0.001]),
                        optimizer=Choice(["sgd"]),
                        min_size=Choice([600]),  # model-specific
                        number_of_epochs=Choice([1]),
                    ),
                ]
            )
            image_object_detection_job_sweep.set_sweep(
                sampling_algorithm="Grid",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

            image_object_detection_job_individual = copy.deepcopy(image_object_detection_job)
            image_object_detection_job_individual.set_training_parameters(
                model_name="atss_r50_fpn_1x_coco", number_of_epochs=1
            )
            image_object_detection_job_reuse = copy.deepcopy(image_object_detection_job_individual)
        else:
            # Configure runtime sweep job search space
            image_object_detection_job_sweep.extend_search_space(
                [
                    SearchSpace(
                        model_name=Choice(["yolov5"]),
                        learning_rate=Uniform(0.0001, 0.01),
                        model_size=Choice(["small", "medium"]),  # model-specific
                        number_of_epochs=Choice([1]),
                    ),
                    SearchSpace(
                        model_name=Choice(["fasterrcnn_resnet50_fpn"]),
                        learning_rate=Uniform(0.0001, 0.001),
                        optimizer=Choice(["sgd", "adam", "adamw"]),
                        min_size=Choice([600, 800]),  # model-specific
                        number_of_epochs=Choice([1]),
                    ),
                ]
            )
            image_object_detection_job_sweep.set_sweep(
                sampling_algorithm="Random",
                early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.2, delay_evaluation=6),
            )

            # Configure AutoMode job
            image_object_detection_job_automode = copy.deepcopy(image_object_detection_job)
            image_object_detection_job_automode.set_limits(max_trials=2, max_concurrent_trials=2)

        # Trigger sweep and then AutoMode job
        submitted_job_sweep = client.jobs.create_or_update(image_object_detection_job_sweep)
        if components:
            submitted_job_individual_components = client.jobs.create_or_update(image_object_detection_job_individual)
            submitted_job_components_reuse = client.jobs.create_or_update(image_object_detection_job_reuse)
        else:
            submitted_job_automode = client.jobs.create_or_update(image_object_detection_job_automode)

        # Assert completion of sweep job
        assert_final_job_status(
            submitted_job_sweep, client, ImageObjectDetectionJob, JobStatus.COMPLETED, deadline=3600
        )

        if components:
            assert_final_job_status(
                submitted_job_individual_components, client, ImageObjectDetectionJob, JobStatus.COMPLETED, deadline=3600
            )
            assert_final_job_status(
                submitted_job_components_reuse, client, ImageObjectDetectionJob, JobStatus.COMPLETED, deadline=3600
            )
        else:
            # Assert completion of Automode job
            assert_final_job_status(
                submitted_job_automode, client, ImageObjectDetectionJob, JobStatus.COMPLETED, deadline=3600
            )

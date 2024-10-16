# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_automl_image.py
DESCRIPTION:
    These samples demonstrate how to use AutoML Image functions
USAGE:
    python ml_samples_automl_image.py

"""


class AutoMLImageSamples(object):
    def automl_image_jobs(self):

        # [START automl.image_classification]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import ClassificationMultilabelPrimaryMetrics

        image_classification_job = automl.image_classification(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="label",
            primary_metric=ClassificationMultilabelPrimaryMetrics.ACCURACY,
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.image_classification]

        # [START automl.image_classification_multilabel]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import ClassificationMultilabelPrimaryMetrics

        image_classification_multilabel_job = automl.image_classification_multilabel(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="label",
            primary_metric=ClassificationMultilabelPrimaryMetrics.IOU,
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.image_classification_multilabel]

        # [START automl.image_object_detection]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import ObjectDetectionPrimaryMetrics

        image_object_detection_job = automl.image_object_detection(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="label",
            primary_metric=ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION,
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.image_object_detection]

        # [START automl.image_instance_segmentation]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import InstanceSegmentationPrimaryMetrics

        image_instance_segmentation_job = automl.image_instance_segmentation(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="label",
            primary_metric=InstanceSegmentationPrimaryMetrics.MEAN_AVERAGE_PRECISION,
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.image_instance_segmentation]

        # [START automl.automl_image_job.image_classification_job]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import ClassificationMultilabelPrimaryMetrics

        image_classification_job = automl.ImageClassificationJob(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="label",
            primary_metric=ClassificationMultilabelPrimaryMetrics.ACCURACY,
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.automl_image_job.image_classification_job]

        # [START automl.automl_image_job.image_classification_multilabel_job]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import ClassificationMultilabelPrimaryMetrics

        image_classification_multilabel_job = automl.ImageClassificationMultilabelJob(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="terms",
            primary_metric=ClassificationMultilabelPrimaryMetrics.IOU,
            tags={"my_custom_tag": "My custom value"},
        )
        # [END automl.automl_image_job.image_classification_multilabel_job]

        # [START automl.automl_image_job.image_object_detection_job]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import ObjectDetectionPrimaryMetrics

        image_object_detection_job = automl.ImageObjectDetectionJob(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            tags={"my_custom_tag": "My custom value"},
            primary_metric=ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION,
        )
        # [END automl.automl_image_job.image_object_detection_job]

        # [START automl.automl_image_job.image_instance_segmentation_job]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.automl import ObjectDetectionPrimaryMetrics

        image_instance_segmentation_job = automl.ImageInstanceSegmentationJob(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            tags={"my_custom_tag": "My custom value"},
            primary_metric=ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION,
        )
        # [END automl.automl_image_job.image_instance_segmentation_job]

        # [START automl.automl_image_job.image_sweep_settings]
        from azure.ai.ml import automl
        from azure.ai.ml.sweep import BanditPolicy

        image_sweep_settings = automl.ImageSweepSettings(
            sampling_algorithm="Grid",
            early_termination=BanditPolicy(evaluation_interval=2, slack_factor=0.05, delay_evaluation=6),
        )
        # [END automl.automl_image_job.image_sweep_settings]

        # [START automl.automl_image_job.image_classification_search_space]
        from azure.ai.ml import automl
        from azure.ai.ml.sweep import Uniform, Choice

        image_classification_search_space = automl.ImageClassificationSearchSpace(
            model_name="vitb16r224",
            number_of_epochs=Choice([15, 30]),
            weight_decay=Uniform(0.01, 0.1),
        )
        # [END automl.automl_image_job.image_classification_search_space]

        # [START automl.automl_image_job.image_object_detection_search_space]
        from azure.ai.ml import automl
        from azure.ai.ml.sweep import Uniform

        image_detection_search_space = automl.ImageObjectDetectionSearchSpace(
            learning_rate=Uniform(0.005, 0.05),
            model_name="yolov5",
            weight_decay=Uniform(0.01, 0.1),
        )
        # [END automl.automl_image_job.image_object_detection_search_space]

        # [START automl.automl_image_job.image_limit_settings]
        from azure.ai.ml import automl, Input
        from azure.ai.ml.constants import AssetTypes

        # Create the AutoML job with the related factory-function.
        image_job = automl.image_instance_segmentation(
            experiment_name="my_experiment",
            compute="my_compute",
            training_data=Input(type=AssetTypes.MLTABLE, path="./training-mltable-folder"),
            validation_data=Input(type=AssetTypes.MLTABLE, path="./validation-mltable-folder"),
            target_column_name="label",
            primary_metric="MeanAveragePrecision",
            tags={"my_custom_tag": "custom value"},
        )
        # Set the limits for the AutoML job.
        image_job.set_limits(
            max_trials=10,
            max_concurrent_trials=2,
        )
        # [END automl.automl_image_job.image_limit_settings]

        # [START automl.automl_image_job.image_classification_model_settings]
        from azure.ai.ml import automl

        image_classification_model_settings = automl.ImageModelSettingsClassification(
            checkpoint_frequency=5,
            early_stopping=False,
            gradient_accumulation_step=2,
        )
        # [END automl.automl_image_job.image_classification_model_settings]

        # [START automl.automl_image_job.image_object_detection_model_settings]
        from azure.ai.ml import automl

        object_detection_model_settings = automl.ImageModelSettingsObjectDetection(min_size=600, max_size=1333)
        # [END automl.automl_image_job.image_object_detection_model_settings]


if __name__ == "__main__":
    sample = AutoMLImageSamples()
    sample.automl_image_jobs()

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoints for creating AutoML tasks"""

from typing import Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ClassificationPrimaryMetrics,
    ClassificationMultilabelPrimaryMetrics,
    ObjectDetectionPrimaryMetrics,
    InstanceSegmentationPrimaryMetrics,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.image.image_classification_job import ImageClassificationJob
from azure.ai.ml.entities._job.automl.image.image_classification_multilabel_job import ImageClassificationMultilabelJob
from azure.ai.ml.entities._job.automl.image.image_object_detection_job import ImageObjectDetectionJob
from azure.ai.ml.entities._job.automl.image.image_instance_segmentation_job import ImageInstanceSegmentationJob
from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator


def _create_image_job(
    job_cls,
    training_data: Input,
    target_column_name: str,
    primary_metric: Union[str, ClassificationPrimaryMetrics] = None,
    validation_data: Input = None,
    validation_data_size: float = None,
    **kwargs,
):
    """Helper function to create objects for AutoML Image jobs."""
    image_job = job_cls(primary_metric=primary_metric, **kwargs)
    image_job.set_data(
        training_data=training_data,
        target_column_name=target_column_name,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
    )

    return image_job


@pipeline_node_decorator
def image_classification(
    *,
    training_data: Input,
    target_column_name: str,
    primary_metric: Union[str, ClassificationPrimaryMetrics] = None,
    validation_data: Input = None,
    validation_data_size: float = None,
    **kwargs,
) -> ImageClassificationJob:
    """Creates an object for AutoML Image multi-class Classification job.

    :param training_data: Training data.
    :type training_data: Input
    :param target_column_name: Name of the target column.
    :type target_column_name: str
    :param primary_metric: Primary optimization metric for the task.
    :type primary_metric: Union[str, ClassificationPrimaryMetrics]
    :param validation_data: Validation data.
    :type validation_data: Input
    :param validation_data_size: The fraction of training data to be set aside for validation purpose.
    :type validation_data_size: float
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: Image classification job
    :rtype: ImageClassificationJob
    """
    return _create_image_job(
        job_cls=ImageClassificationJob,
        training_data=training_data,
        target_column_name=target_column_name,
        primary_metric=primary_metric,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        **kwargs,
    )


@pipeline_node_decorator
def image_classification_multilabel(
    *,
    training_data: Input,
    target_column_name: str,
    primary_metric: Union[str, ClassificationMultilabelPrimaryMetrics] = None,
    validation_data: Input = None,
    validation_data_size: float = None,
    **kwargs,
) -> ImageClassificationMultilabelJob:
    """Creates an object for AutoML Image multi-label Classification job.

    :param training_data: Training data.
    :type training_data: Input
    :param target_column_name: Name of the target column.
    :type target_column_name: str
    :param primary_metric: Primary optimization metric for the task.
    :type primary_metric: Union[str, ClassificationMultilabelPrimaryMetrics]
    :param validation_data: Validation data.
    :type validation_data: Input
    :param validation_data_size: The fraction of training data to be set aside for validation purpose.
    :type validation_data_size: float
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: Image multi-label classification job
    :rtype: ImageClassificationMultilabelJob
    """
    return _create_image_job(
        job_cls=ImageClassificationMultilabelJob,
        training_data=training_data,
        target_column_name=target_column_name,
        primary_metric=primary_metric,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        **kwargs,
    )


@pipeline_node_decorator
def image_object_detection(
    *,
    training_data: Input,
    target_column_name: str,
    primary_metric: Union[str, ObjectDetectionPrimaryMetrics] = None,
    validation_data: Input = None,
    validation_data_size: float = None,
    **kwargs,
) -> ImageObjectDetectionJob:
    """Creates an object for AutoML Image Object Detection job.

    :param training_data: Training data.
    :type training_data: Input
    :param target_column_name: Name of the target column.
    :type target_column_name: str
    :param primary_metric: Primary optimization metric for the task.
    :type primary_metric: Union[str, ObjectDetectionPrimaryMetrics]
    :param validation_data: Validation data.
    :type validation_data: Input
    :param validation_data_size: The fraction of training data to be set aside for validation purpose.
    :type validation_data_size: float
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: Image object detection job
    :rtype: ImageObjectDetectionJob
    """
    return _create_image_job(
        job_cls=ImageObjectDetectionJob,
        training_data=training_data,
        target_column_name=target_column_name,
        primary_metric=primary_metric,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        **kwargs,
    )


@pipeline_node_decorator
def image_instance_segmentation(
    *,
    training_data: Input,
    target_column_name: str,
    primary_metric: Union[str, InstanceSegmentationPrimaryMetrics] = None,
    validation_data: Input = None,
    validation_data_size: float = None,
    **kwargs,
) -> ImageInstanceSegmentationJob:
    """Creates an object for AutoML Image Instance Segmentation job.

    :param training_data: Training data.
    :type training_data: Input
    :param target_column_name: Name of the target column.
    :type target_column_name: str
    :param primary_metric: Primary optimization metric for the task.
    :type primary_metric: Union[str, InstanceSegmentationPrimaryMetrics]
    :param validation_data: Validation data.
    :type validation_data: Input
    :param validation_data_size: The fraction of training data to be set aside for validation purpose.
    :type validation_data_size: float
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: Image instance segmentation job
    :rtype: ImageInstanceSegmentationJob
    """
    return _create_image_job(
        job_cls=ImageInstanceSegmentationJob,
        training_data=training_data,
        target_column_name=target_column_name,
        primary_metric=primary_metric,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        **kwargs,
    )

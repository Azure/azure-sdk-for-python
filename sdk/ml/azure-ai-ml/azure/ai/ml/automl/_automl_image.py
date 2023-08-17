# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoints for creating AutoML tasks."""

from typing import Optional, TypeVar, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ClassificationMultilabelPrimaryMetrics,
    ClassificationPrimaryMetrics,
    InstanceSegmentationPrimaryMetrics,
    ObjectDetectionPrimaryMetrics,
)
from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.image.automl_image_object_detection_base import AutoMLImageObjectDetectionBase
from azure.ai.ml.entities._job.automl.image.image_classification_job import ImageClassificationJob
from azure.ai.ml.entities._job.automl.image.image_classification_multilabel_job import ImageClassificationMultilabelJob
from azure.ai.ml.entities._job.automl.image.image_instance_segmentation_job import ImageInstanceSegmentationJob
from azure.ai.ml.entities._job.automl.image.image_object_detection_job import ImageObjectDetectionJob

TImageJob = TypeVar("TImageJob", bound=AutoMLImageObjectDetectionBase)


def _create_image_job(
    job_cls: TImageJob,
    training_data: Input,
    target_column_name: str,
    primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    **kwargs,
) -> TImageJob:
    """Helper function to create objects for AutoML Image jobs.

    :param job_cls: The job class
    :type job_cls: TImageJob
    :param training_data: The training input data
    :type training_data: Input
    :param target_column_name: The target column name
    :type target_column_name: str
    :param primary_metric: The primary metric
    :type primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]]
    :param validation_data: The validation data
    :type validation_data: Optional[Input]
    :param validation_data_size: The validation data size
    :type validation_data_size: Optional[float]
    :return: An AutoML Image Job
    :rtype: TImageJob
    """
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
    primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    **kwargs,
) -> ImageClassificationJob:
    """Creates an object for AutoML Image multi-class Classification job.

    :keyword training_data:  The training data to be used within the experiment.
    :paramtype training_data: Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: accuracy, AUC_weighted, norm_macro_recall, average_precision_score_weighted,
            and precision_score_weighted
            Defaults to accuracy.
    :type primary_metric: Union[str, ClassificationPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Input
    :keyword validation_data_size:  What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict

    :return: Image classification job object that can be submitted to an Azure ML compute for execution.
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
    primary_metric: Optional[Union[str, ClassificationMultilabelPrimaryMetrics]] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    **kwargs,
) -> ImageClassificationMultilabelJob:
    """Creates an object for AutoML Image multi-label Classification job.

    :keyword training_data:  The training data to be used within the experiment.
    :paramtype training_data: Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: accuracy, AUC_weighted, norm_macro_recall, average_precision_score_weighted,
            precision_score_weighted, and Iou
            Defaults to Iou.
    :type primary_metric: Union[str, ClassificationMultilabelPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Input
    :keyword validation_data_size:  What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict

    :return: Image multi-label classification job object that can be submitted to an Azure ML compute for execution.
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
    primary_metric: Optional[Union[str, ObjectDetectionPrimaryMetrics]] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    **kwargs,
) -> ImageObjectDetectionJob:
    """Creates an object for AutoML Image Object Detection job.

    :keyword training_data:  The training data to be used within the experiment.
    :paramtype training_data: Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: MeanAveragePrecision
            Defaults to MeanAveragePrecision.
    :type primary_metric: Union[str, ObjectDetectionPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Input
    :keyword validation_data_size:  What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict

    :return: Image object detection job object that can be submitted to an Azure ML compute for execution.
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
    primary_metric: Optional[Union[str, InstanceSegmentationPrimaryMetrics]] = None,
    validation_data: Optional[Input] = None,
    validation_data_size: Optional[float] = None,
    **kwargs,
) -> ImageInstanceSegmentationJob:
    """Creates an object for AutoML Image Instance Segmentation job.

    :keyword training_data:  The training data to be used within the experiment.
    :paramtype training_data: Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: MeanAveragePrecision
            Defaults to MeanAveragePrecision.
    :type primary_metric: Union[str, InstanceSegmentationPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Input
    :keyword validation_data_size:  What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict

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

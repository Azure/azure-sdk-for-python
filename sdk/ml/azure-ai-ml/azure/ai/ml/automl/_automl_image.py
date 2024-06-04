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
    :type training_data: ~azure.ai.ml.entities.Input
    :param target_column_name: The target column name
    :type target_column_name: str
    :param primary_metric: The primary metric
    :type primary_metric: Optional[Union[str, ~azure.ai.ml.automl.ClassificationPrimaryMetrics]]
    :param validation_data: The validation data
    :type validation_data: Optional[~azure.ai.ml.entities.Input]
    :param validation_data_size: The validation data size
    :type validation_data_size: Optional[float]
    :return: An AutoML Image Job
    :rtype: TImageJob
    """
    image_job = job_cls(primary_metric=primary_metric, **kwargs)  # type: ignore[operator]
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

    :keyword training_data: The training data to be used within the experiment.
    :paramtype training_data: ~azure.ai.ml.entities.Input
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
    :paramtype primary_metric: Union[str, ~azure.ai.ml.automl.ClassificationPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Optional[~azure.ai.ml.entities.Input]
    :keyword validation_data_size: What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float

    :return: Image classification job object that can be submitted to an Azure ML compute for execution.
    :rtype: ~azure.ai.ml.automl.ImageClassificationJob

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_image.py
                :start-after: [START automl.image_classification]
                :end-before: [END automl.image_classification]
                :language: python
                :dedent: 8
                :caption: creating an automl image classification job
    """
    return _create_image_job(  # type: ignore[type-var, return-value]
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

    :keyword training_data: The training data to be used within the experiment.
    :paramtype training_data: ~azure.ai.ml.entities.Input
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
    :paramtype primary_metric: Union[str, ~azure.ai.ml.automl.ClassificationMultilabelPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Optional[~azure.ai.ml.entities.Input]
    :keyword validation_data_size: The fraction of the training data to hold out for validation when user does not
            provide the validation data. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float

    :return: Image multi-label classification job object that can be submitted to an Azure ML compute for execution.
    :rtype: ~azure.ai.ml.automl.ImageClassificationMultilabelJob

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_image.py
                :start-after: [START automl.image_classification_multilabel]
                :end-before: [END automl.image_classification_multilabel]
                :language: python
                :dedent: 8
                :caption: creating an automl image multilabel classification job
    """
    return _create_image_job(  # type: ignore[type-var, return-value]
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

    :keyword training_data: The training data to be used within the experiment.
    :paramtype training_data: ~azure.ai.ml.entities.Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: MeanAveragePrecision
            Defaults to MeanAveragePrecision.
    :paramtype primary_metric: Union[str, ~azure.ai.ml.automl.ObjectDetectionPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Optional[~azure.ai.ml.entities.Input]
    :keyword validation_data_size: The fraction of the training data to hold out for validation when user does not
            provide the validation data. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float

    :return: Image object detection job object that can be submitted to an Azure ML compute for execution.
    :rtype: ~azure.ai.ml.automl.ImageObjectDetectionJob

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_image.py
                :start-after: [START automl.image_object_detection]
                :end-before: [END automl.image_object_detection]
                :language: python
                :dedent: 8
                :caption: creating an automl image object detection job
    """
    return _create_image_job(  # type: ignore[type-var, return-value]
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

    :keyword training_data: The training data to be used within the experiment.
    :paramtype training_data: ~azure.ai.ml.entities.Input
    :keyword target_column_name: The name of the label column.
            This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
    :paramtype target_column_name: str
    :keyword primary_metric: The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            Acceptable values: MeanAveragePrecision
            Defaults to MeanAveragePrecision.
    :paramtype primary_metric: Union[str, ~azure.ai.ml.automl.InstanceSegmentationPrimaryMetrics]
    :keyword validation_data: The validation data to be used within the experiment.
    :paramtype validation_data: Optional[~azure.ai.ml.entities.Input]
    :keyword validation_data_size: The fraction of the training data to hold out for validation when user does not
            provide the validation data. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``validation_data_size``
            to extract validation data out of the specified training data.

            Defaults to .2
    :paramtype validation_data_size: float

    :return: Image instance segmentation job
    :rtype: ~azure.ai.ml.automl.ImageInstanceSegmentationJob

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_image.py
                :start-after: [START automl.image_instance_segmentation]
                :end-before: [END automl.image_instance_segmentation]
                :language: python
                :dedent: 8
                :caption: creating an automl image instance segmentation job
    """
    return _create_image_job(  # type: ignore[type-var, return-value]
        job_cls=ImageInstanceSegmentationJob,
        training_data=training_data,
        target_column_name=target_column_name,
        primary_metric=primary_metric,
        validation_data=validation_data,
        validation_data_size=validation_data_size,
        **kwargs,
    )

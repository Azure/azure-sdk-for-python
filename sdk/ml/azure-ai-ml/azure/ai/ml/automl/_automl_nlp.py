# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entrypoints for creating AutoML tasks."""

from typing import Optional

from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.automl.nlp.text_classification_job import TextClassificationJob
from azure.ai.ml.entities._job.automl.nlp.text_classification_multilabel_job import TextClassificationMultilabelJob
from azure.ai.ml.entities._job.automl.nlp.text_ner_job import TextNerJob


@pipeline_node_decorator
def text_classification(
    *,
    training_data: Input,
    target_column_name: str,
    validation_data: Input,
    primary_metric: Optional[str] = None,
    log_verbosity: Optional[str] = None,
    **kwargs,
) -> TextClassificationJob:
    """Function to create a TextClassificationJob.

    A text classification job is used to train a model that can predict the class/category of a text data.
    Input training data should include a target column that classifies the text into exactly one class.

    :keyword training_data: The training data to be used within the experiment.
            It should contain both training features and a target column.
    :paramtype training_data: Input
    :keyword target_column_name: Name of the target column.
    :paramtype target_column_name: str
    :keyword validation_data: The validation data to be used within the experiment.
            It should contain both training features and a target column.
    :paramtype validation_data: Input
    :keyword primary_metric: Primary metric for the task.
            Acceptable values: accuracy, AUC_weighted, precision_score_weighted
    :paramtype primary_metric: Union[str, ClassificationPrimaryMetrics]
    :keyword log_verbosity: Log verbosity level.
    :paramtype log_verbosity: str

    :return: The TextClassificationJob object.
    :rtype: TextClassificationJob

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.text_classification]
                :end-before: [END automl.text_classification]
                :language: python
                :dedent: 8
                :caption: creating an automl text classification job
    """

    text_classification_job = TextClassificationJob(
        primary_metric=primary_metric,
        training_data=training_data,
        target_column_name=target_column_name,
        validation_data=validation_data,
        log_verbosity=log_verbosity,
        **kwargs,
    )

    return text_classification_job


@pipeline_node_decorator
def text_classification_multilabel(
    *,
    training_data: Input,
    target_column_name: str,
    validation_data: Input,
    primary_metric: Optional[str] = None,
    log_verbosity: Optional[str] = None,
    **kwargs,
) -> TextClassificationMultilabelJob:
    """Function to create a TextClassificationMultilabelJob.

    A text classification multilabel job is used to train a model that can predict the classes/categories
    of a text data. Input training data should include a target column that classifies the text into class(es).
    For more information on format of multilabel data, refer to:
    https://docs.microsoft.com/en-us/azure/machine-learning/how-to-auto-train-nlp-models#multi-label

    :keyword training_data: The training data to be used within the experiment.
            It should contain both training features and a target column.
    :paramtype training_data: Input
    :keyword target_column_name: Name of the target column.
    :paramtype target_column_name: str
    :keyword validation_data: The validation data to be used within the experiment.
            It should contain both training features and a target column.
    :paramtype validation_data: Input
    :keyword primary_metric: Primary metric for the task.
            Acceptable values: accuracy
    :paramtype primary_metric: str
    :keyword log_verbosity: Log verbosity level.
    :paramtype log_verbosity: str

    :return: The TextClassificationMultilabelJob object.
    :rtype: TextClassificationMultilabelJob

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.text_classification_multilabel]
                :end-before: [END automl.text_classification_multilabel]
                :language: python
                :dedent: 8
                :caption: creating an automl text multilabel classification job
    """

    text_classification_multilabel_job = TextClassificationMultilabelJob(
        primary_metric=primary_metric,
        training_data=training_data,
        target_column_name=target_column_name,
        validation_data=validation_data,
        log_verbosity=log_verbosity,
        **kwargs,
    )

    return text_classification_multilabel_job


@pipeline_node_decorator
def text_ner(
    *,
    training_data: Input,
    validation_data: Input,
    primary_metric: Optional[str] = None,
    log_verbosity: Optional[str] = None,
    **kwargs,
) -> TextNerJob:
    """Function to create a TextNerJob.

    A text named entity recognition job is used to train a model that can predict the named entities in the text.
    Input training data should be a text file in CoNLL format. For more information on format of text NER data,
    refer to:
    https://docs.microsoft.com/en-us/azure/machine-learning/how-to-auto-train-nlp-models#named-entity-recognition-ner

    :keyword training_data: The training data to be used within the experiment.
            It should contain both training features and a target column.
    :paramtype training_data: Input
    :keyword validation_data: The validation data to be used within the experiment.
            It should contain both training features and a target column.
    :paramtype validation_data: Input
    :keyword primary_metric: Primary metric for the task.
            Acceptable values: accuracy
    :paramtype primary_metric: str
    :keyword log_verbosity: Log verbosity level.
    :paramtype log_verbosity: str

    :return: The TextNerJob object.
    :rtype: TextNerJob

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.text_ner]
                :end-before: [END automl.text_ner]
                :language: python
                :dedent: 8
                :caption: creating an automl text ner job
    """

    text_ner_job = TextNerJob(
        primary_metric=primary_metric,
        training_data=training_data,
        validation_data=validation_data,
        log_verbosity=log_verbosity,
        **kwargs,
    )

    return text_ner_job

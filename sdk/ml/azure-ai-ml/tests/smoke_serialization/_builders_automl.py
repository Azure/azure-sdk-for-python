# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for AutoML job entities (tabular + image + nlp)."""
from azure.ai.ml import Input, automl
from azure.ai.ml.constants._common import AssetTypes

_TRAIN = Input(type=AssetTypes.MLTABLE, path="azureml://datastores/workspaceblobstore/paths/smoke/train/")
_VALID = Input(type=AssetTypes.MLTABLE, path="azureml://datastores/workspaceblobstore/paths/smoke/valid/")


def build_automl_classification():
    """AutoML tabular classification job."""
    job = automl.classification(
        name="smoke-automl-classification",
        compute="smoke-compute",
        experiment_name="smoke-experiment",
        training_data=_TRAIN,
        validation_data=_VALID,
        target_column_name="target",
        primary_metric="accuracy",
    )
    job.set_limits(timeout_minutes=60, max_trials=10, max_concurrent_trials=2)
    return job


def build_automl_regression():
    """AutoML tabular regression job."""
    job = automl.regression(
        name="smoke-automl-regression",
        compute="smoke-compute",
        experiment_name="smoke-experiment",
        training_data=_TRAIN,
        validation_data=_VALID,
        target_column_name="target",
        primary_metric="r2_score",
    )
    job.set_limits(timeout_minutes=60, max_trials=10, max_concurrent_trials=2)
    return job


def build_automl_forecasting():
    """AutoML tabular forecasting job."""
    job = automl.forecasting(
        name="smoke-automl-forecasting",
        compute="smoke-compute",
        experiment_name="smoke-experiment",
        training_data=_TRAIN,
        validation_data=_VALID,
        target_column_name="target",
        primary_metric="normalized_root_mean_squared_error",
    )
    job.set_limits(timeout_minutes=60, max_trials=10, max_concurrent_trials=2)
    job.set_forecast_settings(time_column_name="timestamp", forecast_horizon=12)
    return job


def build_automl_text_classification():
    """AutoML NLP text classification job."""
    job = automl.text_classification(
        name="smoke-automl-text-classification",
        compute="smoke-compute",
        experiment_name="smoke-experiment",
        training_data=_TRAIN,
        validation_data=_VALID,
        target_column_name="target",
        primary_metric="accuracy",
    )
    job.set_limits(timeout_minutes=60, max_trials=2, max_concurrent_trials=1)
    return job


def build_automl_text_ner():
    """AutoML NLP text NER job."""
    job = automl.text_ner(
        name="smoke-automl-text-ner",
        compute="smoke-compute",
        experiment_name="smoke-experiment",
        training_data=_TRAIN,
        validation_data=_VALID,
    )
    job.set_limits(timeout_minutes=60, max_trials=2, max_concurrent_trials=1)
    return job


def build_automl_image_classification():
    """AutoML image classification job."""
    job = automl.image_classification(
        name="smoke-automl-image-classification",
        compute="smoke-compute",
        experiment_name="smoke-experiment",
        training_data=_TRAIN,
        validation_data=_VALID,
        target_column_name="label",
        primary_metric="accuracy",
    )
    job.set_limits(timeout_minutes=60, max_trials=2, max_concurrent_trials=1)
    return job


AUTOML_BUILDERS = {
    "automl_classification": build_automl_classification,
    "automl_regression": build_automl_regression,
    "automl_forecasting": build_automl_forecasting,
    "automl_text_classification": build_automl_text_classification,
    "automl_text_ner": build_automl_text_ner,
    "automl_image_classification": build_automl_image_classification,
}

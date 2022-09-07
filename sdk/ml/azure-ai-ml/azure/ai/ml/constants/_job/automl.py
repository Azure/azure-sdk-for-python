# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum


class AutoMLConstants:
    # The following are fields found in the yaml for AutoML Job
    GENERAL_YAML = "general"
    DATA_YAML = "data"
    FEATURIZATION_YAML = "featurization"
    LIMITS_YAML = "limits"
    SWEEP_YAML = "sweep"
    FORECASTING_YAML = "forecasting"
    TRAINING_YAML = "training"
    MAX_TRIALS_YAML = "max_trials"
    VALIDATION_DATASET_SIZE_YAML = "validation_dataset_size"
    TRAINING_DATA_SETTINGS_YAML = "training"
    TEST_DATA_SETTINGS_YAML = "test"
    VALIDATION_DATA_SETTINGS_YAML = "validation"
    COUNTRY_OR_REGION_YAML = "country_or_region_for_holidays"
    TASK_TYPE_YAML = "task"
    TIMEOUT_YAML = "timeout_minutes"
    TRIAL_TIMEOUT_YAML = "trial_timeout_minutes"
    BLOCKED_ALGORITHMS_YAML = "blocked_training_algorithms"
    ALLOWED_ALGORITHMS_YAML = "allowed_training_algorithms"
    ENSEMBLE_MODEL_DOWNLOAD_TIMEOUT_YAML = "ensemble_model_download_timeout_minutes"
    TERMINATION_POLICY_TYPE_YAML = "type"

    # TASK TYPES
    CLASSIFICATION_YAML = "classification"
    REGRESSION_YAML = "regression"
    FORECASTING_YAML = "forecasting"

    # The following are general purpose AutoML fields
    TARGET_LAGS = "target_lags"
    AUTO = "auto"
    OFF = "off"
    CUSTOM = "custom"
    TIME_SERIES_ID_COLUMN_NAMES = "time_series_id_column_names"
    TRANSFORMER_PARAMS = "transformer_params"
    MODE = "mode"


class AutoMLTransformerParameterKeys(Enum):
    IMPUTER = "Imputer"
    TF_IDF = "TfIdf"
    HASH_ONE_HOT_ENCODER = "HashOneHotEncoder"

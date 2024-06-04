# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta

from azure.ai.ml._utils._experimental import experimental


ALL_FEATURES = "all_features"


AZMONITORING = "azmonitoring"

DEPLOYMENT_MODEL_INPUTS_NAME_KEY = "data_collector.collections.model_inputs.data.name"
DEPLOYMENT_MODEL_INPUTS_VERSION_KEY = "data_collector.collections.model_inputs.data.version"
DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY = "data_collector.collections.model_outputs.data.name"
DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY = "data_collector.collections.model_outputs.data.version"
DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY = "data_collector.collections.model_inputs.enabled"
DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY = "data_collector.collections.model_outputs.enabled"


SPARK_INSTANCE_TYPE_KEY = "compute.spark.resources.instance_type"
SPARK_RUNTIME_VERSION = "compute.spark.resources.runtime_version"

COMPUTE_AML_TYPE = "AmlToken"
COMPUTE_MANAGED_IDENTITY_TYPE = "ManagedIdentity"

DEFAULT_DATA_DRIFT_SIGNAL_NAME = "data-drift-signal"
DEFAULT_PREDICTION_DRIFT_SIGNAL_NAME = "prediction-drift-signal"
DEFAULT_DATA_QUALITY_SIGNAL_NAME = "data-quality-signal"
DEFAULT_TOKEN_USAGE_SIGNAL_NAME = "token-usage-signal"


@experimental
class MonitorSignalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    DATA_DRIFT = "data_drift"
    DATA_QUALITY = "data_quality"
    PREDICTION_DRIFT = "prediction_drift"
    MODEL_PERFORMANCE = "model_performance"
    FEATURE_ATTRIBUTION_DRIFT = "feature_attribution_drift"
    CUSTOM = "custom"
    GENERATION_SAFETY_QUALITY = "generation_safety_quality"
    GENERATION_TOKEN_STATISTICS = "generation_token_statistics"


@experimental
class MonitorMetricName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    JENSEN_SHANNON_DISTANCE = "jensen_shannon_distance"
    NORMALIZED_WASSERSTEIN_DISTANCE = "normalized_wasserstein_distance"
    POPULATION_STABILITY_INDEX = "population_stability_index"
    TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST = "two_sample_kolmogorov_smirnov_test"
    PEARSONS_CHI_SQUARED_TEST = "pearsons_chi_squared_test"
    NULL_VALUE_RATE = "null_value_rate"
    DATA_TYPE_ERROR_RATE = "data_type_error_rate"
    OUT_OF_BOUND_RATE = "out_of_bounds_rate"
    NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN = "normalized_discounted_cumulative_gain"
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    MAE = "MAE"
    MSE = "MSE"
    RMSE = "RMSE"


@experimental
class MonitorModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


@experimental
class MonitorFeatureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    NOT_APPLICABLE = "not_applicable"
    ALL_FEATURE_TYPES = "all_feature_types"


@experimental
class MonitorDatasetContext(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    MODEL_INPUTS = "model_inputs"
    MODEL_OUTPUTS = "model_outputs"
    TRAINING = "training"
    TEST = "test"
    VALIDATION = "validation"
    GROUND_TRUTH_DATA = "ground_truth"


class MonitorTargetTasks(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    CLASSIFICATION = "Classification"
    REGRESSION = "Regression"
    QUESTION_ANSWERING = "QuestionAnswering"


class MonitorInputDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    #: An input data with a fixed window size.
    STATIC = "Static"
    #: An input data which trailing relatively to the monitor's current run.
    TRAILING = "Trailing"
    #: An input data with tabular format which doesn't require preprocessing.
    FIXED = "Fixed"


class FADColumnNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    PREDICTION = "prediction"
    PREDICTION_PROBABILITY = "prediction_probability"
    CORRELATION_ID = "correlation_id"


class MonitorFeatureDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"


class NumericalMetricThresholds(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    JENSEN_SHANNON_DISTANCE = "jensen_shannon_distance"
    NORMALIZED_WASSERSTEIN_DISTANCE = "normalized_wasserstein_distance"
    POPULATION_STABILITY_INDEX = "population_stability_index"
    TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST = "two_sample_kolmogorov_smirnov_test"

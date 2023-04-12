# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing_extensions import Literal

from azure.ai.ml.constants._monitoring import MonitorMetricName, MonitorFeatureType
from azure.ai.ml._utils._experimental import experimental


@experimental
class MetricThreshold:
    def __init__(self, threshold: float = None):
        self.applicable_feature_type = None
        self.metric_name = None
        self.threshold = threshold


@experimental
class DataDriftMetricThreshold(MetricThreshold):
    def __init__(
        self,
        applicable_feature_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL] = None,
        metric_name: Literal[
            MonitorMetricName.JENSEN_SHANNON_DISTANCE,
            MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE,
            MonitorMetricName.POPULATION_STABILITY_INDEX,
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_TEST,
            MonitorMetricName.CHI_SQUARED_TEST,
        ] = None,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name


@experimental
class PredictionDriftMetricThreshold(MetricThreshold):
    def __init__(
        self,
        applicable_feature_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL] = None,
        metric_name: Literal[
            MonitorMetricName.JENSEN_SHANNON_DISTANCE,
            MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE,
            MonitorMetricName.POPULATION_STABILITY_INDEX,
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_TEST,
            MonitorMetricName.CHI_SQUARED_TEST,
        ] = None,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name


@experimental
class DataQualityMetricThreshold(MetricThreshold):
    def __init__(
        self,
        applicable_feature_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL] = None,
        metric_name: Literal[
            MonitorMetricName.NULL_VALUE_RATE,
            MonitorMetricName.DATA_TYPE_ERROR_RATE,
            MonitorMetricName.OUT_OF_BOUND_RATE,
        ] = None,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name


@experimental
class FeatureAttributionDriftMetricThreshold(MetricThreshold):
    def __init__(self, threshold: float = None):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = MonitorFeatureType.ALL_FEATURE_TYPES
        self.metric_name = MonitorMetricName.NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN


@experimental
class ModelPerformanceMetricThreshold(MetricThreshold):
    def __init__(
        self,
        metric_name: Literal[
            MonitorMetricName.ACCURACY,
            MonitorMetricName.PRECISION,
            MonitorMetricName.RECALL,
            MonitorMetricName.F1_SCORE,
            MonitorMetricName.MAE,
            MonitorMetricName.MSE,
            MonitorMetricName.RMSE,
        ] = None,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = MonitorFeatureType.NOT_APPLICABLE
        self.metric_name = metric_name


@experimental
class CustomMonitoringMetricThreshold(MetricThreshold):
    def __init__(
        self,
        metric_name: str,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.metric_name = metric_name

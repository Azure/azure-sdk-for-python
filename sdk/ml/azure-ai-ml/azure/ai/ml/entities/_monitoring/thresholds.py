from typing import List, Union

from typing_extensions import Literal

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
        applicable_feature_type: str = None,
        metric_name: str = None,
        threshold: float = None
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name


@experimental
class PredictionDriftMetricThreshold(MetricThreshold):
    def __init__(
        self,
        applicable_feature_type: str = None,
        metric_name: str = None,
        threshold: float = None
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name


@experimental
class DataQuality(MetricThreshold):
    def __init__(
        self,
        applicable_feature_type: str = None,
        metric_name: str = None,
        threshold: float = None
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name


@experimental
class FeatureAttributionDriftMetricThreshold(MetricThreshold):
    def __init__(
        self,
        threshold: float = None
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = "all_feature_types"
        self.metric_name = "normalized_discounted_cumulative_gain"



@experimental
class ModelPerformanceMetricThreshold(MetricThreshold):
    def __init__(
        self,
        metric_name: str = None,
        threshold: float = None
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = "not_applicable"
        self.metric_name = metric_name

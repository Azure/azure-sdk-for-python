# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Union

from typing_extensions import Literal

from azure.ai.ml._utils._experimental import experimental


@experimental
class DataSegment():
    def __init__(
        self,
        *,
        feature_name: str = None,
        feature_values: List[str] = None,
    ):
        self.feature_name = feature_name
        self.feature_values = feature_values


@experimental
class  MonitoringMetricThreshold():
    def __init__(
        self,
        *,
        applicable_feature_type: str = None,
        metric_name: str = None,
        threshold: float = None,
    ):
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name
        self.threshold = threshold


@experimental
class MonitorFeatureFilter():
    def __init__(
        self,
        *,
        top_n_feature_importance: int = None,
    ):
        self.top_n_feature_importance = top_n_feature_importance


@experimental
class BaselineDataRange():
    def __init__(
        self,
        *,
        from_date: str = None,
        to_date: str = None,
    ):
        self.from_date = from_date
        self.to_date = to_date


@experimental
class TargetDataset():
    def __init__(
        self,
        *,
        dataset_name: str = None,
        lookback_period_name: int = None,
    ):
        self.dataset_name = dataset_name
        self.lookback_period_name = lookback_period_name


@experimental
class BaselineDataset():
    def __init__(
        self,
        *,
        dataset_name: str,
        data_range: BaselineDataRange,
    ):
        self.dataset_name = dataset_name
        self.data_range = data_range


@experimental
class MonitoringSignal():
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
    ):
        self.type = None
        self.target_dataset = target_dataset
        self.baseline_dataset = baseline_dataset


@experimental
class MetricMonitoringSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        metric_thresholds: MonitoringMetricThreshold = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset
        )
        self.metric_thresholds = metric_thresholds

@experimental
class DataSignal(MetricMonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        features: Union[List[str], MonitorFeatureFilter, Literal["all_features"]] = None,
        metric_thresholds: MonitoringMetricThreshold = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
        )
        self.features = features



@experimental
class DataDriftSignal(DataSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        features: Union[List[str], MonitorFeatureFilter, Literal["all_features"]] = None,
        metric_thresholds: MonitoringMetricThreshold = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
        )
        self.type = "data_drift"


@experimental
class PredictionDriftSignal(MetricMonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        metric_thresholds: MonitoringMetricThreshold = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds
        )
        self.type = "prediction_drift"


@experimental
class DataQualitySignal(DataSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        features: Union[List[str], MonitorFeatureFilter, Literal["all_features"]] = None,
        metric_thresholds: MonitoringMetricThreshold = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
        )
        self.type = "data_quality"


@experimental
class ModelSignal(MetricMonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        metric_thresholds: MonitoringMetricThreshold = None,
        model_type: str = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
        )
        self.model_type = model_type


@experimental
class FeatureAttributionDriftSignal(ModelSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        metric_thresholds: MonitoringMetricThreshold = None,
        model_type: str = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type
        )
        self.type = "feature_attribution_drift"


@experimental
class ModelPerformanceSignal(ModelSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        metric_thresholds: MonitoringMetricThreshold = None,
        model_type: str = None,
        data_segment: DataSegment = None
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type
        )
        self.type = "model_drift"
        self.data_segment = data_segment


@experimental
class CustomMonitoringSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        component_id: str = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
        )
        self.type = "custom_monitoring_signal"
        self.component_id = component_id

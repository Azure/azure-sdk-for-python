# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Union

from typing_extensions import Literal

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._monitoring.input_data import MonitorInputData
from azure.ai.ml.entities._monitoring.thresholds import (
    MetricThreshold,
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    PredictionDriftMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    ModelPerformanceMetricThreshold,
)


@experimental
class DataSegment:
    def __init__(
        self,
        *,
        feature_name: str = None,
        feature_values: List[str] = None,
    ):
        self.feature_name = feature_name
        self.feature_values = feature_values


@experimental
class MonitorFeatureFilter:
    def __init__(
        self,
        *,
        top_n_feature_importance: int = None,
    ):
        self.top_n_feature_importance = top_n_feature_importance


@experimental
class TargetDataset:
    def __init__(
        self,
        *,
        dataset: MonitorInputData = None,
        lookback_period: int = None,
    ):
        self.dataset = dataset
        self.lookback_period = lookback_period


@experimental
class MonitoringSignal:
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
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
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[MetricThreshold] = None,
    ):
        super().__init__(target_dataset=target_dataset, baseline_dataset=baseline_dataset)
        self.metric_thresholds = metric_thresholds


@experimental
class DataSignal(MetricMonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal["all_features"]] = None,
        metric_thresholds: List[MetricThreshold] = None,
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
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal["all_features"]] = None,
        metric_thresholds: List[DataQualityMetricThreshold] = None,
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
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[PredictionDriftMetricThreshold] = None,
    ):
        super().__init__(
            target_dataset=target_dataset, baseline_dataset=baseline_dataset, metric_thresholds=metric_thresholds
        )
        self.type = "prediction_drift"


@experimental
class DataQualitySignal(DataSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal["all_features"]] = None,
        metric_thresholds: List[DataQualityMetricThreshold] = None,
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
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[MetricThreshold] = None,
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
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[FeatureAttributionDriftMetricThreshold] = None,
        model_type: str = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
        )
        self.type = "feature_attribution_drift"


@experimental
class ModelPerformanceSignal(ModelSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[ModelPerformanceMetricThreshold] = None,
        model_type: str = None,
        data_segment: DataSegment = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
        )
        self.type = "model_drift"
        self.data_segment = data_segment


@experimental
class CustomMonitoringSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        component_id: str = None,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
        )
        self.type = "custom_monitoring_signal"
        self.component_id = component_id

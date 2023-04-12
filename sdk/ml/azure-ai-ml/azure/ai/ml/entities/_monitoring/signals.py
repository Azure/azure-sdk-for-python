# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Union

from typing_extensions import Literal

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._monitoring import MonitorSignalType, ALL_FEATURES, MonitorModelType
from azure.ai.ml.entities._monitoring.input_data import MonitorInputData
from azure.ai.ml.entities._monitoring.thresholds import (
    MetricThreshold,
    DataDriftMetricThreshold,
    DataQualityMetricThreshold,
    PredictionDriftMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    ModelPerformanceMetricThreshold,
    CustomMonitoringMetricThreshold,
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
        metric_thresholds: Union[MetricThreshold, List[MetricThreshold]] = None,
        alert_enabled: bool = True,
    ):
        self.target_dataset = target_dataset
        self.baseline_dataset = baseline_dataset
        self.metric_thresholds = metric_thresholds
        self.alert_enabled = alert_enabled


@experimental
class DataSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[MetricThreshold] = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled
        )
        self.features = features


@experimental
class DataDriftSignal(DataSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[DataDriftMetricThreshold] = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_DRIFT


@experimental
class PredictionDriftSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[PredictionDriftMetricThreshold] = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset, baseline_dataset=baseline_dataset, metric_thresholds=metric_thresholds, alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.PREDICTION_DRIFT


@experimental
class DataQualitySignal(DataSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        features: Union[List[str], MonitorFeatureFilter, Literal[ALL_FEATURES]] = None,
        metric_thresholds: List[DataQualityMetricThreshold] = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            features=features,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.DATA_QUALITY


@experimental
class ModelSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[MetricThreshold] = None,
        model_type: MonitorModelType = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled
        )
        self.model_type = model_type


@experimental
class FeatureAttributionDriftSignal(ModelSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: FeatureAttributionDriftMetricThreshold = None,
        model_type: MonitorModelType = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT


@experimental
class ModelPerformanceSignal(ModelSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: ModelPerformanceMetricThreshold = None,
        model_type: MonitorModelType = None,
        data_segment: DataSegment = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            model_type=model_type,
            alert_enabled=alert_enabled,
        )
        self.type = MonitorSignalType.MODEL_PERFORMANCE
        self.data_segment = data_segment


@experimental
class CustomMonitoringSignal(MonitoringSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: MonitorInputData = None,
        metric_thresholds: List[CustomMonitoringMetricThreshold] = None,
        component_id: str = None,
        alert_enabled: bool = True,
    ):
        super().__init__(
            target_dataset=target_dataset,
            baseline_dataset=baseline_dataset,
            metric_thresholds=metric_thresholds,
            alert_enabled=alert_enabled
        )
        self.type = MonitorSignalType.CUSTOM
        self.component_id = component_id

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Union

from typing_extensions import Literal

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DataDriftMonitoringSignal as RestMonitoringDataDriftSignal,
    DataQualityMonitoringSignal as RestMonitoringDataQualitySignal,
    PredictionDriftMonitoringSignal as RestPredictionDriftMonitoringSignal,
    FeatureAttributionDriftMonitoringSignal as RestFeatureAttributionDriftMonitoringSignal,
    ModelPerformanceSignalBase as RestModelPerformanceSignal,
    CustomMonitoringSignal as RestCustomMonitoringSignal,
    MonitoringDataSegment as RestMonitoringDataSegment,
    TopNFeaturesByAttribution as RestTopNFeaturesByAttribution,
    AllFeatures as RestAllFeatures,
    FeatureSubset as RestFeatureSubset

)
from azure.ai.ml._utils._experimental import experimental


@experimental
class DataSegment(RestTranslatableMixin):
    def __init__(
        self,
        *,
        feature_name: str = None,
        feature_values: List[str] = None,
    ):
        self.feature_name = feature_name
        self.feature_values = feature_values

    def _to_rest_object(self) -> RestMonitoringDataSegment:
        return RestMonitoringDataSegment(feature=self.feature_name, values=self.feature_values)

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataSegment) -> "DataSegment":
        return cls(
            feature_name=obj.feature,
            feature_values=obj.values,
        )


@experimental
class MonitoringMetricThreshold:
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
class MonitorFeatureFilter(RestTranslatableMixin):
    def __init__(
        self,
        *,
        top_n_feature_importance: int = None,
    ):
        self.top_n_feature_importance = top_n_feature_importance

    def _to_rest_object(self) -> RestTopNFeaturesByAttribution:
        return RestTopNFeaturesByAttribution(
            top=self.top_n_feature_importance,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestTopNFeaturesByAttribution) -> "MonitorFeatureFilter":
        return cls(top_n_feature_importance=obj.top)


@experimental
class BaselineDataRange:
    def __init__(
        self,
        *,
        from_date: str = None,
        to_date: str = None,
    ):
        self.from_date = from_date
        self.to_date = to_date


@experimental
class TargetDataset:
    def __init__(
        self,
        *,
        dataset_name: str = None,
        lookback_period_days: int = None,
    ):
        self.dataset_name = dataset_name
        self.lookback_period_days = lookback_period_days


@experimental
class BaselineDataset:
    def __init__(
        self,
        *,
        dataset_name: str,
        data_range: BaselineDataRange,
    ):
        self.dataset_name = dataset_name
        self.data_range = data_range


@experimental
class MonitoringSignal(RestTranslatableMixin):
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
        super().__init__(target_dataset=target_dataset, baseline_dataset=baseline_dataset)
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

    def _to_rest_object(self) -> RestMonitoringDataDriftSignal:
        features = None
        if isinstance(self.features, list):
            features = RestFeatureSubset(features=self.features)
        elif isinstance(self.features, MonitorFeatureFilter):
            features = self.features._to_rest_object()
        elif isinstance(self.features, str) and self.features == "all_features":
            features = RestAllFeatures()
        return RestMonitoringDataDriftSignal(
            features=features,
        )


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
            target_dataset=target_dataset, baseline_dataset=baseline_dataset, metric_thresholds=metric_thresholds
        )
        self.type = "prediction_drift"

    def _to_rest_object(self) -> RestPredictionDriftMonitoringSignal:
        return RestPredictionDriftMonitoringSignal()

    @classmethod
    def _from_rest_object(cls, obj: RestPredictionDriftMonitoringSignal) -> "PredictionDriftSignal":
        return cls()


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

    def _to_rest_object(self) -> RestMonitoringDataQualitySignal:
        if isinstance(self.features, list):
            features = RestFeatureSubset(features=self.features)
        elif isinstance(self.features, MonitorFeatureFilter):
            features = self.features._to_rest_object()
        elif isinstance(self.features, str) and self.features == "all_features":
            features = RestAllFeatures()
        return RestMonitoringDataQualitySignal(
            features=features,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringDataQualitySignal) -> "DataQualitySignal":
        return cls()


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
            model_type=model_type,
        )
        self.type = "feature_attribution_drift"

    def _to_rest_object(self) -> RestFeatureAttributionDriftMonitoringSignal:
        return RestFeatureAttributionDriftMonitoringSignal()

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureAttributionDriftMonitoringSignal) -> "FeatureAttributionDriftSignal":
        return cls()


@experimental
class ModelPerformanceSignal(ModelSignal):
    def __init__(
        self,
        *,
        target_dataset: TargetDataset = None,
        baseline_dataset: BaselineDataset = None,
        metric_thresholds: MonitoringMetricThreshold = None,
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

    def _to_rest_object(self) -> RestModelPerformanceSignal:
        return RestModelPerformanceSignal()

    @classmethod
    def _from_rest_object(cls, obj: RestModelPerformanceSignal) -> "ModelPerformanceSignal":
        return RestModelPerformanceSignal


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

    def _to_rest_object(self) -> RestCustomMonitoringSignal:
        return RestCustomMonitoringSignal(component_id=self.component_id)

    @classmethod
    def _from_rest_object(cls, obj: RestCustomMonitoringSignal) -> "CustomMonitoringSignal":
        return cls(component_id=obj.component_id)
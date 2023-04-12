# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union
from typing_extensions import Literal

from azure.ai.ml.constants._monitoring import MonitorMetricName, MonitorFeatureType, MonitorModelType
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    MonitoringThreshold,
    DataDriftMetricThresholdBase,
    NumericalDataDriftMetricThreshold,
    CategoricalDataDriftMetricThreshold,
    DataQualityMetricThresholdBase,
    NumericalDataQualityMetricThreshold,
    CategoricalDataQualityMetricThreshold,
    PredictionDriftMetricThresholdBase,
    NumericalPredictionDriftMetricThreshold,
    CategoricalPredictionDriftMetricThreshold,
    FeatureAttributionMetricThreshold,
    ModelPerformanceMetricThresholdBase,
    ClassificationModelPerformanceMetricThreshold,
    RegressionModelPerformanceMetricThreshold,
    CustomMetricThreshold,
)
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml._utils._experimental import experimental


@experimental
class MetricThreshold(RestTranslatableMixin):
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
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST,
            MonitorMetricName.PEARSONS_CHI_SQUARED_TEST,
        ] = None,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name

    def _to_rest_object(self) -> DataDriftMetricThresholdBase:
        metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold)
        return (
            NumericalDataDriftMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
            if self.applicable_feature_type == MonitorFeatureType.NUMERICAL
            else CategoricalDataDriftMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: DataDriftMetricThresholdBase) -> "DataDriftMetricThreshold":
        applicable_feature_type = (
            MonitorFeatureType.CATEGORICAL
            if isinstance(obj, CategoricalDataDriftMetricThreshold)
            else MonitorFeatureType.NUMERICAL
        )
        return cls(
            applicable_feature_type=applicable_feature_type,
            metric_name=camel_to_snake(obj.metric),
            threshold=obj.threshold.value,
        )


@experimental
class PredictionDriftMetricThreshold(MetricThreshold):
    def __init__(
        self,
        applicable_feature_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL] = None,
        metric_name: Literal[
            MonitorMetricName.JENSEN_SHANNON_DISTANCE,
            MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE,
            MonitorMetricName.POPULATION_STABILITY_INDEX,
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST,
            MonitorMetricName.PEARSONS_CHI_SQUARED_TEST,
        ] = None,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name

    def _to_rest_object(self) -> PredictionDriftMetricThresholdBase:
        metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold)
        return (
            NumericalPredictionDriftMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
            if self.applicable_feature_type == MonitorFeatureType.NUMERICAL
            else CategoricalPredictionDriftMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: PredictionDriftMetricThresholdBase) -> "PredictionDriftMetricThreshold":
        applicable_feature_type = (
            MonitorFeatureType.CATEGORICAL
            if isinstance(obj, CategoricalPredictionDriftMetricThreshold)
            else MonitorFeatureType.NUMERICAL
        )
        return cls(
            applicable_feature_type=applicable_feature_type,
            metric_name=camel_to_snake(obj.metric),
            threshold=obj.threshold.value,
        )


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

    def _to_rest_object(self) -> DataQualityMetricThresholdBase:
        metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold)
        return (
            NumericalDataQualityMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
            if self.applicable_feature_type == MonitorFeatureType.NUMERICAL
            else CategoricalDataQualityMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: DataQualityMetricThresholdBase) -> "DataQualityMetricThreshold":
        applicable_feature_type = (
            MonitorFeatureType.CATEGORICAL
            if isinstance(obj, CategoricalDataQualityMetricThreshold)
            else MonitorFeatureType.NUMERICAL
        )
        return cls(
            applicable_feature_type=applicable_feature_type,
            metric_name=camel_to_snake(obj.metric),
            threshold=obj.threshold.value,
        )


@experimental
class FeatureAttributionDriftMetricThreshold(MetricThreshold):
    def __init__(self, threshold: float = None):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = MonitorFeatureType.ALL_FEATURE_TYPES
        self.metric_name = MonitorMetricName.NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN

    def _to_rest_object(self) -> FeatureAttributionMetricThreshold:
        return FeatureAttributionMetricThreshold(
            metric=snake_to_camel(self.metric_name), threshold=MonitoringThreshold(value=self.metric_name)
        )

    @classmethod
    def _from_rest_object(cls, obj: FeatureAttributionMetricThreshold) -> "FeatureAttributionDriftMetricThreshold":
        return cls(threshold=obj.threshold.value)


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
        self.metric_name = metric_name

    def _to_rest_object(self, **kwargs) -> ModelPerformanceMetricThresholdBase:
        model_type = kwargs.get("model_type")
        metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold)
        return (
            RegressionModelPerformanceMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
            if model_type == MonitorModelType.REGRESSION
            else ClassificationModelPerformanceMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: ModelPerformanceMetricThresholdBase) -> "ModelPerformanceMetricThreshold":
        return cls(metric=camel_to_snake(obj.metric), threshold=obj.threshold.value)


@experimental
class CustomMonitoringMetricThreshold(MetricThreshold):
    def __init__(
        self,
        metric_name: str,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.metric_name = metric_name

    def _to_rest_object(self) -> CustomMetricThreshold:
        return CustomMetricThreshold(
            metric=self.metric_name,
            threshold=MonitoringThreshold(value=self.threshold),
        )

    @classmethod
    def _from_rest_object(cls, obj: MonitoringThreshold) -> "CustomMonitoringMetricThreshold":
        return cls(
            metric_name=obj.metric,
            threshold=obj.threshold.value
        )

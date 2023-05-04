# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

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
    RegressionModelPerformanceMetric,
    CustomMetricThreshold,
)
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml._utils._experimental import experimental


@experimental
class MetricThreshold(RestTranslatableMixin):
    def __init__(self, *, threshold: float = None):
        self.applicable_feature_type = None
        self.metric_name = None
        self.threshold = threshold


@experimental
class DataDriftMetricThreshold(MetricThreshold):
    """Data drift metric threshold

    :param applicable_feature_type: The feature type of the metric threshold
    :type applicable_feature_type: Literal[
        ~azure.ai.ml.constants.MonitorFeatureType.CATEGORICAL
        , ~azure.ai.ml.constants.MonitorFeatureType.MonitorFeatureType.NUMERICAL]
    :param metric_name: The metric to calculate
    :type metric_name: Literal[
        MonitorMetricName.JENSEN_SHANNON_DISTANCE
        , ~azure.ai.ml.constants.MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE
        , ~azure.ai.ml.constants.MonitorMetricName.POPULATION_STABILITY_INDEX
        , ~azure.ai.ml.constants.MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST
        , ~azure.ai.ml.constants.MonitorMetricName.PEARSONS_CHI_SQUARED_TEST]
    :param threshold: The threshold value. If None, a default value will be set
        depending on the selected metric.
    :type threshold: float
    """

    def __init__(
        self,
        *,
        applicable_feature_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL],
        metric_name: Literal[
            MonitorMetricName.JENSEN_SHANNON_DISTANCE,
            MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE,
            MonitorMetricName.POPULATION_STABILITY_INDEX,
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST,
            MonitorMetricName.PEARSONS_CHI_SQUARED_TEST,
        ],
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name

    def _to_rest_object(self) -> DataDriftMetricThresholdBase:
        metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold) if self.threshold is not None else None
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
        return cls(
            applicable_feature_type=obj.data_type.lower(),
            metric_name=camel_to_snake(obj.metric),
            threshold=obj.threshold.value if obj.threshold else None,
        )


@experimental
class PredictionDriftMetricThreshold(MetricThreshold):
    """Prediction drift metric threshold

    :param applicable_feature_type: The feature type of the metric threshold
    :type applicable_feature_type: Literal[
        ~azure.ai.ml.constants.MonitorFeatureType.CATEGORICAL
        , ~azure.ai.ml.constants.MonitorFeatureType.MonitorFeatureType.NUMERICAL]
    :param metric_name: The metric to calculate
    :type metric_name: Literal[
        ~azure.ai.ml.constants.MonitorMetricName.JENSEN_SHANNON_DISTANCE
        , ~azure.ai.ml.constants.MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE
        , ~azure.ai.ml.constants.MonitorMetricName.POPULATION_STABILITY_INDEX
        , ~azure.ai.ml.constants.MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST
        , ~azure.ai.ml.constants.MonitorMetricName.PEARSONS_CHI_SQUARED_TEST]
    :param threshold: The threshold value. If None, a default value will be set
        depending on the selected metric.
    :type threshold: float
    """

    def __init__(
        self,
        *,
        applicable_feature_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL],
        metric_name: Literal[
            MonitorMetricName.JENSEN_SHANNON_DISTANCE,
            MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE,
            MonitorMetricName.POPULATION_STABILITY_INDEX,
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST,
            MonitorMetricName.PEARSONS_CHI_SQUARED_TEST,
        ],
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name

    def _to_rest_object(self) -> PredictionDriftMetricThresholdBase:
        metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold) if self.threshold is not None else None
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
        return cls(
            applicable_feature_type=obj.data_type.lower(),
            metric_name=camel_to_snake(obj.metric),
            threshold=obj.threshold.value if obj.threshold else None,
        )


@experimental
class DataQualityMetricThreshold(MetricThreshold):
    """Data quality metric threshold

    :param applicable_feature_type: The feature type of the metric threshold
    :type applicable_feature_type: Literal[
        ~azure.ai.ml.constants.MonitorFeatureType.CATEGORICAL
        , ~azure.ai.ml.constants.MonitorFeatureType.MonitorFeatureType.NUMERICAL]
    :param metric_name: The metric to calculate
    :type metric_name: Literal[
        ~azure.ai.ml.constants.MonitorMetricName.JENSEN_SHANNON_DISTANCE
        , ~azure.ai.ml.constants.MonitorMetricName.NULL_VALUE_RATE
        , ~azure.ai.ml.constants.MonitorMetricName.DATA_TYPE_ERROR_RATE
        , ~azure.ai.ml.constants.MonitorMetricName.OUT_OF_BOUND_RATE]
    :param threshold: The threshold value. If None, a default value will be set
        depending on the selected metric.
    :type threshold: float
    """

    def __init__(
        self,
        *,
        applicable_feature_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL],
        metric_name: Literal[
            MonitorMetricName.NULL_VALUE_RATE,
            MonitorMetricName.DATA_TYPE_ERROR_RATE,
            MonitorMetricName.OUT_OF_BOUND_RATE,
        ],
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = applicable_feature_type
        self.metric_name = metric_name

    def _to_rest_object(self) -> DataQualityMetricThresholdBase:
        metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold) if self.threshold is not None else None
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
        return cls(
            applicable_feature_type=obj.data_type.lower(),
            metric_name=camel_to_snake(obj.metric),
            threshold=obj.threshold.value if obj.threshold else None,
        )


@experimental
class FeatureAttributionDriftMetricThreshold(MetricThreshold):
    """Feature attribution drift metric threshold

    :ivar applicable_feature_type: The feature type of the metric threshold
    :vartype applicable_feature_type: Literal[
        ~azure.ai.ml.constants.MonitorFeatureType.ALL_FEATURE_TYPES]
    :ivar metric_name: The metric to calculate
    :vartype metric_name: Literal[
        ~azure.ai.ml.constants.MonitorMetricName.NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN]
    :param threshold: The threshold value. If None, a default value will be set
        depending on the selected metric.
    :type threshold: float
    """

    def __init__(self, *, threshold: float = None):
        super().__init__(threshold=threshold)
        self.applicable_feature_type = MonitorFeatureType.ALL_FEATURE_TYPES
        self.metric_name = MonitorMetricName.NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN

    def _to_rest_object(self) -> FeatureAttributionMetricThreshold:
        return FeatureAttributionMetricThreshold(
            metric=snake_to_camel(self.metric_name),
            threshold=MonitoringThreshold(value=self.threshold) if self.threshold else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: FeatureAttributionMetricThreshold) -> "FeatureAttributionDriftMetricThreshold":
        return cls(threshold=obj.threshold.value if obj.threshold else None)


@experimental
class ModelPerformanceMetricThreshold(MetricThreshold):
    def __init__(
        self,
        *,
        metric_name: Literal[
            MonitorMetricName.ACCURACY,
            MonitorMetricName.PRECISION,
            MonitorMetricName.RECALL,
            MonitorMetricName.F1_SCORE,
            MonitorMetricName.MAE,
            MonitorMetricName.MSE,
            MonitorMetricName.RMSE,
        ],
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.metric_name = metric_name

    def _to_rest_object(self, **kwargs) -> ModelPerformanceMetricThresholdBase:
        model_type = kwargs.get("model_type")
        if self.metric_name.lower() == MonitorMetricName.MAE.lower():
            metric = RegressionModelPerformanceMetric.MEAN_ABSOLUTE_ERROR
        elif self.metric_name.lower() == MonitorMetricName.MSE.lower():
            metric = RegressionModelPerformanceMetric.MEAN_SQUARED_ERROR
        elif self.metric_name.lower() == MonitorMetricName.RMSE.lower():
            metric = RegressionModelPerformanceMetric.ROOT_MEAN_SQUARED_ERROR
        else:
            metric = snake_to_camel(self.metric_name)
        threshold = MonitoringThreshold(value=self.threshold) if self.threshold is not None else None
        return (
            RegressionModelPerformanceMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
            if model_type.lower() == MonitorModelType.REGRESSION.lower()
            else ClassificationModelPerformanceMetricThreshold(
                metric=metric,
                threshold=threshold,
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: ModelPerformanceMetricThresholdBase) -> "ModelPerformanceMetricThreshold":
        if obj.metric == RegressionModelPerformanceMetric.MEAN_ABSOLUTE_ERROR:
            metric_name = MonitorMetricName.MAE
        elif obj.metric == RegressionModelPerformanceMetric.MEAN_SQUARED_ERROR:
            metric_name = MonitorMetricName.MSE
        elif obj.metric == RegressionModelPerformanceMetric.ROOT_MEAN_SQUARED_ERROR:
            metric_name = MonitorMetricName.RMSE
        else:
            metric_name = snake_to_camel(obj.metric)
        return cls(metric_name=metric_name, threshold=obj.threshold.value if obj.threshold else None)


@experimental
class CustomMonitoringMetricThreshold(MetricThreshold):
    """Feature attribution drift metric threshold

    :param metric_name: The metric to calculate
    :type metric_name: str
    :param threshold: The threshold value. If None, a default value will be set
        depending on the selected metric.
    :type threshold: float
    """

    def __init__(
        self,
        *,
        metric_name: str,
        threshold: float = None,
    ):
        super().__init__(threshold=threshold)
        self.metric_name = metric_name

    def _to_rest_object(self) -> CustomMetricThreshold:
        return CustomMetricThreshold(
            metric=self.metric_name,
            threshold=MonitoringThreshold(value=self.threshold) if self.threshold is not None else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: CustomMetricThreshold) -> "CustomMonitoringMetricThreshold":
        return cls(metric_name=obj.metric, threshold=obj.threshold.value if obj.threshold else None)

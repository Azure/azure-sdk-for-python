# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument, line-too-long

from typing import Any, Dict, List, Optional

from typing_extensions import Literal

from azure.ai.ml.constants._monitoring import MonitorMetricName, MonitorFeatureType, MonitorModelType
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
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
    GenerationSafetyQualityMetricThreshold,
)
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml._utils._experimental import experimental


@experimental
class MetricThreshold(RestTranslatableMixin):
    def __init__(self, *, threshold: float = None):
        self.data_type = None
        self.metric_name = None
        self.threshold = threshold


@experimental
class NumericalDriftMetrics(RestTranslatableMixin):
    def __init__(
        self,
        *,
        jensen_shannon_distance: float = None,
        normalized_wasserstein_distance: float = None,
        population_stability_index: float = None,
        two_sample_kolmogorov_smirnov_test: float = None,
        metric: Optional[str] = None,
        metric_threshold: Optional[float] = None,
    ):
        self.jensen_shannon_distance = jensen_shannon_distance
        self.normalized_wasserstein_distance = normalized_wasserstein_distance
        self.population_stability_index = population_stability_index
        self.two_sample_kolmogorov_smirnov_test = two_sample_kolmogorov_smirnov_test
        self.metric = metric
        self.metric_threshold = metric_threshold

    def _find_name_and_threshold(self):
        metric_name = None
        threshold = None
        if self.jensen_shannon_distance:
            metric_name = MonitorMetricName.JENSEN_SHANNON_DISTANCE
            threshold = MonitoringThreshold(value=self.jensen_shannon_distance)
        elif self.normalized_wasserstein_distance:
            metric_name = MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE
            threshold = MonitoringThreshold(value=self.normalized_wasserstein_distance)
        elif self.population_stability_index:
            metric_name = MonitorMetricName.POPULATION_STABILITY_INDEX
            threshold = MonitoringThreshold(value=self.population_stability_index)
        elif self.two_sample_kolmogorov_smirnov_test:
            metric_name = MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST
            threshold = MonitoringThreshold(value=self.two_sample_kolmogorov_smirnov_test)

        return metric_name, threshold

    @classmethod
    def _from_rest_object(  # pylint: disable=arguments-differ, inconsistent-return-statements
        cls, metric_name, threshold
    ) -> "NumericalDriftMetrics":
        metric_name = camel_to_snake(metric_name)
        if metric_name == MonitorMetricName.JENSEN_SHANNON_DISTANCE:
            return cls(jensen_shannon_distance=threshold)
        if metric_name == MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE:
            return cls(normalized_wasserstein_distance=threshold)
        if metric_name == MonitorMetricName.POPULATION_STABILITY_INDEX:
            return cls(population_stability_index=threshold)
        if metric_name == MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST:
            return cls(two_sample_kolmogorov_smirnov_test=threshold)

    @classmethod
    def _get_default_thresholds(cls) -> "NumericalDriftMetrics":
        return cls(
            normalized_wasserstein_distance=0.1,
        )

    @classmethod
    def defaults(cls) -> "NumericalDriftMetrics":
        return cls._get_default_thresholds()

    def get_name_and_threshold(self):
        return self._find_name_and_threshold()


@experimental
class CategoricalDriftMetrics(RestTranslatableMixin):
    def __init__(
        self,
        *,
        jensen_shannon_distance: float = None,
        population_stability_index: float = None,
        pearsons_chi_squared_test: float = None,
    ):
        self.jensen_shannon_distance = jensen_shannon_distance
        self.population_stability_index = population_stability_index
        self.pearsons_chi_squared_test = pearsons_chi_squared_test

    def _find_name_and_threshold(self):
        metric_name = None
        threshold = None
        if self.jensen_shannon_distance:
            metric_name = MonitorMetricName.JENSEN_SHANNON_DISTANCE
            threshold = MonitoringThreshold(value=self.jensen_shannon_distance)
        if self.population_stability_index and threshold is None:
            metric_name = MonitorMetricName.POPULATION_STABILITY_INDEX
            threshold = MonitoringThreshold(value=self.population_stability_index)
        if self.pearsons_chi_squared_test and threshold is None:
            metric_name = MonitorMetricName.PEARSONS_CHI_SQUARED_TEST
            threshold = MonitoringThreshold(value=self.pearsons_chi_squared_test)

        return metric_name, threshold

    @classmethod
    def _from_rest_object(  # pylint: disable=arguments-differ, inconsistent-return-statements
        cls, metric_name, threshold
    ) -> "CategoricalDriftMetrics":
        metric_name = camel_to_snake(metric_name)
        if metric_name == MonitorMetricName.JENSEN_SHANNON_DISTANCE:
            return cls(jensen_shannon_distance=threshold)
        if metric_name == MonitorMetricName.POPULATION_STABILITY_INDEX:
            return cls(population_stability_index=threshold)
        if metric_name == MonitorMetricName.PEARSONS_CHI_SQUARED_TEST:
            return cls(pearsons_chi_squared_test=threshold)

    @classmethod
    def _get_default_thresholds(cls) -> "CategoricalDriftMetrics":
        return cls(
            jensen_shannon_distance=0.1,
        )

    @classmethod
    def defaults(cls) -> "CategoricalDriftMetrics":
        return cls._get_default_thresholds()

    def get_name_and_threshold(self):
        return self._find_name_and_threshold()


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
        data_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL] = None,
        threshold: float = None,
        metric: Optional[str] = None,
        numerical: NumericalDriftMetrics = None,
        categorical: CategoricalDriftMetrics = None,
    ):
        super().__init__(threshold=threshold)
        self.data_type = data_type
        self.metric = metric
        self.numerical = numerical
        self.categorical = categorical

    def _to_rest_object(self) -> DataDriftMetricThresholdBase:
        thresholds = []
        if self.numerical:
            num_metric_name, num_threshold = self.numerical.get_name_and_threshold()
            thresholds.append(
                NumericalDataDriftMetricThreshold(
                    metric=snake_to_camel(num_metric_name),
                    threshold=num_threshold,
                )
            )
        if self.categorical:
            cat_metric_name, cat_threshold = self.categorical.get_name_and_threshold()
            thresholds.append(
                CategoricalDataDriftMetricThreshold(
                    metric=snake_to_camel(cat_metric_name),
                    threshold=cat_threshold,
                )
            )

        return thresholds

    @classmethod
    def _from_rest_object(cls, obj: DataDriftMetricThresholdBase) -> "DataDriftMetricThreshold":
        num = None
        cat = None
        for threshold in obj:
            if threshold.data_type == "Numerical":
                num = NumericalDriftMetrics()._from_rest_object(  # pylint: disable=protected-access
                    threshold.metric, threshold.threshold.value if threshold.threshold else None
                )
            elif threshold.data_type == "Categorical":
                cat = CategoricalDriftMetrics()._from_rest_object(  # pylint: disable=protected-access
                    threshold.metric, threshold.threshold.value if threshold.threshold else None
                )

        return cls(
            numerical=num,
            categorical=cat,
        )

    @classmethod
    def _get_default_thresholds(cls) -> "DataDriftMetricThreshold":
        return cls(
            numerical=NumericalDriftMetrics.defaults(),
            categorical=CategoricalDriftMetrics.defaults(),
        )

    def __eq__(self, other: Any):
        if not isinstance(other, DataDriftMetricThreshold):
            return NotImplemented
        return self.numerical == other.numerical and self.categorical == other.categorical


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
        data_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL] = None,
        threshold: float = None,
        numerical: NumericalDriftMetrics = None,
        categorical: CategoricalDriftMetrics = None,
    ):
        super().__init__(threshold=threshold)
        self.data_type = data_type
        self.numerical = numerical
        self.categorical = categorical

    def _to_rest_object(self) -> PredictionDriftMetricThresholdBase:
        thresholds = []
        if self.numerical:
            num_metric_name, num_threshold = self.numerical.get_name_and_threshold()
            thresholds.append(
                NumericalPredictionDriftMetricThreshold(
                    metric=snake_to_camel(num_metric_name),
                    threshold=num_threshold,
                )
            )
        if self.categorical:
            cat_metric_name, cat_threshold = self.categorical.get_name_and_threshold()
            thresholds.append(
                CategoricalPredictionDriftMetricThreshold(
                    metric=snake_to_camel(cat_metric_name),
                    threshold=cat_threshold,
                )
            )

        return thresholds

    @classmethod
    def _from_rest_object(cls, obj: PredictionDriftMetricThresholdBase) -> "PredictionDriftMetricThreshold":
        num = None
        cat = None
        for threshold in obj:
            if threshold.data_type == "Numerical":
                num = NumericalDriftMetrics()._from_rest_object(  # pylint: disable=protected-access
                    threshold.metric, threshold.threshold.value if threshold.threshold else None
                )
            elif threshold.data_type == "Categorical":
                cat = CategoricalDriftMetrics()._from_rest_object(  # pylint: disable=protected-access
                    threshold.metric, threshold.threshold.value if threshold.threshold else None
                )

        return cls(
            numerical=num,
            categorical=cat,
        )

    @classmethod
    def _get_default_thresholds(cls) -> "PredictionDriftMetricThreshold":
        return cls(
            numerical=NumericalDriftMetrics.defaults(),
            categorical=CategoricalDriftMetrics.defaults(),
        )

    def __eq__(self, other: Any):
        if not isinstance(other, PredictionDriftMetricThreshold):
            return NotImplemented
        return (
            self.data_type == other.data_type
            and self.metric_name == other.metric_name
            and self.threshold == other.threshold
        )


@experimental
class DataQualityMetricsNumerical(RestTranslatableMixin):
    def __init__(
        self, *, null_value_rate: float = None, data_type_error_rate: float = None, out_of_bounds_rate: float = None
    ):
        self.null_value_rate = null_value_rate
        self.data_type_error_rate = data_type_error_rate
        self.out_of_bounds_rate = out_of_bounds_rate

    def _to_rest_object(self) -> List[NumericalDataQualityMetricThreshold]:
        metric_thresholds = []
        if self.null_value_rate is not None:
            metric_name = MonitorMetricName.NULL_VALUE_RATE
            threshold = MonitoringThreshold(value=self.null_value_rate)
            metric_thresholds.append(
                NumericalDataQualityMetricThreshold(metric=snake_to_camel(metric_name), threshold=threshold)
            )
        if self.data_type_error_rate is not None:
            metric_name = MonitorMetricName.DATA_TYPE_ERROR_RATE
            threshold = MonitoringThreshold(value=self.data_type_error_rate)
            metric_thresholds.append(
                NumericalDataQualityMetricThreshold(metric=snake_to_camel(metric_name), threshold=threshold)
            )
        if self.out_of_bounds_rate is not None:
            metric_name = MonitorMetricName.OUT_OF_BOUND_RATE
            threshold = MonitoringThreshold(value=self.out_of_bounds_rate)
            metric_thresholds.append(
                NumericalDataQualityMetricThreshold(metric=snake_to_camel(metric_name), threshold=threshold)
            )

        return metric_thresholds

    @classmethod
    def _from_rest_object(cls, obj: List) -> "DataQualityMetricsNumerical":
        null_value_rate_val = None
        data_type_error_rate_val = None
        out_of_bounds_rate_val = None
        for thresholds in obj:
            if thresholds.metric == "nullValueRate":
                null_value_rate_val = thresholds.threshold.value
            if thresholds.metric == "dataTypeErrorRate":
                data_type_error_rate_val = thresholds.threshold.value
            if thresholds.metric == "outOfBoundsRate":
                out_of_bounds_rate_val = thresholds.threshold.value
        return cls(
            null_value_rate=null_value_rate_val,
            data_type_error_rate=data_type_error_rate_val,
            out_of_bounds_rate=out_of_bounds_rate_val,
        )

    @classmethod
    def _get_default_thresholds(cls) -> "DataQualityMetricsNumerical":
        return cls(
            null_value_rate=0.0,
            data_type_error_rate=0.0,
            out_of_bounds_rate=0.0,
        )

    @classmethod
    def defaults(cls) -> "DataQualityMetricsNumerical":
        return cls._get_default_thresholds()


@experimental
class DataQualityMetricsCategorical(RestTranslatableMixin):
    def __init__(
        self, *, null_value_rate: float = None, data_type_error_rate: float = None, out_of_bounds_rate: float = None
    ):
        self.null_value_rate = null_value_rate
        self.data_type_error_rate = data_type_error_rate
        self.out_of_bounds_rate = out_of_bounds_rate

    def _to_rest_object(self) -> List[CategoricalDataQualityMetricThreshold]:
        metric_thresholds = []
        if self.null_value_rate is not None:
            metric_name = MonitorMetricName.NULL_VALUE_RATE
            threshold = MonitoringThreshold(value=self.null_value_rate)
            metric_thresholds.append(
                CategoricalDataQualityMetricThreshold(metric=snake_to_camel(metric_name), threshold=threshold)
            )
        if self.data_type_error_rate is not None:
            metric_name = MonitorMetricName.DATA_TYPE_ERROR_RATE
            threshold = MonitoringThreshold(value=self.data_type_error_rate)
            metric_thresholds.append(
                CategoricalDataQualityMetricThreshold(metric=snake_to_camel(metric_name), threshold=threshold)
            )
        if self.out_of_bounds_rate is not None:
            metric_name = MonitorMetricName.OUT_OF_BOUND_RATE
            threshold = MonitoringThreshold(value=self.out_of_bounds_rate)
            metric_thresholds.append(
                CategoricalDataQualityMetricThreshold(metric=snake_to_camel(metric_name), threshold=threshold)
            )

        return metric_thresholds

    @classmethod
    def _from_rest_object(cls, obj: List) -> "DataQualityMetricsCategorical":
        null_value_rate_val = None
        data_type_error_rate_val = None
        out_of_bounds_rate_val = None
        for thresholds in obj:
            if thresholds.metric == "nullValueRate":
                null_value_rate_val = thresholds.threshold.value
            if thresholds.metric == "dataTypeErrorRate":
                data_type_error_rate_val = thresholds.threshold.value
            if thresholds.metric == "outOfBoundsRate":
                out_of_bounds_rate_val = thresholds.threshold.value
        return cls(
            null_value_rate=null_value_rate_val,
            data_type_error_rate=data_type_error_rate_val,
            out_of_bounds_rate=out_of_bounds_rate_val,
        )

    @classmethod
    def _get_default_thresholds(cls) -> "DataQualityMetricsCategorical":
        return cls(
            null_value_rate="0.0",
            data_type_error_rate=0.0,
            out_of_bounds_rate=0.0,
        )

    @classmethod
    def defaults(cls) -> "DataQualityMetricsCategorical":
        return cls._get_default_thresholds()


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
        data_type: Literal[MonitorFeatureType.CATEGORICAL, MonitorFeatureType.NUMERICAL] = None,
        threshold: float = None,
        metric_name: Optional[str] = None,
        numerical: Optional[DataQualityMetricsNumerical] = None,
        categorical: Optional[DataQualityMetricsCategorical] = None,
    ):
        super().__init__(threshold=threshold)
        self.data_type = data_type
        self.metric_name = metric_name
        self.numerical = numerical
        self.categorical = categorical

    def _to_rest_object(self) -> DataQualityMetricThresholdBase:
        thresholds = []
        if self.numerical:
            thresholds = thresholds + (
                DataQualityMetricsNumerical(  # pylint: disable=protected-access
                    null_value_rate=self.numerical.null_value_rate,
                    data_type_error_rate=self.numerical.data_type_error_rate,
                    out_of_bounds_rate=self.numerical.out_of_bounds_rate,
                )._to_rest_object()
            )
        if self.categorical:
            thresholds = thresholds + (
                DataQualityMetricsCategorical(  # pylint: disable=protected-access
                    null_value_rate=self.numerical.null_value_rate,
                    data_type_error_rate=self.numerical.data_type_error_rate,
                    out_of_bounds_rate=self.numerical.out_of_bounds_rate,
                )._to_rest_object()
            )
        return thresholds

    @classmethod
    def _from_rest_object(cls, obj: DataQualityMetricThresholdBase) -> "DataQualityMetricThreshold":
        num = []
        cat = []
        for threshold in obj:
            if threshold.data_type == "Numerical":
                num.append(threshold)
            elif threshold.data_type == "Categorical":
                cat.append(threshold)

        num_from_rest = DataQualityMetricsNumerical()._from_rest_object(num)  # pylint: disable=protected-access
        cat_from_rest = DataQualityMetricsCategorical()._from_rest_object(cat)  # pylint: disable=protected-access
        return cls(
            numerical=num_from_rest,
            categorical=cat_from_rest,
        )

    @classmethod
    def _get_default_thresholds(cls) -> "DataQualityMetricThreshold":
        return cls(
            numerical=DataQualityMetricsNumerical()._get_default_thresholds(),  # pylint: disable=protected-access
            categorical=DataQualityMetricsCategorical()._get_default_thresholds(),  # pylint: disable=protected-access
        )

    def __eq__(self, other: Any):
        if not isinstance(other, DataQualityMetricThreshold):
            return NotImplemented
        return (
            self.data_type == other.data_type
            and self.metric_name == other.metric_name
            and self.threshold == other.threshold
        )


@experimental
class FeatureAttributionDriftMetricThreshold(MetricThreshold):
    """Feature attribution drift metric threshold

    :param normalized_discounted_cumulative_gain: The threshold value for metric.
    :type normalized_discounted_cumulative_gain: float
    """

    def __init__(self, *, normalized_discounted_cumulative_gain: float = None, threshold: float = None):
        super().__init__(threshold=threshold)
        self.data_type = MonitorFeatureType.ALL_FEATURE_TYPES
        self.metric_name = MonitorMetricName.NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN
        self.normalized_discounted_cumulative_gain = normalized_discounted_cumulative_gain

    def _to_rest_object(self) -> FeatureAttributionMetricThreshold:
        return FeatureAttributionMetricThreshold(
            metric=snake_to_camel(self.metric_name),
            threshold=MonitoringThreshold(value=self.normalized_discounted_cumulative_gain)
            if self.normalized_discounted_cumulative_gain
            else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: FeatureAttributionMetricThreshold) -> "FeatureAttributionDriftMetricThreshold":
        return cls(normalized_discounted_cumulative_gain=obj.threshold.value if obj.threshold else None)


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


@experimental
class GenerationSafetyQualityMonitoringMetricThreshold(RestTranslatableMixin):  # pylint: disable=name-too-long
    """Generation safety quality metric threshold

    :keyword groundedness: The groundedness metric threshold
    :paramtype groundedness: Dict[str, float]
    :keyword relevance: The relevance metric threshold
    :paramtype relevance: Dict[str, float]
    :keyword coherence: The coherence metric threshold
    :paramtype coherence: Dict[str, float]
    :keyword fluency: The fluency metric threshold
    :paramtype fluency: Dict[str, float]
    :keyword similarity: The similarity metric threshold
    :paramtype similarity: Dict[str, float]
    """

    def __init__(
        self,
        *,
        groundedness: Dict[str, float] = None,
        relevance: Dict[str, float] = None,
        coherence: Dict[str, float] = None,
        fluency: Dict[str, float] = None,
        similarity: Dict[str, float] = None,
    ):
        self.groundedness = groundedness
        self.relevance = relevance
        self.coherence = coherence
        self.fluency = fluency
        self.similarity = similarity

    def _to_rest_object(self) -> GenerationSafetyQualityMetricThreshold:
        metric_thresholds = []
        if self.groundedness:
            if "acceptable_groundedness_score_per_instance" in self.groundedness:
                acceptable_threshold = MonitoringThreshold(
                    value=self.groundedness["acceptable_groundedness_score_per_instance"]
                )
            else:
                acceptable_threshold = MonitoringThreshold(value=3)
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AcceptableGroundednessScorePerInstance", threshold=acceptable_threshold
                )
            )
            aggregated_threshold = MonitoringThreshold(value=self.groundedness["aggregated_groundedness_pass_rate"])
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AggregatedGroundednessPassRate", threshold=aggregated_threshold
                )
            )
        if self.relevance:
            if "acceptable_relevance_score_per_instance" in self.relevance:
                acceptable_threshold = MonitoringThreshold(
                    value=self.relevance["acceptable_relevance_score_per_instance"]
                )
            else:
                acceptable_threshold = MonitoringThreshold(value=3)
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AcceptableRelevanceScorePerInstance", threshold=acceptable_threshold
                )
            )
            aggregated_threshold = MonitoringThreshold(value=self.relevance["aggregated_relevance_pass_rate"])
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AggregatedRelevancePassRate", threshold=aggregated_threshold
                )
            )
        if self.coherence:
            if "acceptable_coherence_score_per_instance" in self.coherence:
                acceptable_threshold = MonitoringThreshold(
                    value=self.coherence["acceptable_coherence_score_per_instance"]
                )
            else:
                acceptable_threshold = MonitoringThreshold(value=3)
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AcceptableCoherenceScorePerInstance", threshold=acceptable_threshold
                )
            )
            aggregated_threshold = MonitoringThreshold(value=self.coherence["aggregated_coherence_pass_rate"])
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AggregatedCoherencePassRate", threshold=aggregated_threshold
                )
            )
        if self.fluency:
            if "acceptable_fluency_score_per_instance" in self.fluency:
                acceptable_threshold = MonitoringThreshold(value=self.fluency["acceptable_fluency_score_per_instance"])
            else:
                acceptable_threshold = MonitoringThreshold(value=3)
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AcceptableFluencyScorePerInstance", threshold=acceptable_threshold
                )
            )
            aggregated_threshold = MonitoringThreshold(value=self.fluency["aggregated_fluency_pass_rate"])
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AggregatedFluencyPassRate", threshold=aggregated_threshold
                )
            )
        if self.similarity:
            if "acceptable_similarity_score_per_instance" in self.similarity:
                acceptable_threshold = MonitoringThreshold(
                    value=self.similarity["acceptable_similarity_score_per_instance"]
                )
            else:
                acceptable_threshold = MonitoringThreshold(value=3)
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AcceptableSimilarityScorePerInstance", threshold=acceptable_threshold
                )
            )
            aggregated_threshold = MonitoringThreshold(value=self.similarity["aggregated_similarity_pass_rate"])
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="AggregatedSimilarityPassRate", threshold=aggregated_threshold
                )
            )
        return metric_thresholds

    @classmethod
    def _from_rest_object(
        cls, obj: GenerationSafetyQualityMetricThreshold
    ) -> "GenerationSafetyQualityMonitoringMetricThreshold":
        groundedness = {}
        relevance = {}
        coherence = {}
        fluency = {}
        similarity = {}

        for threshold in obj:
            if threshold.metric == "AcceptableGroundednessScorePerInstance":
                groundedness["acceptable_groundedness_score_per_instance"] = threshold.threshold.value
            if threshold.metric == "AcceptableRelevanceScorePerInstance":
                relevance["acceptable_relevance_score_per_instance"] = threshold.threshold.value
            if threshold.metric == "AcceptableCoherenceScorePerInstance":
                coherence["acceptable_coherence_score_per_instance"] = threshold.threshold.value
            if threshold.metric == "AcceptableFluencyScorePerInstance":
                fluency["acceptable_fluency_score_per_instance"] = threshold.threshold.value
            if threshold.metric == "AcceptableSimilarityScorePerInstance":
                similarity["acceptable_similarity_score_per_instance"] = threshold.threshold.value
            if threshold.metric == "AggregatedGroundednessPassRate":
                groundedness["aggregated_groundedness_pass_rate"] = threshold.threshold.value
            if threshold.metric == "AggregatedRelevancePassRate":
                relevance["aggregated_relevance_pass_rate"] = threshold.threshold.value
            if threshold.metric == "AggregatedCoherencePassRate":
                coherence["aggregated_coherence_pass_rate"] = threshold.threshold.value
            if threshold.metric == "AggregatedFluencyPassRate":
                fluency["aggregated_fluency_pass_rate"] = threshold.threshold.value
            if threshold.metric == "AggregatedSimilarityPassRate":
                similarity["aggregated_similarity_pass_rate"] = threshold.threshold.value

        return cls(
            groundedness=groundedness if groundedness else None,
            relevance=relevance if relevance else None,
            coherence=coherence if coherence else None,
            fluency=fluency if fluency else None,
            similarity=similarity if similarity else None,
        )

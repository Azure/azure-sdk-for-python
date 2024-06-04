# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument, line-too-long, protected-access

from typing import Any, Dict, List, Optional, Tuple

from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    CategoricalDataDriftMetricThreshold,
    CategoricalDataQualityMetricThreshold,
    CategoricalPredictionDriftMetricThreshold,
    ClassificationModelPerformanceMetricThreshold,
    CustomMetricThreshold,
    DataDriftMetricThresholdBase,
    DataQualityMetricThresholdBase,
    FeatureAttributionMetricThreshold,
    GenerationSafetyQualityMetricThreshold,
    GenerationTokenStatisticsMetricThreshold,
    ModelPerformanceMetricThresholdBase,
    MonitoringThreshold,
    NumericalDataDriftMetricThreshold,
    NumericalDataQualityMetricThreshold,
    NumericalPredictionDriftMetricThreshold,
    PredictionDriftMetricThresholdBase,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.constants._monitoring import MonitorFeatureType, MonitorMetricName
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class MetricThreshold(RestTranslatableMixin):
    def __init__(self, *, threshold: Optional[float] = None):
        self.data_type: Any = None
        self.metric_name: Optional[str] = None
        self.threshold = threshold


class NumericalDriftMetrics(RestTranslatableMixin):
    """Numerical Drift Metrics

    :param jensen_shannon_distance: The Jensen-Shannon distance between the two distributions
    :paramtype jensen_shannon_distance: float
    :param normalized_wasserstein_distance: The normalized Wasserstein distance between the two distributions
    :paramtype normalized_wasserstein_distance: float
    :param population_stability_index: The population stability index between the two distributions
    :paramtype population_stability_index: float
    :param two_sample_kolmogorov_smirnov_test: The two sample Kolmogorov-Smirnov test between the two distributions
    :paramtype two_sample_kolmogorov_smirnov_test: float
    """

    def __init__(
        self,
        *,
        jensen_shannon_distance: Optional[float] = None,
        normalized_wasserstein_distance: Optional[float] = None,
        population_stability_index: Optional[float] = None,
        two_sample_kolmogorov_smirnov_test: Optional[float] = None,
        metric: Optional[str] = None,
        metric_threshold: Optional[float] = None,
    ):
        self.jensen_shannon_distance = jensen_shannon_distance
        self.normalized_wasserstein_distance = normalized_wasserstein_distance
        self.population_stability_index = population_stability_index
        self.two_sample_kolmogorov_smirnov_test = two_sample_kolmogorov_smirnov_test
        self.metric = metric
        self.metric_threshold = metric_threshold

    def _find_name_and_threshold(self) -> Tuple:
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
    # pylint: disable=arguments-differ, inconsistent-return-statements
    def _from_rest_object(cls, metric_name: str, threshold: Optional[float]) -> "NumericalDriftMetrics":  # type: ignore
        metric_name = camel_to_snake(metric_name)
        if metric_name == MonitorMetricName.JENSEN_SHANNON_DISTANCE:
            return cls(jensen_shannon_distance=threshold)
        if metric_name == MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE:
            return cls(normalized_wasserstein_distance=threshold)
        if metric_name == MonitorMetricName.POPULATION_STABILITY_INDEX:
            return cls(population_stability_index=threshold)
        if metric_name == MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST:
            return cls(two_sample_kolmogorov_smirnov_test=threshold)
        return cls()

    @classmethod
    def _get_default_thresholds(cls) -> "NumericalDriftMetrics":
        return cls(
            normalized_wasserstein_distance=0.1,
        )


class CategoricalDriftMetrics(RestTranslatableMixin):
    """Categorical Drift Metrics

    :param jensen_shannon_distance: The Jensen-Shannon distance between the two distributions
    :paramtype jensen_shannon_distance: float
    :param population_stability_index: The population stability index between the two distributions
    :paramtype population_stability_index: float
    :param pearsons_chi_squared_test: The Pearson's Chi-Squared test between the two distributions
    :paramtype pearsons_chi_squared_test: float
    """

    def __init__(
        self,
        *,
        jensen_shannon_distance: Optional[float] = None,
        population_stability_index: Optional[float] = None,
        pearsons_chi_squared_test: Optional[float] = None,
    ):
        self.jensen_shannon_distance = jensen_shannon_distance
        self.population_stability_index = population_stability_index
        self.pearsons_chi_squared_test = pearsons_chi_squared_test

    def _find_name_and_threshold(self) -> Tuple:
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
    # pylint: disable=arguments-differ, inconsistent-return-statements
    def _from_rest_object(  # type: ignore
        cls, metric_name: str, threshold: Optional[float]
    ) -> "CategoricalDriftMetrics":
        metric_name = camel_to_snake(metric_name)
        if metric_name == MonitorMetricName.JENSEN_SHANNON_DISTANCE:
            return cls(jensen_shannon_distance=threshold)
        if metric_name == MonitorMetricName.POPULATION_STABILITY_INDEX:
            return cls(population_stability_index=threshold)
        if metric_name == MonitorMetricName.PEARSONS_CHI_SQUARED_TEST:
            return cls(pearsons_chi_squared_test=threshold)
        return cls()

    @classmethod
    def _get_default_thresholds(cls) -> "CategoricalDriftMetrics":
        return cls(
            jensen_shannon_distance=0.1,
        )


class DataDriftMetricThreshold(MetricThreshold):
    """Data drift metric threshold

    :param numerical: Numerical drift metrics
    :paramtype numerical: ~azure.ai.ml.entities.NumericalDriftMetrics
    :param categorical: Categorical drift metrics
    :paramtype categorical: ~azure.ai.ml.entities.CategoricalDriftMetrics
    """

    def __init__(
        self,
        *,
        data_type: Optional[MonitorFeatureType] = None,
        threshold: Optional[float] = None,
        metric: Optional[str] = None,
        numerical: Optional[NumericalDriftMetrics] = None,
        categorical: Optional[CategoricalDriftMetrics] = None,
    ):
        super().__init__(threshold=threshold)
        self.data_type = data_type
        self.metric = metric
        self.numerical = numerical
        self.categorical = categorical

    def _to_rest_object(self) -> DataDriftMetricThresholdBase:
        thresholds = []
        if self.numerical:
            num_metric_name, num_threshold = self.numerical._find_name_and_threshold()
            thresholds.append(
                NumericalDataDriftMetricThreshold(
                    metric=snake_to_camel(num_metric_name),
                    threshold=num_threshold,
                )
            )
        if self.categorical:
            cat_metric_name, cat_threshold = self.categorical._find_name_and_threshold()
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
            numerical=NumericalDriftMetrics._get_default_thresholds(),
            categorical=CategoricalDriftMetrics._get_default_thresholds(),
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DataDriftMetricThreshold):
            return NotImplemented
        return self.numerical == other.numerical and self.categorical == other.categorical


class PredictionDriftMetricThreshold(MetricThreshold):
    """Prediction drift metric threshold

    :param numerical: Numerical drift metrics
    :paramtype numerical: ~azure.ai.ml.entities.NumericalDriftMetrics
    :param categorical: Categorical drift metrics
    :paramtype categorical: ~azure.ai.ml.entities.CategoricalDriftMetrics
    """

    def __init__(
        self,
        *,
        data_type: Optional[MonitorFeatureType] = None,
        threshold: Optional[float] = None,
        numerical: Optional[NumericalDriftMetrics] = None,
        categorical: Optional[CategoricalDriftMetrics] = None,
    ):
        super().__init__(threshold=threshold)
        self.data_type = data_type
        self.numerical = numerical
        self.categorical = categorical

    def _to_rest_object(self) -> PredictionDriftMetricThresholdBase:
        thresholds = []
        if self.numerical:
            num_metric_name, num_threshold = self.numerical._find_name_and_threshold()
            thresholds.append(
                NumericalPredictionDriftMetricThreshold(
                    metric=snake_to_camel(num_metric_name),
                    threshold=num_threshold,
                )
            )
        if self.categorical:
            cat_metric_name, cat_threshold = self.categorical._find_name_and_threshold()
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
            numerical=NumericalDriftMetrics._get_default_thresholds(),
            categorical=CategoricalDriftMetrics._get_default_thresholds(),
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PredictionDriftMetricThreshold):
            return NotImplemented
        return (
            self.data_type == other.data_type
            and self.metric_name == other.metric_name
            and self.threshold == other.threshold
        )


class DataQualityMetricsNumerical(RestTranslatableMixin):
    """Data Quality Numerical Metrics

    :param null_value_rate: The null value rate
    :paramtype null_value_rate: float
    :param data_type_error_rate: The data type error rate
    :paramtype data_type_error_rate: float
    :param out_of_bounds_rate: The out of bounds rate
    :paramtype out_of_bounds_rate: float
    """

    def __init__(
        self,
        *,
        null_value_rate: Optional[float] = None,
        data_type_error_rate: Optional[float] = None,
        out_of_bounds_rate: Optional[float] = None,
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
            if thresholds.metric in ("NullValueRate" "nullValueRate"):
                null_value_rate_val = thresholds.threshold.value
            if thresholds.metric in ("DataTypeErrorRate", "dataTypeErrorRate"):
                data_type_error_rate_val = thresholds.threshold.value
            if thresholds.metric in ("OutOfBoundsRate", "outOfBoundsRate"):
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


class DataQualityMetricsCategorical(RestTranslatableMixin):
    """Data Quality Categorical Metrics

    :param null_value_rate: The null value rate
    :paramtype null_value_rate: float
    :param data_type_error_rate: The data type error rate
    :paramtype data_type_error_rate: float
    :param out_of_bounds_rate: The out of bounds rate
    :paramtype out_of_bounds_rate: float
    """

    def __init__(
        self,
        *,
        null_value_rate: Optional[float] = None,
        data_type_error_rate: Optional[float] = None,
        out_of_bounds_rate: Optional[float] = None,
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
            if thresholds.metric in ("NullValueRate" "nullValueRate"):
                null_value_rate_val = thresholds.threshold.value
            if thresholds.metric in ("DataTypeErrorRate", "dataTypeErrorRate"):
                data_type_error_rate_val = thresholds.threshold.value
            if thresholds.metric in ("OutOfBoundsRate", "outOfBoundsRate"):
                out_of_bounds_rate_val = thresholds.threshold.value
        return cls(
            null_value_rate=null_value_rate_val,
            data_type_error_rate=data_type_error_rate_val,
            out_of_bounds_rate=out_of_bounds_rate_val,
        )

    @classmethod
    def _get_default_thresholds(cls) -> "DataQualityMetricsCategorical":
        return cls(
            null_value_rate=0.0,
            data_type_error_rate=0.0,
            out_of_bounds_rate=0.0,
        )


class DataQualityMetricThreshold(MetricThreshold):
    """Data quality metric threshold

    :param numerical: Numerical data quality metrics
    :paramtype numerical: ~azure.ai.ml.entities.DataQualityMetricsNumerical
    :param categorical: Categorical data quality metrics
    :paramtype categorical: ~azure.ai.ml.entities.DataQualityMetricsCategorical
    """

    def __init__(
        self,
        *,
        data_type: Optional[MonitorFeatureType] = None,
        threshold: Optional[float] = None,
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
        thresholds: list = []
        if self.numerical:
            thresholds = thresholds + (
                DataQualityMetricsNumerical(  # pylint: disable=protected-access
                    null_value_rate=self.numerical.null_value_rate,
                    data_type_error_rate=self.numerical.data_type_error_rate,
                    out_of_bounds_rate=self.numerical.out_of_bounds_rate,
                )._to_rest_object()
            )
        if self.categorical:
            thresholds = (
                thresholds
                + (
                    DataQualityMetricsCategorical(  # pylint: disable=protected-access
                        null_value_rate=self.numerical.null_value_rate,
                        data_type_error_rate=self.numerical.data_type_error_rate,
                        out_of_bounds_rate=self.numerical.out_of_bounds_rate,
                    )._to_rest_object()
                )
                if self.numerical is not None
                else thresholds
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

    def __eq__(self, other: Any) -> bool:
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
    :paramtype normalized_discounted_cumulative_gain: float
    """

    def __init__(
        self, *, normalized_discounted_cumulative_gain: Optional[float] = None, threshold: Optional[float] = None
    ):
        super().__init__(threshold=threshold)
        self.data_type = MonitorFeatureType.ALL_FEATURE_TYPES
        self.metric_name = MonitorMetricName.NORMALIZED_DISCOUNTED_CUMULATIVE_GAIN
        self.normalized_discounted_cumulative_gain = normalized_discounted_cumulative_gain

    def _to_rest_object(self) -> FeatureAttributionMetricThreshold:
        return FeatureAttributionMetricThreshold(
            metric=snake_to_camel(self.metric_name),
            threshold=(
                MonitoringThreshold(value=self.normalized_discounted_cumulative_gain)
                if self.normalized_discounted_cumulative_gain
                else None
            ),
        )

    @classmethod
    def _from_rest_object(cls, obj: FeatureAttributionMetricThreshold) -> "FeatureAttributionDriftMetricThreshold":
        return cls(normalized_discounted_cumulative_gain=obj.threshold.value if obj.threshold else None)


@experimental
class ModelPerformanceClassificationThresholds(RestTranslatableMixin):
    def __init__(
        self,
        *,
        accuracy: Optional[float] = None,
        precision: Optional[float] = None,
        recall: Optional[float] = None,
    ):
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall

    def _to_str_object(self, **kwargs):
        thresholds = []
        if self.accuracy:
            thresholds.append(
                '{"modelType":"classification","metric":"Accuracy","threshold":{"value":' + f"{self.accuracy}" + "}}"
            )
        if self.precision:
            thresholds.append(
                '{"modelType":"classification","metric":"Precision","threshold":{"value":' + f"{self.precision}" + "}}"
            )
        if self.recall:
            thresholds.append(
                '{"modelType":"classification","metric":"Recall","threshold":{"value":' + f"{self.recall}" + "}}"
            )

        if not thresholds:
            return None

        return ", ".join(thresholds)

    @classmethod
    def _from_rest_object(cls, obj) -> "ModelPerformanceClassificationThresholds":
        return cls(
            accuracy=obj.threshold.value if obj.threshold else None,
        )


@experimental
class ModelPerformanceRegressionThresholds(RestTranslatableMixin):
    def __init__(
        self,
        *,
        mean_absolute_error: Optional[float] = None,
        mean_squared_error: Optional[float] = None,
        root_mean_squared_error: Optional[float] = None,
    ):
        self.mean_absolute_error = mean_absolute_error
        self.mean_squared_error = mean_squared_error
        self.root_mean_squared_error = root_mean_squared_error

    def _to_str_object(self, **kwargs):
        thresholds = []
        if self.mean_absolute_error:
            thresholds.append(
                '{"modelType":"regression","metric":"MeanAbsoluteError","threshold":{"value":'
                + f"{self.mean_absolute_error}"
                + "}}"
            )
        if self.mean_squared_error:
            thresholds.append(
                '{"modelType":"regression","metric":"MeanSquaredError","threshold":{"value":'
                + f"{self.mean_squared_error}"
                + "}}"
            )
        if self.root_mean_squared_error:
            thresholds.append(
                '{"modelType":"regression","metric":"RootMeanSquaredError","threshold":{"value":'
                + f"{self.root_mean_squared_error}"
                + "}}"
            )

        if not thresholds:
            return None

        return ", ".join(thresholds)


@experimental
class ModelPerformanceMetricThreshold(RestTranslatableMixin):
    def __init__(
        self,
        *,
        classification: Optional[ModelPerformanceClassificationThresholds] = None,
        regression: Optional[ModelPerformanceRegressionThresholds] = None,
    ):
        self.classification = classification
        self.regression = regression

    def _to_str_object(self, **kwargs):
        thresholds = []
        if self.classification:
            thresholds.append(self.classification._to_str_object(**kwargs))
        if self.regression:
            thresholds.append(self.regression._to_str_object(**kwargs))

        if not thresholds:
            return None
        if len(thresholds) == 2:
            result = "[" + ", ".join(thresholds) + "]"
        else:
            result = "[" + thresholds[0] + "]"
        return result

    def _to_rest_object(self, **kwargs) -> ModelPerformanceMetricThresholdBase:
        threshold = MonitoringThreshold(value=0.9)
        return ClassificationModelPerformanceMetricThreshold(
            metric="Accuracy",
            threshold=threshold,
        )

    @classmethod
    def _from_rest_object(cls, obj: ModelPerformanceMetricThresholdBase) -> "ModelPerformanceMetricThreshold":
        return cls(
            classification=ModelPerformanceClassificationThresholds._from_rest_object(obj),
            regression=None,
        )


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
        metric_name: Optional[str],
        threshold: Optional[float] = None,
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

    :param groundedness: The groundedness metric threshold
    :paramtype groundedness: Dict[str, float]
    :param relevance: The relevance metric threshold
    :paramtype relevance: Dict[str, float]
    :param coherence: The coherence metric threshold
    :paramtype coherence: Dict[str, float]
    :param fluency: The fluency metric threshold
    :paramtype fluency: Dict[str, float]
    :param similarity: The similarity metric threshold
    :paramtype similarity: Dict[str, float]
    """

    def __init__(
        self,
        *,
        groundedness: Optional[Dict[str, float]] = None,
        relevance: Optional[Dict[str, float]] = None,
        coherence: Optional[Dict[str, float]] = None,
        fluency: Optional[Dict[str, float]] = None,
        similarity: Optional[Dict[str, float]] = None,
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


@experimental
class GenerationTokenStatisticsMonitorMetricThreshold(RestTranslatableMixin):  # pylint: disable=name-too-long
    """Generation token statistics metric threshold definition.

    All required parameters must be populated in order to send to Azure.

    :ivar metric: Required. [Required] Gets or sets the feature attribution metric to calculate.
     Possible values include: "TotalTokenCount", "TotalTokenCountPerGroup".
    :vartype metric: str or
     ~azure.mgmt.machinelearningservices.models.GenerationTokenStatisticsMetric
    :ivar threshold: Gets or sets the threshold value.
     If null, a default value will be set depending on the selected metric.
    :vartype threshold: ~azure.mgmt.machinelearningservices.models.MonitoringThreshold
    """

    def __init__(
        self,
        *,
        totaltoken: Optional[Dict[str, float]] = None,
    ):
        self.totaltoken = totaltoken

    def _to_rest_object(self) -> GenerationSafetyQualityMetricThreshold:
        metric_thresholds = []
        if self.totaltoken:
            if "total_token_count" in self.totaltoken:
                acceptable_threshold = MonitoringThreshold(value=self.totaltoken["total_token_count"])
            else:
                acceptable_threshold = MonitoringThreshold(value=3)
            metric_thresholds.append(
                GenerationTokenStatisticsMetricThreshold(metric="TotalTokenCount", threshold=acceptable_threshold)
            )
            acceptable_threshold_per_group = MonitoringThreshold(value=self.totaltoken["total_token_count_per_group"])
            metric_thresholds.append(
                GenerationSafetyQualityMetricThreshold(
                    metric="TotalTokenCountPerGroup", threshold=acceptable_threshold_per_group
                )
            )
        return metric_thresholds

    @classmethod
    def _from_rest_object(
        cls, obj: GenerationTokenStatisticsMetricThreshold
    ) -> "GenerationTokenStatisticsMonitorMetricThreshold":
        totaltoken = {}
        for threshold in obj:
            if threshold.metric == "TotalTokenCount":
                totaltoken["total_token_count"] = threshold.threshold.value
            if threshold.metric == "TotalTokenCountPerGroup":
                totaltoken["total_token_count_per_group"] = threshold.threshold.value

        return cls(
            totaltoken=totaltoken if totaltoken else None,
        )

    @classmethod
    def _get_default_thresholds(cls) -> "GenerationTokenStatisticsMonitorMetricThreshold":
        return cls(totaltoken={"total_token_count": 0, "total_token_count_per_group": 0})

import pytest
import types
from types import SimpleNamespace

from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitoringThreshold,
    FeatureAttributionMetricThreshold,
    ClassificationModelPerformanceMetricThreshold,
    GenerationSafetyQualityMetricThreshold,
    GenerationTokenStatisticsMetricThreshold,
    CustomMetricThreshold,
)
from azure.ai.ml.constants._monitoring import MonitorMetricName
from azure.ai.ml.entities._monitoring.thresholds import (
    NumericalDriftMetrics,
    CategoricalDriftMetrics,
    DataDriftMetricThreshold,
    PredictionDriftMetricThreshold,
    DataQualityMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    ModelPerformanceClassificationThresholds,
    ModelPerformanceRegressionThresholds,
    ModelPerformanceMetricThreshold,
    CustomMonitoringMetricThreshold,
    GenerationSafetyQualityMonitoringMetricThreshold,
    GenerationTokenStatisticsMonitorMetricThreshold,
)

GenerationTokenStatisticsMonitoringMetricThreshold = GenerationTokenStatisticsMonitorMetricThreshold


class _DummyThreshold:
    def __init__(self, metric: str, value: float):
        class _Value:
            pass

        self.metric = metric
        self.threshold = _Value()
        self.threshold.value = value


def test_numerical_drift_metrics_from_rest_jensen_shannon_distance():
    metric = NumericalDriftMetrics._from_rest_object("JensenShannonDistance", 0.5)

    assert metric.jensen_shannon_distance == 0.5
    assert metric.normalized_wasserstein_distance is None
    assert metric.population_stability_index is None
    assert metric.two_sample_kolmogorov_smirnov_test is None


def test_numerical_drift_metrics_from_rest_normalized_wasserstein_distance():
    metric = NumericalDriftMetrics._from_rest_object("NormalizedWassersteinDistance", 0.3)

    assert metric.jensen_shannon_distance is None
    assert metric.normalized_wasserstein_distance == 0.3
    assert metric.population_stability_index is None
    assert metric.two_sample_kolmogorov_smirnov_test is None


def test_numerical_drift_metrics_from_rest_population_stability_index():
    metric = NumericalDriftMetrics._from_rest_object("PopulationStabilityIndex", 0.2)

    assert metric.jensen_shannon_distance is None
    assert metric.normalized_wasserstein_distance is None
    assert metric.population_stability_index == 0.2
    assert metric.two_sample_kolmogorov_smirnov_test is None


def test_numerical_drift_metrics_from_rest_two_sample_ks_test():
    metric = NumericalDriftMetrics._from_rest_object("TwoSampleKolmogorovSmirnovTest", 0.1)

    assert metric.jensen_shannon_distance is None
    assert metric.normalized_wasserstein_distance is None
    assert metric.population_stability_index is None
    assert metric.two_sample_kolmogorov_smirnov_test == 0.1


def test_numerical_drift_metrics_from_rest_unknown_metric_returns_empty():
    metric = NumericalDriftMetrics._from_rest_object("UnknownMetric", 1.0)

    assert metric.jensen_shannon_distance is None
    assert metric.normalized_wasserstein_distance is None
    assert metric.population_stability_index is None
    assert metric.two_sample_kolmogorov_smirnov_test is None


def test_numerical_drift_metrics_get_default_thresholds():
    metric = NumericalDriftMetrics._get_default_thresholds()

    assert metric.normalized_wasserstein_distance == 0.1
    assert metric.jensen_shannon_distance is None
    assert metric.population_stability_index is None
    assert metric.two_sample_kolmogorov_smirnov_test is None


def test_categorical_drift_metrics_find_name_and_threshold_priority_order():
    metrics = CategoricalDriftMetrics(
        jensen_shannon_distance=0.2,
        population_stability_index=0.4,
        pearsons_chi_squared_test=0.6,
    )

    metric_name, threshold = metrics._find_name_and_threshold()

    assert metric_name == MonitorMetricName.JENSEN_SHANNON_DISTANCE
    assert isinstance(threshold, MonitoringThreshold)
    assert threshold.value == 0.2


def test_categorical_drift_metrics_find_name_and_threshold_population_only():
    metrics = CategoricalDriftMetrics(
        population_stability_index=0.4,
    )

    metric_name, threshold = metrics._find_name_and_threshold()

    assert metric_name == MonitorMetricName.POPULATION_STABILITY_INDEX
    assert isinstance(threshold, MonitoringThreshold)
    assert threshold.value == 0.4


def test_categorical_drift_metrics_find_name_and_threshold_pearsons_only():
    metrics = CategoricalDriftMetrics(
        pearsons_chi_squared_test=0.6,
    )

    metric_name, threshold = metrics._find_name_and_threshold()

    assert metric_name == MonitorMetricName.PEARSONS_CHI_SQUARED_TEST
    assert isinstance(threshold, MonitoringThreshold)
    assert threshold.value == 0.6


def test_categorical_drift_metrics_get_default_thresholds():
    metric = CategoricalDriftMetrics._get_default_thresholds()

    assert metric.jensen_shannon_distance == 0.1
    assert metric.population_stability_index is None
    assert metric.pearsons_chi_squared_test is None


def test_data_drift_metric_threshold_eq_not_implemented_for_other_type():
    threshold = DataDriftMetricThreshold()

    result = DataDriftMetricThreshold.__eq__(threshold, 5)  # type: ignore[arg-type]

    assert result is NotImplemented


def test_prediction_drift_metric_threshold_eq_not_implemented_for_other_type():
    threshold = PredictionDriftMetricThreshold()

    result = PredictionDriftMetricThreshold.__eq__(threshold, "other")  # type: ignore[arg-type]

    assert result is NotImplemented


def test_data_quality_metric_threshold_eq_not_implemented_for_other_type():
    threshold = DataQualityMetricThreshold()

    result = DataQualityMetricThreshold.__eq__(threshold, object())  # type: ignore[arg-type]

    assert result is NotImplemented


def test_feature_attribution_drift_metric_threshold_to_rest_with_and_without_value():
    fat_with_value = FeatureAttributionDriftMetricThreshold(normalized_discounted_cumulative_gain=2.5)
    rest_with_value = fat_with_value._to_rest_object()
    assert isinstance(rest_with_value, FeatureAttributionMetricThreshold)
    assert rest_with_value.threshold.value == 2.5

    fat_without_value = FeatureAttributionDriftMetricThreshold()
    rest_without_value = fat_without_value._to_rest_object()
    assert rest_without_value.threshold is None


def test_feature_attribution_drift_metric_threshold_from_rest():
    rest_obj = FeatureAttributionMetricThreshold(
        metric="NormalizedDiscountedCumulativeGain",
        threshold=MonitoringThreshold(value=1.2),
    )
    fat = FeatureAttributionDriftMetricThreshold._from_rest_object(rest_obj)
    assert isinstance(fat, FeatureAttributionDriftMetricThreshold)
    assert fat.normalized_discounted_cumulative_gain == 1.2


def test_model_performance_classification_thresholds_to_str_and_from_rest():
    thresholds = ModelPerformanceClassificationThresholds(accuracy=0.8, precision=0.7, recall=0.6)
    result = thresholds._to_str_object()
    assert '"metric":"Accuracy"' in result
    assert '"threshold":{"value":0.8}' in result
    assert '"metric":"Precision"' in result
    assert '"threshold":{"value":0.7}' in result
    assert '"metric":"Recall"' in result
    assert '"threshold":{"value":0.6}' in result

    empty_thresholds = ModelPerformanceClassificationThresholds()
    assert empty_thresholds._to_str_object() is None

    rest_obj = ClassificationModelPerformanceMetricThreshold(
        metric="Accuracy", threshold=MonitoringThreshold(value=0.9)
    )
    from_rest = ModelPerformanceClassificationThresholds._from_rest_object(rest_obj)
    assert isinstance(from_rest, ModelPerformanceClassificationThresholds)
    assert from_rest.accuracy == 0.9
    assert from_rest.precision is None
    assert from_rest.recall is None


def test_model_performance_regression_thresholds_to_str_object_branches():
    thresholds = ModelPerformanceRegressionThresholds(
        mean_absolute_error=1.0,
        mean_squared_error=2.0,
        root_mean_squared_error=3.0,
    )
    result = thresholds._to_str_object()
    assert '"metric":"MeanAbsoluteError"' in result
    assert '"threshold":{"value":1.0}' in result
    assert '"metric":"MeanSquaredError"' in result
    assert '"threshold":{"value":2.0}' in result
    assert '"metric":"RootMeanSquaredError"' in result
    assert '"threshold":{"value":3.0}' in result

    empty_thresholds = ModelPerformanceRegressionThresholds()
    assert empty_thresholds._to_str_object() is None


def test_model_performance_metric_threshold_to_str_object_combinations():
    classification = ModelPerformanceClassificationThresholds(accuracy=0.75)
    regression = ModelPerformanceRegressionThresholds(mean_absolute_error=1.1)

    both = ModelPerformanceMetricThreshold(classification=classification, regression=regression)
    both_str = both._to_str_object()
    assert both_str.startswith("[") and both_str.endswith("]")
    assert '"metric":"Accuracy"' in both_str
    assert '"metric":"MeanAbsoluteError"' in both_str
    assert "," in both_str.strip("[]")

    only_classification = ModelPerformanceMetricThreshold(classification=classification)
    only_class_str = only_classification._to_str_object()
    assert only_class_str.startswith("[") and only_class_str.endswith("]")
    assert '"metric":"Accuracy"' in only_class_str
    assert "MeanAbsoluteError" not in only_class_str

    only_regression = ModelPerformanceMetricThreshold(regression=regression)
    only_reg_str = only_regression._to_str_object()
    assert only_reg_str.startswith("[") and only_reg_str.endswith("]")
    assert '"metric":"MeanAbsoluteError"' in only_reg_str
    assert "Accuracy" not in only_reg_str

    empty = ModelPerformanceMetricThreshold()
    assert empty._to_str_object() is None


def test_custom_monitoring_metric_threshold_to_and_from_rest():
    custom_with_threshold = CustomMonitoringMetricThreshold(metric_name="myMetric", threshold=1.5)
    rest_with_threshold = custom_with_threshold._to_rest_object()
    assert rest_with_threshold.metric == "myMetric"
    assert isinstance(rest_with_threshold.threshold, MonitoringThreshold)
    assert rest_with_threshold.threshold.value == 1.5

    custom_without_threshold = CustomMonitoringMetricThreshold(metric_name="myMetric", threshold=None)
    rest_without_threshold = custom_without_threshold._to_rest_object()
    assert rest_without_threshold.metric == "myMetric"
    assert rest_without_threshold.threshold is None

    from_rest = CustomMonitoringMetricThreshold._from_rest_object(rest_with_threshold)
    assert from_rest.metric_name == "myMetric"
    assert from_rest.threshold == 1.5


def test_generation_safety_quality_monitoring_metric_threshold_to_and_from_rest_with_defaults():
    safety = GenerationSafetyQualityMonitoringMetricThreshold(
        groundedness={"aggregated_groundedness_pass_rate": 0.9},
        relevance={
            "acceptable_relevance_score_per_instance": 4,
            "aggregated_relevance_pass_rate": 0.8,
        },
    )
    rest_list = safety._to_rest_object()
    grounded_accept = [m for m in rest_list if m.metric == "AcceptableGroundednessScorePerInstance"][0]
    grounded_agg = [m for m in rest_list if m.metric == "AggregatedGroundednessPassRate"][0]
    relevance_accept = [m for m in rest_list if m.metric == "AcceptableRelevanceScorePerInstance"][0]
    relevance_agg = [m for m in rest_list if m.metric == "AggregatedRelevancePassRate"][0]

    assert grounded_accept.threshold.value == 3
    assert grounded_agg.threshold.value == 0.9
    assert relevance_accept.threshold.value == 4
    assert relevance_agg.threshold.value == 0.8

    round_tripped = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(rest_list)
    assert round_tripped.groundedness["aggregated_groundedness_pass_rate"] == 0.9
    assert "acceptable_groundedness_score_per_instance" in round_tripped.groundedness
    assert round_tripped.relevance["acceptable_relevance_score_per_instance"] == 4
    assert round_tripped.relevance["aggregated_relevance_pass_rate"] == 0.8


def test_generation_token_statistics_monitor_metric_threshold_to_rest_with_and_without_total_token():
    token_thresholds = GenerationTokenStatisticsMonitoringMetricThreshold(
        totaltoken={"total_token_count": 5, "total_token_count_per_group": 2}
    )
    rest_list = token_thresholds._to_rest_object()
    assert len(rest_list) == 2

    total_count = [m for m in rest_list if m.metric == "TotalTokenCount"][0]
    total_count_per_group = [m for m in rest_list if m.metric == "TotalTokenCountPerGroup"][0]

    assert isinstance(total_count, GenerationTokenStatisticsMetricThreshold)
    assert total_count.threshold.value == 5
    assert isinstance(total_count_per_group, GenerationSafetyQualityMetricThreshold)
    assert total_count_per_group.threshold.value == 2

    token_thresholds_default = GenerationTokenStatisticsMonitoringMetricThreshold(
        totaltoken={"total_token_count_per_group": 4}
    )
    rest_list_default = token_thresholds_default._to_rest_object()
    total_count_default = [m for m in rest_list_default if m.metric == "TotalTokenCount"][0]
    assert total_count_default.threshold.value == 3


def test_generation_token_statistics_monitor_metric_threshold_from_rest_and_defaults():
    rest_list = [
        GenerationTokenStatisticsMetricThreshold(
            metric="TotalTokenCount", threshold=MonitoringThreshold(value=7)
        ),
        GenerationTokenStatisticsMetricThreshold(
            metric="TotalTokenCountPerGroup", threshold=MonitoringThreshold(value=11)
        ),
    ]
    from_rest = GenerationTokenStatisticsMonitoringMetricThreshold._from_rest_object(rest_list)
    assert from_rest.totaltoken["total_token_count"] == 7
    assert from_rest.totaltoken["total_token_count_per_group"] == 11

    default_obj = GenerationTokenStatisticsMonitoringMetricThreshold._get_default_thresholds()
    assert default_obj.totaltoken["total_token_count"] == 0
    assert default_obj.totaltoken["total_token_count_per_group"] == 0


def test_model_performance_classification_accuracy_true_and_false_branches():
    cls_with_accuracy = ModelPerformanceClassificationThresholds(accuracy=0.8, precision=None, recall=None)
    result_with_accuracy = cls_with_accuracy._to_str_object()
    assert '"Accuracy"' in result_with_accuracy

    cls_without_accuracy = ModelPerformanceClassificationThresholds(accuracy=None, precision=0.5, recall=None)
    result_without_accuracy = cls_without_accuracy._to_str_object()
    assert '"Precision"' in result_without_accuracy
    assert '"Accuracy"' not in result_without_accuracy


def test_model_performance_metric_threshold_str_object_len_branches_and_nonempty():
    classification_thresholds = ModelPerformanceClassificationThresholds(accuracy=0.9, precision=None, recall=None)
    regression_thresholds = ModelPerformanceRegressionThresholds(
        mean_absolute_error=0.1,
        mean_squared_error=None,
        root_mean_squared_error=None,
    )

    metric_two = ModelPerformanceMetricThreshold(
        classification=classification_thresholds,
        regression=regression_thresholds,
    )
    result_two = metric_two._to_str_object()
    assert result_two.startswith("[")
    assert '"Accuracy"' in result_two
    assert '"MeanAbsoluteError"' in result_two

    metric_one = ModelPerformanceMetricThreshold(
        classification=classification_thresholds,
        regression=None,
    )
    result_one = metric_one._to_str_object()
    assert result_one.startswith("[")
    assert '"Accuracy"' in result_one
    assert '"MeanAbsoluteError"' not in result_one


def test_custom_monitoring_metric_threshold_to_rest_object_threshold_branches():
    metric_with_threshold = CustomMonitoringMetricThreshold(metric_name="my_metric", threshold=1.5)
    rest_with_threshold = metric_with_threshold._to_rest_object()
    assert isinstance(rest_with_threshold, CustomMetricThreshold)
    assert rest_with_threshold.threshold.value == 1.5

    metric_without_threshold = CustomMonitoringMetricThreshold(metric_name="my_metric", threshold=None)
    rest_without_threshold = metric_without_threshold._to_rest_object()
    assert isinstance(rest_without_threshold, CustomMetricThreshold)
    assert rest_without_threshold.threshold is None


def test_generation_safety_quality_monitoring_metric_threshold_empty_returns_empty_list():
    metric = GenerationSafetyQualityMonitoringMetricThreshold()
    rest_list = metric._to_rest_object()
    assert isinstance(rest_list, list)
    assert rest_list == []


def test_generation_token_statistics_monitor_metric_threshold_default_total_token_count_branch():
    metric = GenerationTokenStatisticsMonitoringMetricThreshold(
        totaltoken={"total_token_count_per_group": 7}
    )
    rest_list = metric._to_rest_object()
    assert len(rest_list) == 2

    total_token_rest = next(x for x in rest_list if x.metric == "TotalTokenCount")
    assert isinstance(total_token_rest, GenerationTokenStatisticsMetricThreshold)
    assert total_token_rest.threshold.value == 3

    per_group_rest = next(x for x in rest_list if x.metric == "TotalTokenCountPerGroup")
    assert isinstance(per_group_rest, GenerationSafetyQualityMetricThreshold)
    assert per_group_rest.threshold.value == 7


def test_generation_safety_quality_from_rest_object_relevance_only_and_others_none():
    thresholds = [
        _DummyThreshold("AcceptableRelevanceScorePerInstance", 4.0),
        _DummyThreshold("AggregatedRelevancePassRate", 0.9),
    ]

    result = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(thresholds)

    assert result.groundedness is None
    assert result.coherence is None
    assert result.fluency is None
    assert result.similarity is None
    assert result.relevance == {
        "acceptable_relevance_score_per_instance": 4.0,
        "aggregated_relevance_pass_rate": 0.9,
    }


def test_generation_safety_quality_from_rest_object_with_no_thresholds_returns_all_none():
    thresholds = []

    result = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(thresholds)

    assert result.groundedness is None
    assert result.relevance is None
    assert result.coherence is None
    assert result.fluency is None
    assert result.similarity is None


def test_generation_token_statistics_from_rest_object_with_both_metrics():
    thresholds = [
        _DummyThreshold("TotalTokenCount", 5.0),
        _DummyThreshold("TotalTokenCountPerGroup", 7.0),
    ]

    result = GenerationTokenStatisticsMonitoringMetricThreshold._from_rest_object(thresholds)

    assert result.totaltoken == {
        "total_token_count": 5.0,
        "total_token_count_per_group": 7.0,
    }


def test_generation_token_statistics_from_rest_object_with_no_metrics_results_in_none():
    thresholds = []

    result = GenerationTokenStatisticsMonitoringMetricThreshold._from_rest_object(thresholds)

    assert result.totaltoken is None


def test_generation_token_statistics_get_default_thresholds_values():
    result = GenerationTokenStatisticsMonitoringMetricThreshold._get_default_thresholds()

    assert result.totaltoken == {
        "total_token_count": 0,
        "total_token_count_per_group": 0,
    }


def test_generation_safety_quality_from_rest_object_all_metrics():
    thresholds = [
        _DummyThreshold("AcceptableGroundednessScorePerInstance", 1.1),
        _DummyThreshold("AggregatedGroundednessPassRate", 2.2),
        _DummyThreshold("AcceptableRelevanceScorePerInstance", 3.3),
        _DummyThreshold("AggregatedRelevancePassRate", 4.4),
        _DummyThreshold("AcceptableCoherenceScorePerInstance", 5.5),
        _DummyThreshold("AggregatedCoherencePassRate", 6.6),
        _DummyThreshold("AcceptableFluencyScorePerInstance", 7.7),
        _DummyThreshold("AggregatedFluencyPassRate", 8.8),
        _DummyThreshold("AcceptableSimilarityScorePerInstance", 9.9),
        _DummyThreshold("AggregatedSimilarityPassRate", 10.1),
    ]

    result = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(thresholds)

    assert result.groundedness == {
        "acceptable_groundedness_score_per_instance": 1.1,
        "aggregated_groundedness_pass_rate": 2.2,
    }
    assert result.relevance == {
        "acceptable_relevance_score_per_instance": 3.3,
        "aggregated_relevance_pass_rate": 4.4,
    }
    assert result.coherence == {
        "acceptable_coherence_score_per_instance": 5.5,
        "aggregated_coherence_pass_rate": 6.6,
    }
    assert result.fluency == {
        "acceptable_fluency_score_per_instance": 7.7,
        "aggregated_fluency_pass_rate": 8.8,
    }
    assert result.similarity == {
        "acceptable_similarity_score_per_instance": 9.9,
        "aggregated_similarity_pass_rate": 10.1,
    }


def test_generation_token_statistics_from_rest_object_only_total_token_count():
    thresholds = [
        _DummyThreshold("TotalTokenCount", 5.0),
    ]

    result = GenerationTokenStatisticsMonitoringMetricThreshold._from_rest_object(thresholds)

    assert result.totaltoken == {"total_token_count": 5.0}


def test_generation_token_statistics_from_rest_object_only_total_token_count_per_group():
    thresholds = [
        _DummyThreshold("TotalTokenCountPerGroup", 4.0),
    ]

    result = GenerationTokenStatisticsMonitoringMetricThreshold._from_rest_object(thresholds)

    assert result.totaltoken == {"total_token_count_per_group": 4.0}

@pytest.mark.parametrize(
    'field_kwargs, expected_metric, expected_value',
    [
        ({'jensen_shannon_distance': 0.12}, MonitorMetricName.JENSEN_SHANNON_DISTANCE, 0.12),
        ({'normalized_wasserstein_distance': 0.34}, MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE, 0.34),
        ({'population_stability_index': 0.56}, MonitorMetricName.POPULATION_STABILITY_INDEX, 0.56),
        ({'two_sample_kolmogorov_smirnov_test': 0.78}, MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST, 0.78),
    ],
)
def test_numerical_drift_metrics_selects_first_available_metric(field_kwargs, expected_metric, expected_value):
    metrics = NumericalDriftMetrics(**field_kwargs)
    metric_name, threshold = metrics._find_name_and_threshold()
    assert metric_name == expected_metric
    assert threshold.value == expected_value

@pytest.mark.parametrize(
    'field_kwargs, expected_metric, expected_value',
    [
        ({'jensen_shannon_distance': 0.11}, MonitorMetricName.JENSEN_SHANNON_DISTANCE, 0.11),
        ({'population_stability_index': 0.22}, MonitorMetricName.POPULATION_STABILITY_INDEX, 0.22),
        ({'pearsons_chi_squared_test': 0.33}, MonitorMetricName.PEARSONS_CHI_SQUARED_TEST, 0.33),
    ],
)
def test_categorical_drift_metrics_selects_next_metric_when_prior_absent(field_kwargs, expected_metric, expected_value):
    metrics = CategoricalDriftMetrics(**field_kwargs)
    metric_name, threshold = metrics._find_name_and_threshold()
    assert metric_name == expected_metric
    assert threshold.value == expected_value

@pytest.mark.parametrize(
    'rest_metric, attribute_name, value',
    [
        ('JensenShannonDistance', 'jensen_shannon_distance', 0.13),
        ('PopulationStabilityIndex', 'population_stability_index', 0.24),
        ('PearsonsChiSquaredTest', 'pearsons_chi_squared_test', 0.35),
    ],
)
def test_categorical_drift_metrics_from_rest_sets_attribute(rest_metric, attribute_name, value):
    metrics = CategoricalDriftMetrics()._from_rest_object(rest_metric, value)
    assert getattr(metrics, attribute_name) == value


def test_categorical_drift_metrics_from_rest_returns_empty_for_unknown_metric():
    metrics = CategoricalDriftMetrics()._from_rest_object('UnknownMetric', 0.5)
    assert metrics.jensen_shannon_distance is None
    assert metrics.population_stability_index is None
    assert metrics.pearsons_chi_squared_test is None


def test_data_drift_metric_threshold_from_rest_groups_numerical_and_categorical_thresholds():
    obj = [
        SimpleNamespace(
            data_type='Numerical',
            metric='JensenShannonDistance',
            threshold=SimpleNamespace(value=0.45),
        ),
        SimpleNamespace(
            data_type='Categorical',
            metric='PearsonsChiSquaredTest',
            threshold=SimpleNamespace(value=0.67),
        ),
    ]
    result = DataDriftMetricThreshold._from_rest_object(obj)
    assert result.numerical.jensen_shannon_distance == 0.45
    assert result.categorical.pearsons_chi_squared_test == 0.67


def test_feature_attribution_drift_metric_threshold_serialization():
    metric = FeatureAttributionDriftMetricThreshold(normalized_discounted_cumulative_gain=0.7)
    rest_obj = metric._to_rest_object()
    assert rest_obj.metric == "normalizedDiscountedCumulativeGain"
    assert rest_obj.threshold.value == 0.7

    no_value_rest = FeatureAttributionDriftMetricThreshold()._to_rest_object()
    assert no_value_rest.metric == "normalizedDiscountedCumulativeGain"
    assert no_value_rest.threshold is None

    restored = FeatureAttributionDriftMetricThreshold._from_rest_object(rest_obj)
    assert restored.normalized_discounted_cumulative_gain == 0.7

    none_rest = FeatureAttributionDriftMetricThreshold._from_rest_object(
        FeatureAttributionMetricThreshold(metric="NormalizedDiscountedCumulativeGain", threshold=None)
    )
    assert none_rest.normalized_discounted_cumulative_gain is None


def test_model_performance_classification_and_regression_to_str_object_variations():
    classification = ModelPerformanceClassificationThresholds(accuracy=0.8, recall=0.4)
    classification_str = classification._to_str_object()
    assert classification_str == (
        "{\"modelType\":\"classification\",\"metric\":\"Accuracy\",\"threshold\":{\"value\":0.8}}, "
        "{\"modelType\":\"classification\",\"metric\":\"Recall\",\"threshold\":{\"value\":0.4}}"
    )
    assert ModelPerformanceClassificationThresholds()._to_str_object() is None

    regression = ModelPerformanceRegressionThresholds(mean_absolute_error=1.1, mean_squared_error=2.2)
    regression_str = regression._to_str_object()
    assert regression_str == (
        "{\"modelType\":\"regression\",\"metric\":\"MeanAbsoluteError\",\"threshold\":{\"value\":1.1}}, "
        "{\"modelType\":\"regression\",\"metric\":\"MeanSquaredError\",\"threshold\":{\"value\":2.2}}"
    )
    assert ModelPerformanceRegressionThresholds()._to_str_object() is None


def test_model_performance_metric_threshold_to_str_object_variants():
    classification = ModelPerformanceClassificationThresholds(accuracy=0.6)
    regression = ModelPerformanceRegressionThresholds(mean_absolute_error=1.0)
    combined = ModelPerformanceMetricThreshold(classification=classification, regression=regression)
    assert combined._to_str_object() == "[" + classification._to_str_object() + ", " + regression._to_str_object() + "]"

    single = ModelPerformanceMetricThreshold(classification=classification)
    assert single._to_str_object() == "[" + classification._to_str_object() + "]"


def test_model_performance_metric_threshold_from_rest_object():
    rest_obj = ClassificationModelPerformanceMetricThreshold(
        metric="Accuracy",
        threshold=MonitoringThreshold(value=0.333),
    )
    result = ModelPerformanceMetricThreshold._from_rest_object(rest_obj)
    assert result.classification.accuracy == 0.333
    assert result.regression is None


def test_custom_monitoring_metric_threshold_serialization():
    custom = CustomMonitoringMetricThreshold(metric_name="myMetric", threshold=0.12)
    rest_obj = custom._to_rest_object()
    assert rest_obj.metric == "myMetric"
    assert rest_obj.threshold.value == 0.12

    other = CustomMonitoringMetricThreshold(metric_name="otherMetric")
    other_rest = other._to_rest_object()
    assert other_rest.metric == "otherMetric"
    assert other_rest.threshold is None

    round_trip = CustomMonitoringMetricThreshold._from_rest_object(
        CustomMetricThreshold(metric="roundTrip", threshold=MonitoringThreshold(value=0.9))
    )
    assert round_trip.metric_name == "roundTrip"
    assert round_trip.threshold == 0.9


def test_generation_safety_quality_monitoring_metric_threshold_variants():
    groundedness = {
        "acceptable_groundedness_score_per_instance": 5.5,
        "aggregated_groundedness_pass_rate": 0.92,
    }
    fluency = {"aggregated_fluency_pass_rate": 0.77}
    subject = GenerationSafetyQualityMonitoringMetricThreshold(groundedness=groundedness, fluency=fluency)
    rest_list = subject._to_rest_object()
    metrics = {threshold.metric: threshold for threshold in rest_list}
    assert metrics["AcceptableGroundednessScorePerInstance"].threshold.value == 5.5
    assert metrics["AggregatedGroundednessPassRate"].threshold.value == 0.92
    assert metrics["AcceptableFluencyScorePerInstance"].threshold.value == 3
    assert metrics["AggregatedFluencyPassRate"].threshold.value == 0.77

    restored = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(
        [
            GenerationSafetyQualityMetricThreshold(
                metric="AcceptableGroundednessScorePerInstance", threshold=MonitoringThreshold(value=2.2)
            ),
            GenerationSafetyQualityMetricThreshold(
                metric="AggregatedGroundednessPassRate", threshold=MonitoringThreshold(value=0.55)
            ),
            GenerationSafetyQualityMetricThreshold(
                metric="AcceptableSimilarityScorePerInstance", threshold=MonitoringThreshold(value=1.8)
            ),
            GenerationSafetyQualityMetricThreshold(
                metric="AggregatedSimilarityPassRate", threshold=MonitoringThreshold(value=0.85)
            ),
        ]
    )
    assert restored.groundedness["acceptable_groundedness_score_per_instance"] == 2.2
    assert restored.groundedness["aggregated_groundedness_pass_rate"] == 0.55
    assert restored.similarity["acceptable_similarity_score_per_instance"] == 1.8
    assert restored.similarity["aggregated_similarity_pass_rate"] == 0.85


def test_generation_token_statistics_monitor_metric_threshold_variations():
    subject = GenerationTokenStatisticsMonitorMetricThreshold(
        totaltoken={"total_token_count": 10, "total_token_count_per_group": 4}
    )
    rest_list = subject._to_rest_object()
    metrics = {threshold.metric: threshold for threshold in rest_list}
    assert metrics["TotalTokenCount"].threshold.value == 10
    assert metrics["TotalTokenCountPerGroup"].threshold.value == 4

    fallback = GenerationTokenStatisticsMonitorMetricThreshold(totaltoken={"total_token_count_per_group": 7})
    fallback_list = fallback._to_rest_object()
    fallback_metrics = {threshold.metric: threshold for threshold in fallback_list}
    assert fallback_metrics["TotalTokenCount"].threshold.value == 3
    assert fallback_metrics["TotalTokenCountPerGroup"].threshold.value == 7

    restored = GenerationTokenStatisticsMonitorMetricThreshold._from_rest_object(
        [
            GenerationTokenStatisticsMetricThreshold(metric="TotalTokenCount", threshold=MonitoringThreshold(value=11)),
            GenerationTokenStatisticsMetricThreshold(
                metric="TotalTokenCountPerGroup", threshold=MonitoringThreshold(value=5)
            ),
        ]
    )
    assert restored.totaltoken["total_token_count"] == 11
    assert restored.totaltoken["total_token_count_per_group"] == 5


def test_generation_safety_to_rest_object_defaults_and_from_rest_reconstruction():
    threshold = GenerationSafetyQualityMonitoringMetricThreshold(
        groundedness={"aggregated_groundedness_pass_rate": 0.65},
        fluency={
            "acceptable_fluency_score_per_instance": 0.75,
            "aggregated_fluency_pass_rate": 0.9,
        },
    )
    rest = threshold._to_rest_object()
    assert len(rest) == 4
    assert rest[0].metric == "AcceptableGroundednessScorePerInstance"
    assert rest[0].threshold.value == 3
    assert rest[1].metric == "AggregatedGroundednessPassRate"
    assert rest[1].threshold.value == 0.65
    assert rest[2].metric == "AcceptableFluencyScorePerInstance"
    assert rest[2].threshold.value == 0.75
    assert rest[3].metric == "AggregatedFluencyPassRate"
    assert rest[3].threshold.value == 0.9

    rest_items = [
        types.SimpleNamespace(metric="AcceptableRelevanceScorePerInstance", threshold=types.SimpleNamespace(value=0.12)),
        types.SimpleNamespace(metric="AggregatedRelevancePassRate", threshold=types.SimpleNamespace(value=0.4)),
        types.SimpleNamespace(metric="AcceptableCoherenceScorePerInstance", threshold=types.SimpleNamespace(value=0.22)),
        types.SimpleNamespace(metric="AggregatedCoherencePassRate", threshold=types.SimpleNamespace(value=0.55)),
    ]
    reconstructed = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(rest_items)
    assert reconstructed.relevance == {
        "acceptable_relevance_score_per_instance": 0.12,
        "aggregated_relevance_pass_rate": 0.4,
    }
    assert reconstructed.coherence == {
        "acceptable_coherence_score_per_instance": 0.22,
        "aggregated_coherence_pass_rate": 0.55,
    }


def test_generation_token_statistics_to_rest_from_rest_and_defaults():
    threshold = GenerationTokenStatisticsMonitorMetricThreshold(
        totaltoken={"total_token_count_per_group": 8},
    )
    rest = threshold._to_rest_object()
    assert len(rest) == 2
    assert rest[0].metric == "TotalTokenCount"
    assert rest[0].threshold.value == 3
    assert rest[1].metric == "TotalTokenCountPerGroup"
    assert rest[1].threshold.value == 8

    rest_items = [
        types.SimpleNamespace(metric="TotalTokenCount", threshold=types.SimpleNamespace(value=5)),
        types.SimpleNamespace(metric="TotalTokenCountPerGroup", threshold=types.SimpleNamespace(value=6)),
    ]
    reconstructed = GenerationTokenStatisticsMonitorMetricThreshold._from_rest_object(rest_items)
    assert reconstructed.totaltoken == {"total_token_count": 5, "total_token_count_per_group": 6}

    defaults = GenerationTokenStatisticsMonitorMetricThreshold._get_default_thresholds()
    assert defaults.totaltoken == {"total_token_count": 0, "total_token_count_per_group": 0}


def test_generation_token_statistics_to_rest_object_default_total_token_count():
    metric = GenerationTokenStatisticsMonitorMetricThreshold(
        totaltoken={"total_token_count_per_group": 5.75}
    )
    rest = metric._to_rest_object()
    assert len(rest) == 2
    total_count, per_group = rest
    assert total_count.metric == "TotalTokenCount"
    assert total_count.threshold.value == 3
    assert per_group.metric == "TotalTokenCountPerGroup"
    assert per_group.threshold.value == 5.75


def test_generation_token_statistics_to_rest_object_respects_total_token_count():
    metric = GenerationTokenStatisticsMonitorMetricThreshold(
        totaltoken={"total_token_count": 8, "total_token_count_per_group": 2}
    )
    rest = metric._to_rest_object()
    assert rest[0].metric == "TotalTokenCount"
    assert rest[0].threshold.value == 8
    assert rest[1].metric == "TotalTokenCountPerGroup"
    assert rest[1].threshold.value == 2


def test_generation_token_statistics_from_rest_object_populates_totaltoken():
    rest = [
        GenerationTokenStatisticsMetricThreshold(
            metric="TotalTokenCount",
            threshold=MonitoringThreshold(value=4),
        ),
        GenerationSafetyQualityMetricThreshold(
            metric="TotalTokenCountPerGroup",
            threshold=MonitoringThreshold(value=9),
        ),
    ]
    result = GenerationTokenStatisticsMonitorMetricThreshold._from_rest_object(rest)
    assert result.totaltoken == {"total_token_count": 4, "total_token_count_per_group": 9}


def test_generation_token_statistics_from_rest_object_returns_none_for_empty_list():
    result = GenerationTokenStatisticsMonitorMetricThreshold._from_rest_object([])
    assert result.totaltoken is None


def test_generation_token_statistics_get_default_thresholds():
    result = GenerationTokenStatisticsMonitorMetricThreshold._get_default_thresholds()
    assert result.totaltoken == {"total_token_count": 0, "total_token_count_per_group": 0}


def test_generation_safety_quality_to_rest_groundedness_default_acceptance():
    threshold = GenerationSafetyQualityMonitoringMetricThreshold(
        groundedness={"aggregated_groundedness_pass_rate": 0.7}
    )
    rest = threshold._to_rest_object()
    assert len(rest) == 2
    assert rest[0].metric == "AcceptableGroundednessScorePerInstance"
    assert rest[0].threshold.value == 3
    assert rest[1].metric == "AggregatedGroundednessPassRate"
    assert rest[1].threshold.value == 0.7


def test_generation_safety_quality_to_rest_relevance_with_custom_acceptance():
    threshold = GenerationSafetyQualityMonitoringMetricThreshold(
        relevance={
            "acceptable_relevance_score_per_instance": 4.2,
            "aggregated_relevance_pass_rate": 0.88,
        }
    )
    rest = threshold._to_rest_object()
    assert len(rest) == 2
    assert rest[0].metric == "AcceptableRelevanceScorePerInstance"
    assert rest[0].threshold.value == 4.2
    assert rest[1].metric == "AggregatedRelevancePassRate"
    assert rest[1].threshold.value == 0.88


def test_generation_safety_quality_from_rest_populates_dicts():
    thresholds = [
        GenerationSafetyQualityMetricThreshold(
            metric="AcceptableGroundednessScorePerInstance", threshold=MonitoringThreshold(value=0.4)
        ),
        GenerationSafetyQualityMetricThreshold(
            metric="AggregatedGroundednessPassRate", threshold=MonitoringThreshold(value=0.8)
        ),
        GenerationSafetyQualityMetricThreshold(
            metric="AcceptableSimilarityScorePerInstance", threshold=MonitoringThreshold(value=0.2)
        ),
        GenerationSafetyQualityMetricThreshold(
            metric="AggregatedSimilarityPassRate", threshold=MonitoringThreshold(value=0.9)
        ),
    ]
    result = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object(thresholds)
    assert result.groundedness == {
        "acceptable_groundedness_score_per_instance": 0.4,
        "aggregated_groundedness_pass_rate": 0.8,
    }
    assert result.similarity == {
        "acceptable_similarity_score_per_instance": 0.2,
        "aggregated_similarity_pass_rate": 0.9,
    }
    assert result.relevance is None
    assert result.coherence is None
    assert result.fluency is None


def test_generation_safety_quality_from_rest_empty_returns_none():
    result = GenerationSafetyQualityMonitoringMetricThreshold._from_rest_object([])
    assert result.groundedness is None
    assert result.relevance is None
    assert result.coherence is None
    assert result.fluency is None
    assert result.similarity is None


def test_generation_token_statistics_to_rest_total_token_count_default():
    threshold = GenerationTokenStatisticsMonitorMetricThreshold(totaltoken={"total_token_count_per_group": 2})
    rest = threshold._to_rest_object()
    assert len(rest) == 2
    assert rest[0].metric == "TotalTokenCount"
    assert rest[0].threshold.value == 3
    assert rest[1].metric == "TotalTokenCountPerGroup"
    assert rest[1].threshold.value == 2


def test_generation_token_statistics_to_rest_total_token_count_custom():
    threshold = GenerationTokenStatisticsMonitorMetricThreshold(
        totaltoken={"total_token_count": 5, "total_token_count_per_group": 1.5}
    )
    rest = threshold._to_rest_object()
    assert len(rest) == 2
    assert rest[0].metric == "TotalTokenCount"
    assert rest[0].threshold.value == 5
    assert rest[1].metric == "TotalTokenCountPerGroup"
    assert rest[1].threshold.value == 1.5


def test_generation_token_statistics_from_rest_returns_totaltoken_dict():
    thresholds = [
        GenerationTokenStatisticsMetricThreshold(metric="TotalTokenCount", threshold=MonitoringThreshold(value=6)),
        GenerationTokenStatisticsMetricThreshold(
            metric="TotalTokenCountPerGroup", threshold=MonitoringThreshold(value=1.5)
        ),
    ]
    result = GenerationTokenStatisticsMonitorMetricThreshold._from_rest_object(thresholds)
    assert result.totaltoken == {"total_token_count": 6, "total_token_count_per_group": 1.5}


def test_generation_token_statistics_from_rest_empty_returns_none():
    result = GenerationTokenStatisticsMonitorMetricThreshold._from_rest_object([])
    assert result.totaltoken is None
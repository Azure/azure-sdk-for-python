# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument, name-too-long

from marshmallow import fields, post_load

from azure.ai.ml.constants._monitoring import MonitorFeatureType
from azure.ai.ml._schema.core.fields import StringTransformedEnum, NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MetricThresholdSchema(metaclass=PatchedSchemaMeta):
    threshold = fields.Float()


class NumericalDriftMetricsSchema(metaclass=PatchedSchemaMeta):
    jensen_shannon_distance = fields.Float()
    normalized_wasserstein_distance = fields.Float()
    population_stability_index = fields.Float()
    two_sample_kolmogorov_smirnov_test = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import NumericalDriftMetrics

        return NumericalDriftMetrics(**data)


class CategoricalDriftMetricsSchema(metaclass=PatchedSchemaMeta):
    jensen_shannon_distance = fields.Float()
    population_stability_index = fields.Float()
    pearsons_chi_squared_test = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import CategoricalDriftMetrics

        return CategoricalDriftMetrics(**data)


class DataDriftMetricThresholdSchema(MetricThresholdSchema):
    data_type = StringTransformedEnum(allowed_values=[MonitorFeatureType.NUMERICAL, MonitorFeatureType.CATEGORICAL])

    numerical = NestedField(NumericalDriftMetricsSchema)
    categorical = NestedField(CategoricalDriftMetricsSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataDriftMetricThreshold

        return DataDriftMetricThreshold(**data)


class DataQualityMetricsNumericalSchema(metaclass=PatchedSchemaMeta):
    null_value_rate = fields.Float()
    data_type_error_rate = fields.Float()
    out_of_bounds_rate = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataQualityMetricsNumerical

        return DataQualityMetricsNumerical(**data)


class DataQualityMetricsCategoricalSchema(metaclass=PatchedSchemaMeta):
    null_value_rate = fields.Float()
    data_type_error_rate = fields.Float()
    out_of_bounds_rate = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataQualityMetricsCategorical

        return DataQualityMetricsCategorical(**data)


class DataQualityMetricThresholdSchema(MetricThresholdSchema):
    data_type = StringTransformedEnum(allowed_values=[MonitorFeatureType.NUMERICAL, MonitorFeatureType.CATEGORICAL])
    numerical = NestedField(DataQualityMetricsNumericalSchema)
    categorical = NestedField(DataQualityMetricsCategoricalSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataQualityMetricThreshold

        return DataQualityMetricThreshold(**data)


class PredictionDriftMetricThresholdSchema(MetricThresholdSchema):
    data_type = StringTransformedEnum(allowed_values=[MonitorFeatureType.NUMERICAL, MonitorFeatureType.CATEGORICAL])
    numerical = NestedField(NumericalDriftMetricsSchema)
    categorical = NestedField(CategoricalDriftMetricsSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import PredictionDriftMetricThreshold

        return PredictionDriftMetricThreshold(**data)


# pylint: disable-next=name-too-long
class FeatureAttributionDriftMetricThresholdSchema(MetricThresholdSchema):
    normalized_discounted_cumulative_gain = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import FeatureAttributionDriftMetricThreshold

        return FeatureAttributionDriftMetricThreshold(**data)


class ModelPerformanceClassificationThresholdsSchema(metaclass=PatchedSchemaMeta):
    accuracy = fields.Float()
    precision = fields.Float()
    recall = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import ModelPerformanceClassificationThresholds

        return ModelPerformanceClassificationThresholds(**data)


class ModelPerformanceRegressionThresholdsSchema(metaclass=PatchedSchemaMeta):
    mae = fields.Float()
    mse = fields.Float()
    rmse = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import ModelPerformanceRegressionThresholds

        return ModelPerformanceRegressionThresholds(**data)


class ModelPerformanceMetricThresholdSchema(MetricThresholdSchema):
    classification = NestedField(ModelPerformanceClassificationThresholdsSchema)
    regression = NestedField(ModelPerformanceRegressionThresholdsSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import ModelPerformanceMetricThreshold

        return ModelPerformanceMetricThreshold(**data)


class CustomMonitoringMetricThresholdSchema(MetricThresholdSchema):
    metric_name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import CustomMonitoringMetricThreshold

        return CustomMonitoringMetricThreshold(**data)


class GenerationSafetyQualityMetricThresholdSchema(metaclass=PatchedSchemaMeta):  # pylint: disable=name-too-long
    groundedness = fields.Dict(
        keys=StringTransformedEnum(
            allowed_values=["aggregated_groundedness_pass_rate", "acceptable_groundedness_score_per_instance"]
        ),
        values=fields.Float(),
    )
    relevance = fields.Dict(
        keys=StringTransformedEnum(
            allowed_values=["aggregated_relevance_pass_rate", "acceptable_relevance_score_per_instance"]
        ),
        values=fields.Float(),
    )
    coherence = fields.Dict(
        keys=StringTransformedEnum(
            allowed_values=["aggregated_coherence_pass_rate", "acceptable_coherence_score_per_instance"]
        ),
        values=fields.Float(),
    )
    fluency = fields.Dict(
        keys=StringTransformedEnum(
            allowed_values=["aggregated_fluency_pass_rate", "acceptable_fluency_score_per_instance"]
        ),
        values=fields.Float(),
    )
    similarity = fields.Dict(
        keys=StringTransformedEnum(
            allowed_values=["aggregated_similarity_pass_rate", "acceptable_similarity_score_per_instance"]
        ),
        values=fields.Float(),
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import GenerationSafetyQualityMonitoringMetricThreshold

        return GenerationSafetyQualityMonitoringMetricThreshold(**data)


class GenerationTokenStatisticsMonitorMetricThresholdSchema(
    metaclass=PatchedSchemaMeta
):  # pylint: disable=name-too-long
    totaltoken = fields.Dict(
        keys=StringTransformedEnum(allowed_values=["total_token_count", "total_token_count_per_group"]),
        values=fields.Float(),
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import GenerationTokenStatisticsMonitorMetricThreshold

        return GenerationTokenStatisticsMonitorMetricThreshold(**data)

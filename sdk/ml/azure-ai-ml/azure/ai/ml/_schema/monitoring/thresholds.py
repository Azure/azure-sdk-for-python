# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml.constants._monitoring import MonitorFeatureType, MonitorMetricName
from azure.ai.ml._schema.core.fields import StringTransformedEnum, NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MetricThresholdSchema(metaclass=PatchedSchemaMeta):
    threshold = fields.Number()


class NumericalDriftMetricsSchema(metaclass=PatchedSchemaMeta):
    jensen_shannon_distance = fields.Number()
    normalized_wasserstein_distance = fields.Number()
    population_stability_index = fields.Number()
    two_sample_kolmogorov_smirnov_test = fields.Number()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import NumericalDriftMetrics

        return NumericalDriftMetrics(**data)


class CategoricalDriftMetricsSchema(metaclass=PatchedSchemaMeta):
    jensen_shannon_distance = fields.Number()
    population_stability_index = fields.Number()
    pearsons_chi_squared_test = fields.Number()

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
    null_value_rate = fields.Number()
    data_type_error_rate = fields.Number()
    out_of_bounds_rate = fields.Number()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataQualityMetricsNumerical

        return DataQualityMetricsNumerical(**data)


class DataQualityMetricsCategoricalSchema(metaclass=PatchedSchemaMeta):
    null_value_rate = fields.Number()
    data_type_error_rate = fields.Number()
    out_of_bounds_rate = fields.Number()

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
    normalized_discounted_cumulative_gain = fields.Number()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import FeatureAttributionDriftMetricThreshold

        return FeatureAttributionDriftMetricThreshold(**data)


class ModelPerformanceMetricThresholdSchema(MetricThresholdSchema):
    metric_name = StringTransformedEnum(
        allowed_values=[
            MonitorMetricName.ACCURACY,
            MonitorMetricName.PRECISION,
            MonitorMetricName.RECALL,
            MonitorMetricName.F1_SCORE,
            MonitorMetricName.MAE,
            MonitorMetricName.MSE,
            MonitorMetricName.RMSE,
        ]
    )

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
        keys=StringTransformedEnum(allowed_values=["aggregated_groundedness_pass_rate"]), values=fields.Number()
    )
    relevance = fields.Dict(
        keys=StringTransformedEnum(allowed_values=["aggregated_relevance_pass_rate"]), values=fields.Number()
    )
    coherence = fields.Dict(
        keys=StringTransformedEnum(allowed_values=["aggregated_coherence_pass_rate"]), values=fields.Number()
    )
    fluency = fields.Dict(
        keys=StringTransformedEnum(allowed_values=["aggregated_fluency_pass_rate"]), values=fields.Number()
    )
    similarity = fields.Dict(
        keys=StringTransformedEnum(allowed_values=["aggregated_similarity_pass_rate"]), values=fields.Number()
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import GenerationSafetyQualityMonitoringMetricThreshold

        return GenerationSafetyQualityMonitoringMetricThreshold(**data)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml.constants._monitoring import MonitorFeatureType, MonitorMetricName
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MetricThresholdSchema(metaclass=PatchedSchemaMeta):
    threshold = fields.Number()


class DataDriftMetricThresholdSchema(MetricThresholdSchema):
    applicable_feature_type = StringTransformedEnum(
        allowed_values=[MonitorFeatureType.NUMERICAL, MonitorFeatureType.CATEGORICAL]
    )
    metric_name = StringTransformedEnum(
        allowed_values=[
            MonitorMetricName.JENSEN_SHANNON_DISTANCE,
            MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE,
            MonitorMetricName.POPULATION_STABILITY_INDEX,
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST,
            MonitorMetricName.PEARSONS_CHI_SQUARED_TEST,
        ]
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataDriftMetricThreshold

        return DataDriftMetricThreshold(**data)


class DataQualityMetricThresholdSchema(MetricThresholdSchema):
    applicable_feature_type = StringTransformedEnum(
        allowed_values=[MonitorFeatureType.NUMERICAL, MonitorFeatureType.CATEGORICAL]
    )
    metric_name = StringTransformedEnum(
        allowed_values=[
            MonitorMetricName.NULL_VALUE_RATE,
            MonitorMetricName.DATA_TYPE_ERROR_RATE,
            MonitorMetricName.OUT_OF_BOUND_RATE,
        ]
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataQualityMetricThreshold

        return DataQualityMetricThreshold(**data)


class PredictionDriftMetricThresholdSchema(MetricThresholdSchema):
    applicable_feature_type = StringTransformedEnum(
        allowed_values=[MonitorFeatureType.NUMERICAL, MonitorFeatureType.CATEGORICAL]
    )
    metric_name = StringTransformedEnum(
        allowed_values=[
            MonitorMetricName.JENSEN_SHANNON_DISTANCE,
            MonitorMetricName.NORMALIZED_WASSERSTEIN_DISTANCE,
            MonitorMetricName.POPULATION_STABILITY_INDEX,
            MonitorMetricName.TWO_SAMPLE_KOLMOGOROV_SMIRNOV_TEST,
            MonitorMetricName.PEARSONS_CHI_SQUARED_TEST,
        ]
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import PredictionDriftMetricThreshold

        return PredictionDriftMetricThreshold(**data)


class FeatureAttributionDriftMetricThresholdSchema(MetricThresholdSchema):
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

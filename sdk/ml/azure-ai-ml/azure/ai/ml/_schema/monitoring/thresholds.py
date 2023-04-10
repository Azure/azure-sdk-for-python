# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MetricThreshold(metaclass=PatchedSchemaMeta):
    threshold = fields.Number()


class DataDriftMetricThreshold(MetricThreshold):
    applicable_feature_type = fields.Str()
    metric_name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataDriftMetricThreshold

        return DataDriftMetricThreshold(**data)


class DataQualityMetricThreshold(MetricThreshold):
    applicable_feature_type = fields.Str()
    metric_name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import DataQualityMetricThreshold

        return DataQualityMetricThreshold(**data)


class PredictionDriftMetricThreshold(MetricThreshold):
    applicable_feature_type = fields.Str()
    metric_name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import PredictionDriftMetricThreshold

        return PredictionDriftMetricThreshold(**data)


class FeatureAttributionDriftMetricThreshold(MetricThreshold):

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import FeatureAttributionDriftMetricThreshold

        return FeatureAttributionDriftMetricThreshold(**data)


class ModelPerformanceMetricThreshold(MetricThreshold):
    metric_name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.thresholds import ModelPerformanceMetricThreshold

        return ModelPerformanceMetricThreshold(**data)

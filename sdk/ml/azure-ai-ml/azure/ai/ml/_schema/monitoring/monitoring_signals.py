# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import List, Union

from marshmallow import fields, post_load

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, UnionField, StringTransformedEnum
from azure.ai.ml._utils._experimental import experimental


class DataSegmentSchema(PatchedSchemaMeta):
    feature_name = fields.Str()
    feature_values = fields.List(fields.Str)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import DataSegment

        return DataSegment(**data)


class MonitoringMetricThresholdSchema(PatchedSchemaMeta):
    applicable_feature_type = fields.Str()
    metric_name = fields.Str()
    threshold = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import MonitoringMetricThreshold

        return MonitoringMetricThreshold(**data)


class MonitorFeatureFilterSchema(PatchedSchemaMeta):
    top_n_feature_importance = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import MonitorFeatureFilter

        return MonitorFeatureFilter(**data)


class BaselineDataRangeSchema(PatchedSchemaMeta):
    from_date = fields.Str()
    to_date = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import BaselineDataRange

        return BaselineDataRange(**data)


class TargetDatasetSchema(PatchedSchemaMeta):
    dataset_name = fields.Str()
    lookback_period_name = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import TargetDataset

        return TargetDataset(**data)


class BaselineDatasetSchema(PatchedSchemaMeta):
    dataset_name = fields.Str()
    data_range = NestedField(BaselineDataRangeSchema)


    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import BaselineDataset

        return BaselineDataset(**data)


class MonitoringSignalSchema(PatchedSchemaMeta):
    target_dataset = NestedField(TargetDatasetSchema)
    baseline_dataset = NestedField(BaselineDatasetSchema)


class MetricMonitoringSignalSchema(MonitoringSignalSchema):
    metric_thresholds = NestedField(MonitoringMetricThresholdSchema)


class DataSignalSchema(MetricMonitoringSignalSchema):
    features = UnionField(
        union_fields=[
            fields.List(fields.Str),
            NestedField(MonitorFeatureFilterSchema),
            StringTransformedEnum(allowed_values=["all_features"])
        ]
    )


class DataDriftSignalSchema(DataSignalSchema):
    type = StringTransformedEnum(allowed_values=["data_drift"])

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import DataDriftSignal

        return DataDriftSignal(**data)


class DataQualitySignalSchema(DataSignalSchema):
    type = StringTransformedEnum(allowed_values=["data_quality"])

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import DataQualitySignal

        return DataQualitySignal(**data)


class PredictionDriftSignalSchema(MetricMonitoringSignalSchema):
    type = StringTransformedEnum(allowed_values=["prediction_drift"])

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import PredictionDriftSignal

        return PredictionDriftSignal(**data)


class ModelSignalSchema(MetricMonitoringSignalSchema):
    model_type = fields.Str()


class FeatureAttributionDriftSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=["feature_attribution_drift"])

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import FeatureAttributionDriftSignal

        return FeatureAttributionDriftSignal(**data)


class ModelPerformanceSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=["model_drift"])
    data_segment = NestedField(DataSegmentSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import ModelPerformanceSignal

        return ModelPerformanceSignal(**data)


class CustomMonitoringSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=["custom_monitoring_signal"])
    component_id = ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitoring_signals import CustomMonitoringSignal

        return CustomMonitoringSignal(**data)

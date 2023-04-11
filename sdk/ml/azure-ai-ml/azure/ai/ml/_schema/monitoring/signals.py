# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._monitoring import MonitorSignalType, ALL_FEATURES, MonitorModelType
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, UnionField, StringTransformedEnum
from azure.ai.ml._schema.monitoring.input_data import MonitorInputDataSchema
from azure.ai.ml._schema.monitoring.thresholds import (
    DataDriftMetricThresholdSchema,
    DataQualityMetricThresholdSchema,
    PredictionDriftMetricThresholdSchema,
    FeatureAttributionDriftMetricThresholdSchema,
    ModelPerformanceMetricThresholdSchema,
)


class DataSegmentSchema(metaclass=PatchedSchemaMeta):
    feature_name = fields.Str()
    feature_values = fields.List(fields.Str)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import DataSegment

        return DataSegment(**data)


class MonitorFeatureFilterSchema(metaclass=PatchedSchemaMeta):
    top_n_feature_importance = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import MonitorFeatureFilter

        return MonitorFeatureFilter(**data)


class TargetDatasetSchema(metaclass=PatchedSchemaMeta):
    dataset = NestedField(MonitorInputDataSchema)
    lookback_period = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import TargetDataset

        return TargetDataset(**data)


class MonitoringSignalSchema(metaclass=PatchedSchemaMeta):
    target_dataset = NestedField(TargetDatasetSchema)
    baseline_dataset = NestedField(MonitorInputDataSchema)


class DataSignalSchema(MonitoringSignalSchema):
    features = UnionField(
        union_fields=[
            fields.List(fields.Str),
            NestedField(MonitorFeatureFilterSchema),
            StringTransformedEnum(allowed_values=ALL_FEATURES),
        ]
    )


class DataDriftSignalSchema(DataSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.DATA_DRIFT, required=True)
    metric_thresholds = fields.List(NestedField(DataDriftMetricThreshold))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import DataDriftSignal

        data.pop("type", None)
        return DataDriftSignal(**data)


class DataQualitySignalSchema(DataSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.DATA_QUALITY, required=True)
    metric_thresholds = fields.List(NestedField(DataQualityMetricThreshold))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import DataQualitySignal

        data.pop("type", None)
        return DataQualitySignal(**data)


class PredictionDriftSignalSchema(MonitoringSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.PREDICTION_DRIFT, required=True)
    metric_thresholds = fields.List(NestedField(PredictionDriftMetricThreshold))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import PredictionDriftSignal

        data.pop("type", None)
        return PredictionDriftSignal(**data)


class ModelSignalSchema(MonitoringSignalSchema):
    model_type = StringTransformedEnum(allowed_values=[MonitorModelType.CLASSIFICATION, MonitorModelType.REGRESSION])


class FeatureAttributionDriftSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT, required=True)
    metric_thresholds = fields.List(NestedField(FeatureAttributionDriftMetricThreshold))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import FeatureAttributionDriftSignal

        data.pop("type", None)
        return FeatureAttributionDriftSignal(**data)


class ModelPerformanceSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.MODEL_PERFORMANCE, required=True)
    data_segment = NestedField(DataSegmentSchema)
    metric_thresholds = fields.List(NestedField(ModelPerformanceMetricThreshold))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import ModelPerformanceSignal

        data.pop("type", None)
        return ModelPerformanceSignal(**data)


class CustomMonitoringSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.CUSTOM, required=True)
    component_id = ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import CustomMonitoringSignal

        data.pop("type", None)
        return CustomMonitoringSignal(**data)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load, pre_dump, ValidationError

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
    CustomMonitoringMetricThresholdSchema,
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

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import MonitorFeatureFilter

        if not isinstance(data, MonitorFeatureFilter):
            raise ValidationError("Cannot dump non-MonitorFeatureFilter object into MonitorFeatureFilter")
        return data

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
    alert_notification = fields.Bool()


class DataSignalSchema(MonitoringSignalSchema):
    features = UnionField(
        union_fields=[
            NestedField(MonitorFeatureFilterSchema),
            StringTransformedEnum(allowed_values=ALL_FEATURES),
            fields.List(fields.Str),
        ]
    )


class DataDriftSignalSchema(DataSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.DATA_DRIFT, required=True)
    metric_thresholds = fields.List(NestedField(DataDriftMetricThresholdSchema))
    data_segment = NestedField(DataSegmentSchema)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import DataDriftSignal

        if not isinstance(data, DataDriftSignal):
            raise ValidationError("Cannot dump non-DataDriftSignal object into DataDriftSignal")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import DataDriftSignal

        data.pop("type", None)
        return DataDriftSignal(**data)


class DataQualitySignalSchema(DataSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.DATA_QUALITY, required=True)
    metric_thresholds = fields.List(NestedField(DataQualityMetricThresholdSchema))

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import DataQualitySignal

        if not isinstance(data, DataQualitySignal):
            raise ValidationError("Cannot dump non-DataQualitySignal object into DataQualitySignal")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import DataQualitySignal

        data.pop("type", None)
        return DataQualitySignal(**data)


class PredictionDriftSignalSchema(MonitoringSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.PREDICTION_DRIFT, required=True)
    metric_thresholds = fields.List(NestedField(PredictionDriftMetricThresholdSchema))

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import PredictionDriftSignal

        if not isinstance(data, PredictionDriftSignal):
            raise ValidationError("Cannot dump non-PredictionDriftSignal object into PredictionDriftSignal")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import PredictionDriftSignal

        data.pop("type", None)
        return PredictionDriftSignal(**data)


class ModelSignalSchema(MonitoringSignalSchema):
    model_type = StringTransformedEnum(allowed_values=[MonitorModelType.CLASSIFICATION, MonitorModelType.REGRESSION])


class FeatureAttributionDriftSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT, required=True)
    metric_thresholds = NestedField(FeatureAttributionDriftMetricThresholdSchema)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import FeatureAttributionDriftSignal

        if not isinstance(data, FeatureAttributionDriftSignal):
            raise ValidationError(
                "Cannot dump non-FeatureAttributionDriftSignal object into FeatureAttributionDriftSignal"
            )
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import FeatureAttributionDriftSignal

        data.pop("type", None)
        return FeatureAttributionDriftSignal(**data)


class ModelPerformanceSignalSchema(ModelSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.MODEL_PERFORMANCE, required=True)
    data_segment = NestedField(DataSegmentSchema)
    metric_thresholds = NestedField(ModelPerformanceMetricThresholdSchema)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import ModelPerformanceSignal

        if not isinstance(data, ModelPerformanceSignal):
            raise ValidationError("Cannot dump non-ModelPerformanceSignal object into ModelPerformanceSignal")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import ModelPerformanceSignal

        data.pop("type", None)
        return ModelPerformanceSignal(**data)


class CustomMonitoringSignalSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.CUSTOM, required=True)
    component_id = ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT)
    metric_thresholds = fields.List(NestedField(CustomMonitoringMetricThresholdSchema))
    input_datasets = fields.Dict(keys=fields.Str(), values=NestedField(MonitorInputDataSchema))
    alert_notification = fields.Bool()

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import CustomMonitoringSignal

        if not isinstance(data, CustomMonitoringSignal):
            raise ValidationError("Cannot dump non-CustomMonitoringSignal object into CustomMonitoringSignal")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import CustomMonitoringSignal

        data.pop("type", None)
        return CustomMonitoringSignal(**data)

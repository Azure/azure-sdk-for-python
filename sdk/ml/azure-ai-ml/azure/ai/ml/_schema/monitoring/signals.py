# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load, pre_dump, ValidationError

from azure.ai.ml._schema.job.input_output_entry import DataInputSchema, MLTableInputSchema
from azure.ai.ml.constants._common import AzureMLResourceType
from azure.ai.ml.constants._monitoring import (
    MonitorSignalType,
    ALL_FEATURES,
    MonitorModelType,
    MonitorDatasetContext,
    FADColumnNames,
)
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, UnionField, StringTransformedEnum
from azure.ai.ml._schema.monitoring.thresholds import (
    DataDriftMetricThresholdSchema,
    DataQualityMetricThresholdSchema,
    PredictionDriftMetricThresholdSchema,
    FeatureAttributionDriftMetricThresholdSchema,
    ModelPerformanceMetricThresholdSchema,
    CustomMonitoringMetricThresholdSchema,
    GenerationSafetyQualityMetricThresholdSchema,
    GenerationTokenStatisticsMonitorMetricThresholdSchema,
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


class BaselineDataRangeSchema(metaclass=PatchedSchemaMeta):
    window_start = fields.Str()
    window_end = fields.Str()
    lookback_window_size = fields.Str()
    lookback_window_offset = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import BaselineDataRange

        return BaselineDataRange(**data)


class ProductionDataSchema(metaclass=PatchedSchemaMeta):
    input_data = UnionField(union_fields=[NestedField(DataInputSchema), NestedField(MLTableInputSchema)])
    data_context = StringTransformedEnum(allowed_values=[o.value for o in MonitorDatasetContext])
    pre_processing_component = fields.Str()
    data_window = NestedField(BaselineDataRangeSchema)
    data_column_names = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import ProductionData

        return ProductionData(**data)


class ReferenceDataSchema(metaclass=PatchedSchemaMeta):
    input_data = UnionField(union_fields=[NestedField(DataInputSchema), NestedField(MLTableInputSchema)])
    data_context = StringTransformedEnum(allowed_values=[o.value for o in MonitorDatasetContext])
    pre_processing_component = fields.Str()
    target_column_name = fields.Str()
    data_window = NestedField(BaselineDataRangeSchema)
    data_column_names = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import ReferenceData

        return ReferenceData(**data)


class MonitoringSignalSchema(metaclass=PatchedSchemaMeta):
    production_data = NestedField(ProductionDataSchema)
    reference_data = NestedField(ReferenceDataSchema)
    properties = fields.Dict()
    alert_enabled = fields.Bool()


class DataSignalSchema(MonitoringSignalSchema):
    features = UnionField(
        union_fields=[
            NestedField(MonitorFeatureFilterSchema),
            StringTransformedEnum(allowed_values=ALL_FEATURES),
            fields.List(fields.Str),
        ]
    )
    feature_type_override = fields.Dict()


class DataDriftSignalSchema(DataSignalSchema):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.DATA_DRIFT, required=True)
    metric_thresholds = NestedField(DataDriftMetricThresholdSchema)
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
    metric_thresholds = NestedField(DataQualityMetricThresholdSchema)

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
    metric_thresholds = NestedField(PredictionDriftMetricThresholdSchema)

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


class FADProductionDataSchema(metaclass=PatchedSchemaMeta):
    input_data = UnionField(union_fields=[NestedField(DataInputSchema), NestedField(MLTableInputSchema)])
    data_context = StringTransformedEnum(allowed_values=[o.value for o in MonitorDatasetContext])
    data_column_names = fields.Dict(
        keys=StringTransformedEnum(allowed_values=[o.value for o in FADColumnNames]), values=fields.Str()
    )
    pre_processing_component = fields.Str()
    data_window = NestedField(BaselineDataRangeSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import FADProductionData

        return FADProductionData(**data)


class FeatureAttributionDriftSignalSchema(metaclass=PatchedSchemaMeta):
    production_data = fields.List(NestedField(FADProductionDataSchema))
    reference_data = NestedField(ReferenceDataSchema)
    alert_enabled = fields.Bool()
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


class ModelPerformanceSignalSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.MODEL_PERFORMANCE, required=True)
    production_data = NestedField(ProductionDataSchema)
    reference_data = NestedField(ReferenceDataSchema)
    data_segment = NestedField(DataSegmentSchema)
    alert_enabled = fields.Bool()
    metric_thresholds = NestedField(ModelPerformanceMetricThresholdSchema)
    properties = fields.Dict()

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


class ConnectionSchema(metaclass=PatchedSchemaMeta):
    environment_variables = fields.Dict(keys=fields.Str(), values=fields.Str())
    secret_config = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import Connection

        return Connection(**data)


class CustomMonitoringSignalSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.CUSTOM, required=True)
    connection = NestedField(ConnectionSchema)
    component_id = ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT)
    metric_thresholds = fields.List(NestedField(CustomMonitoringMetricThresholdSchema))
    input_data = fields.Dict(keys=fields.Str(), values=NestedField(ReferenceDataSchema))
    alert_enabled = fields.Bool()
    inputs = fields.Dict(
        keys=fields.Str, values=UnionField(union_fields=[NestedField(DataInputSchema), NestedField(MLTableInputSchema)])
    )

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


class LlmDataSchema(metaclass=PatchedSchemaMeta):
    input_data = UnionField(union_fields=[NestedField(DataInputSchema), NestedField(MLTableInputSchema)])
    data_column_names = fields.Dict()
    data_window = NestedField(BaselineDataRangeSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import LlmData

        return LlmData(**data)


class GenerationSafetyQualitySchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.GENERATION_SAFETY_QUALITY, required=True)
    production_data = fields.List(NestedField(LlmDataSchema))
    connection_id = fields.Str()
    metric_thresholds = NestedField(GenerationSafetyQualityMetricThresholdSchema)
    alert_enabled = fields.Bool()
    properties = fields.Dict()
    sampling_rate = fields.Float()

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import GenerationSafetyQualitySignal

        if not isinstance(data, GenerationSafetyQualitySignal):
            raise ValidationError("Cannot dump non-GenerationSafetyQuality object into GenerationSafetyQuality")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import GenerationSafetyQualitySignal

        data.pop("type", None)
        return GenerationSafetyQualitySignal(**data)


class GenerationTokenStatisticsSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(allowed_values=MonitorSignalType.GENERATION_TOKEN_STATISTICS, required=True)
    production_data = NestedField(LlmDataSchema)
    metric_thresholds = NestedField(GenerationTokenStatisticsMonitorMetricThresholdSchema)
    alert_enabled = fields.Bool()
    properties = fields.Dict()
    sampling_rate = fields.Float()

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import GenerationTokenStatisticsSignal

        if not isinstance(data, GenerationTokenStatisticsSignal):
            raise ValidationError("Cannot dump non-GenerationSafetyQuality object into GenerationSafetyQuality")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.signals import GenerationTokenStatisticsSignal

        data.pop("type", None)
        return GenerationTokenStatisticsSignal(**data)

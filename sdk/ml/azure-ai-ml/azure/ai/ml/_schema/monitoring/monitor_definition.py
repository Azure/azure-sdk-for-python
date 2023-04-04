# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.monitoring.monitoring_target import MonitoringTargetSchema
from azure.ai.ml._schema.monitoring.monitoring_input_data import MonitorInputDataSchema
from azure.ai.ml._schema.monitoring.monitoring_signals import (
    DataDriftSignalSchema,
    DataQualitySignalSchema,
    PredictionDriftSignalSchema,
    FeatureAttributionDriftSignalSchema,
    ModelPerformanceSignalSchema,
    CustomMonitoringSignalSchema,
)
from azure.ai.ml._schema.monitoring.alert_notification import AlertNotificationSchema
from azure.ai.ml._schema.core.fields import NestedField, UnionField, ComputeField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MonitorDefinitionSchema(metaclass=PatchedSchemaMeta):
    compute = ComputeField()
    monitoring_target = NestedField(MonitoringTargetSchema)
    data_ingestion = NestedField(MonitorInputDataSchema)
    monitoring_signals = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            union_fields=[
                NestedField(DataDriftSignalSchema),
                NestedField(DataQualitySignalSchema),
                NestedField(PredictionDriftSignalSchema),
                NestedField(FeatureAttributionDriftSignalSchema),
                NestedField(ModelPerformanceSignalSchema),
                NestedField(CustomMonitoringSignalSchema),
            ]
        ),
    )
    alert_notification = NestedField(AlertNotificationSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.monitor_definition import MonitorDefinition

        return MonitorDefinition(**data)

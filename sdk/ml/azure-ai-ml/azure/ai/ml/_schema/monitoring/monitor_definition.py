# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml.constants._monitoring import AZMONITORING
from azure.ai.ml._schema.monitoring.target import MonitoringTargetSchema
from azure.ai.ml._schema.monitoring.signals import (
    DataDriftSignalSchema,
    DataQualitySignalSchema,
    PredictionDriftSignalSchema,
    FeatureAttributionDriftSignalSchema,
    CustomMonitoringSignalSchema,
)
from azure.ai.ml._schema.monitoring.alert_notification import AlertNotificationSchema
from azure.ai.ml._schema.core.fields import NestedField, UnionField, ComputeField, StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class MonitorDefinitionSchema(metaclass=PatchedSchemaMeta):
    compute = ComputeField()
    monitoring_target = NestedField(MonitoringTargetSchema)
    monitoring_signals = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            union_fields=[
                NestedField(DataDriftSignalSchema),
                NestedField(DataQualitySignalSchema),
                NestedField(PredictionDriftSignalSchema),
                NestedField(FeatureAttributionDriftSignalSchema),
                NestedField(CustomMonitoringSignalSchema),
            ]
        ),
    )
    alert_notification = UnionField(
        union_fields=[StringTransformedEnum(allowed_values=AZMONITORING), NestedField(AlertNotificationSchema)]
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.definition import MonitorDefinition

        return MonitorDefinition(**data)

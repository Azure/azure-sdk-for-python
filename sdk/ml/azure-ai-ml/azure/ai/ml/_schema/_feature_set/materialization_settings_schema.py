# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.schedule.trigger import RecurrenceTriggerSchema
from azure.ai.ml._schema._notification.notification_schema import NotificationSchema


class MaterializationComputeResourceSchema(metaclass=PatchedSchemaMeta):
    instance_type = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.materialization_compute_resource import MaterializationComputeResource

        return MaterializationComputeResource(instance_type=data.pop("instance_type"), **data)


class MaterializationSettingsSchema(metaclass=PatchedSchemaMeta):
    schedule = NestedField(RecurrenceTriggerSchema)
    notification = NestedField(NotificationSchema)
    resource = NestedField(MaterializationComputeResourceSchema)
    spark_configuration = fields.Dict()
    offline_enabled = fields.Boolean()
    online_enabled = fields.Boolean()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_set.materialization_settings import MaterializationSettings

        return MaterializationSettings(**data)

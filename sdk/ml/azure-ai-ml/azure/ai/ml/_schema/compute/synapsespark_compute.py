# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml.constants._compute import ComputeType

from ..core.fields import NestedField, StringTransformedEnum
from ..core.schema import PathAwareSchema
from .compute import ComputeSchema, IdentitySchema


class AutoScaleSettingsSchema(PathAwareSchema):
    min_node_count = fields.Int(dump_only=True)
    max_node_count = fields.Int(dump_only=True)
    auto_scale_enabled = fields.Bool(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AutoScaleSettings

        return AutoScaleSettings(**data)


class AutoPauseSettingsSchema(PathAwareSchema):
    delay_in_minutes = fields.Int(dump_only=True)
    auto_pause_enabled = fields.Bool(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AutoPauseSettings

        return AutoPauseSettings(**data)


class SynapseSparkComputeSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.SYNAPSESPARK], required=True)
    resource_id = fields.Str(required=True)
    identity = NestedField(IdentitySchema)
    node_family = fields.Str(dump_only=True)
    node_size = fields.Str(dump_only=True)
    node_count = fields.Int(dump_only=True)
    spark_version = fields.Str(dump_only=True)
    scale_settings = NestedField(AutoScaleSettingsSchema)
    auto_pause_settings = NestedField(AutoPauseSettingsSchema)

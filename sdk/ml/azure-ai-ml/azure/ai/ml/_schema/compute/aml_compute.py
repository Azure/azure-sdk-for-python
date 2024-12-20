# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._compute import ComputeTier, ComputeType, ComputeSizeTier

from ..core.fields import NestedField, StringTransformedEnum, UnionField
from .compute import ComputeSchema, IdentitySchema, NetworkSettingsSchema


class AmlComputeSshSettingsSchema(metaclass=PatchedSchemaMeta):
    admin_username = fields.Str()
    admin_password = fields.Str()
    ssh_key_value = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AmlComputeSshSettings

        return AmlComputeSshSettings(**data)


class AmlComputeSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.AMLCOMPUTE], required=True)
    size = UnionField(
        union_fields=[
            fields.Str(metadata={"arm_type": ComputeSizeTier.AML_COMPUTE_DEDICATED, "tier": ComputeTier.DEDICATED}),
            fields.Str(metadata={"arm_type": ComputeSizeTier.AML_COMPUTE_LOWPRIORITY, "tier": ComputeTier.LOWPRIORITY}),
        ],
    )
    tier = StringTransformedEnum(allowed_values=[ComputeTier.LOWPRIORITY, ComputeTier.DEDICATED])
    min_instances = fields.Int()
    max_instances = fields.Int()
    idle_time_before_scale_down = fields.Int()
    ssh_public_access_enabled = fields.Bool()
    ssh_settings = NestedField(AmlComputeSshSettingsSchema)
    network_settings = NestedField(NetworkSettingsSchema)
    identity = NestedField(IdentitySchema)
    enable_node_public_ip = fields.Bool(
        metadata={"description": "Enable or disable node public IP address provisioning."}
    )

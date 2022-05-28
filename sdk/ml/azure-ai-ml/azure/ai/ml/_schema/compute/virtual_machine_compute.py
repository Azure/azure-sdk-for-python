# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from .compute import ComputeSchema
from ..core.fields import StringTransformedEnum, NestedField
from azure.ai.ml.constants import ComputeType
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from marshmallow.decorators import post_load


class VirtualMachineSshSettingsSchema(metaclass=PatchedSchemaMeta):
    admin_username = fields.Str()
    admin_password = fields.Str()
    ssh_port = fields.Int()
    ssh_private_key_file = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import VirtualMachineSshSettings

        return VirtualMachineSshSettings(**data)


class VirtualMachineComputeSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.VIRTUALMACHINE], required=True)
    resource_id = fields.Str(required=True)
    compute_location = fields.Str(dump_only=True)
    ssh_settings = NestedField(VirtualMachineSshSettingsSchema)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from marshmallow.decorators import post_load
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from .compute import ComputeSchema, NetworkSettingsSchema
from .schedule import ComputeSchedulesSchema
from ..core.fields import StringTransformedEnum, NestedField, ExperimentalField
from azure.ai.ml.constants import ComputeType


class ComputeInstanceSshSettingsSchema(metaclass=PatchedSchemaMeta):
    admin_username = fields.Str(dump_only=True)
    ssh_port = fields.Str(dump_only=True)
    ssh_key_value = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ComputeInstanceSshSettings

        return ComputeInstanceSshSettings(**data)


class CreateOnBehalfOfSchema(metaclass=PatchedSchemaMeta):
    user_tenant_id = fields.Str()
    user_object_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AssignedUserConfiguration

        return AssignedUserConfiguration(**data)


class ComputeInstanceSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.COMPUTEINSTANCE], required=True)
    size = fields.Str()
    network_settings = NestedField(NetworkSettingsSchema)
    create_on_behalf_of = NestedField(CreateOnBehalfOfSchema)
    ssh_settings = NestedField(ComputeInstanceSshSettingsSchema)
    ssh_public_access_enabled = fields.Bool(default=None)
    state = fields.Str(dump_only=True)
    last_operation = fields.Dict(keys=fields.Str(), values=fields.Str(), dump_only=True)
    services = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()), dump_only=True)
    schedules = ExperimentalField(NestedField(ComputeSchedulesSchema))

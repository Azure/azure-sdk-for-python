# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml.constants._compute import ComputeType

from ..core.fields import NestedField, StringTransformedEnum
from .compute import ComputeSchema, IdentitySchema


class FabricSparkComputeSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.FABRICSPARK], required=True)
    fabric_workspace_id = fields.Str()
    lakehouse_id = fields.Str()
    environment_id = fields.Str()
    pool_id = fields.Str()
    pool_name = fields.Str(dump_only=True)
    is_attached_compute = fields.Bool(dump_only=True)
    modified_on = fields.Str(dump_only=True)
    disable_local_auth = fields.Bool(dump_only=True)
    identity = NestedField(IdentitySchema)

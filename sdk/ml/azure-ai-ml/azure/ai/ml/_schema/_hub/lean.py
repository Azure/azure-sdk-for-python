# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.workspace.identity import IdentitySchema

class LeanSchema(PathAwareSchema):
    name = fields.Str(required=True)
    location = fields.Str()
    id = fields.Str(dump_only=True)
    resource_group = fields.Str()
    description = fields.Str()
    display_name = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    identity = NestedField(IdentitySchema)
    primary_user_assigned_identity = fields.Str()
    hub_resourceid = fields.Str()

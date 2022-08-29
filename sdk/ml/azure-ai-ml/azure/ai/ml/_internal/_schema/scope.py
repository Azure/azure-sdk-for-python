# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields, post_load
from azure.ai.ml._internal._schema.node import InternalBaseNodeSchema, NodeType
from azure.ai.ml._schema import StringTransformedEnum


class ScopeSchema(InternalBaseNodeSchema):
    type = StringTransformedEnum(allowed_values=[NodeType.SCOPE], casing_transform=lambda x: x)
    adla_account_name = fields.Str(required=True)
    scope_param = fields.Str()
    custom_job_name_suffix = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml._internal.entities.scope import Scope

        return Scope(**data)

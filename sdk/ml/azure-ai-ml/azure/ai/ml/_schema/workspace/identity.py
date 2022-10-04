# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.constants._workspace import ManagedServiceIdentityType
from azure.ai.ml.entities._credentials import IdentityConfiguration, ManagedIdentityConfiguration


class UserAssignedIdentitySchema(metaclass=PatchedSchemaMeta):
    principal_id = fields.Str(required=False)
    client_id = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs):
        return ManagedIdentityConfiguration(**data)


class IdentitySchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[
            ManagedServiceIdentityType.SYSTEM_ASSIGNED,
            ManagedServiceIdentityType.USER_ASSIGNED,
            ManagedServiceIdentityType.NONE,
            ManagedServiceIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED,
        ],
        casing_transform=camel_to_snake,
        metadata={"description": "resource identity type."},
    )
    principal_id = fields.Str(required=False)
    tenant_id = fields.Str(required=False)
    user_assigned_identities = fields.Dict(
        keys=fields.Str(required=True), values=NestedField(UserAssignedIdentitySchema, allow_none=True), allow_none=True
    )

    @post_load
    def make(self, data, **kwargs):
        data["type"] = snake_to_camel(data.pop("type"))
        return IdentityConfiguration(**data)

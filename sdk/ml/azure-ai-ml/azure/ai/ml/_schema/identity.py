# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema import PatchedSchemaMeta, NestedField, StringTransformedEnum, UnionField
from marshmallow import fields, post_load, validates, ValidationError, pre_dump
from azure.ai.ml._restclient.v2021_10_01.models import (
    ResourceIdentity,
)
from azure.ai.ml._vendor.azure_resources.models._resource_management_client_enums import (
    ResourceIdentityType,
)
from azure.ai.ml._utils.utils import camel_to_snake


class IdentitySchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(
        allowed_values=[
            ResourceIdentityType.SYSTEM_ASSIGNED,
            ResourceIdentityType.USER_ASSIGNED,
            ResourceIdentityType.NONE,
            # ResourceIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED, # This is for post PuPr
        ],
        casing_transform=camel_to_snake,
        metadata={"description": "resource identity type."},
    )
    principal_id = fields.Str()
    tenant_id = fields.Str()
    user_assigned_identities = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()))

    @validates("user_assigned_identities")
    def validate_user_assigned_identities(self, data, **kwargs):
        if len(data) > 1:
            raise ValidationError(f"Only 1 user assigned identity is currently supported, {len(data)} found")

    @post_load
    def make(self, data, **kwargs):
        return ResourceIdentity(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        if data.user_assigned_identities:
            ids = []
            for id in data.user_assigned_identities:
                item = {}
                item["resource_id"] = id
                item["principal_id"] = data.user_assigned_identities[id].principal_id
                item["client_id"] = data.user_assigned_identities[id].client_id
                ids.append(item)
            data.user_assigned_identities = ids
        return data

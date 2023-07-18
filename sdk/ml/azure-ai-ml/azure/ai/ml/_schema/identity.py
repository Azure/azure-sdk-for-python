# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import ValidationError, fields, post_load, pre_dump, validates

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._vendor.azure_resources.models._resource_management_client_enums import ResourceIdentityType
from azure.ai.ml.entities._credentials import IdentityConfiguration, ManagedIdentityConfiguration


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
        user_assigned_identities_list = []
        user_assigned_identities = data.pop("user_assigned_identities", None)
        if user_assigned_identities:
            for identity in user_assigned_identities:
                user_assigned_identities_list.append(
                    ManagedIdentityConfiguration(
                        resource_id=identity.get("resource_id", None),
                        client_id=identity.get("client_id", None),
                        object_id=identity.get("object_id", None),
                    )
                )
            data["user_assigned_identities"] = user_assigned_identities_list
        return IdentityConfiguration(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        if data.user_assigned_identities:
            ids = []
            for _id in data.user_assigned_identities:
                item = {}
                item["resource_id"] = _id.resource_id
                item["principal_id"] = _id.principal_id
                item["client_id"] = _id.client_id
                ids.append(item)
            data.user_assigned_identities = ids
        return data

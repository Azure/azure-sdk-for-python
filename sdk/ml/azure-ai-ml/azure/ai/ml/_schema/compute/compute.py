# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._vendor.azure_resources.models._resource_management_client_enums import ResourceIdentityType

from ..core.schema import PathAwareSchema


class ComputeSchema(PathAwareSchema):
    name = fields.Str(required=True)
    id = fields.Str(dump_only=True)
    type = fields.Str()
    location = fields.Str()
    description = fields.Str()
    provisioning_errors = fields.Str(dump_only=True)
    created_on = fields.Str(dump_only=True)
    provisioning_state = fields.Str(dump_only=True)
    resource_id = fields.Str()


class NetworkSettingsSchema(PathAwareSchema):
    vnet_name = fields.Str()
    subnet = fields.Str()
    public_ip_address = fields.Str(dump_only=True)
    private_ip_address = fields.Str(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import NetworkSettings

        return NetworkSettings(**data)


class UserAssignedIdentitySchema(PathAwareSchema):
    resource_id = fields.Str()
    principal_id = fields.Str(dump_only=True)
    client_id = fields.Str(dump_only=True)
    tenant_id = fields.Str(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ManagedIdentityConfiguration

        return ManagedIdentityConfiguration(**data)


class IdentitySchema(PathAwareSchema):
    type = StringTransformedEnum(
        allowed_values=[
            ResourceIdentityType.SYSTEM_ASSIGNED,
            ResourceIdentityType.USER_ASSIGNED,
            ResourceIdentityType.NONE,
            ResourceIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED,
        ],
        casing_transform=camel_to_snake,
        metadata={"description": "resource identity type."},
    )
    user_assigned_identities = fields.List(NestedField(UserAssignedIdentitySchema))
    principal_id = fields.Str(dump_only=True)
    tenant_id = fields.Str(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import IdentityConfiguration

        return IdentityConfiguration(**data)

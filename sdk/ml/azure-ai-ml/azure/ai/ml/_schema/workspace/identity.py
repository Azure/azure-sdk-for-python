# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields
from marshmallow.decorators import post_load, pre_dump

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.constants._workspace import ManagedServiceIdentityType
from azure.ai.ml.entities._credentials import IdentityConfiguration, ManagedIdentityConfiguration


class UserAssignedIdentitySchema(metaclass=PatchedSchemaMeta):
    principal_id = fields.Str(required=False)
    client_id = fields.Str(required=False)
    resource_id = fields.Str(required=False)

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

    @pre_dump
    def predump(self, data, **kwargs):
        if data and isinstance(data, IdentityConfiguration):
            data.user_assigned_identities = self.uai_list2dict(data.user_assigned_identities)
        return data

    @post_load
    def make(self, data, **kwargs):
        if data.get("user_assigned_identities", False):
            data["user_assigned_identities"] = self.uai_dict2list(data.pop("user_assigned_identities"))
        data["type"] = snake_to_camel(data.pop("type"))
        return IdentityConfiguration(**data)

    def uai_dict2list(self, uai_dict):
        res = []
        for resource_id, meta in uai_dict.items():
            if not isinstance(meta, ManagedIdentityConfiguration):
                continue
            c_id = meta.client_id
            p_id = meta.principal_id
            res.append(ManagedIdentityConfiguration(resource_id=resource_id, client_id=c_id, principal_id=p_id))
        return res

    def uai_list2dict(self, uai_list):
        res = {}
        if uai_list and isinstance(uai_list, list):
            for uai in uai_list:
                if not isinstance(uai, ManagedIdentityConfiguration):
                    continue
                meta = {}
                if uai.client_id:
                    meta["client_id"] = uai.client_id
                if uai.principal_id:
                    meta["principal_id"] = uai.principal_id
                res[uai.resource_id] = meta
        return res if res else None

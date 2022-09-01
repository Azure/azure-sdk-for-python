# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class NewAcrAccountSchema(metaclass=PatchedSchemaMeta):
    acr_account_behind_vnet = fields.Bool()
    acr_account_name = fields.Str()
    acr_account_resource_group_name = fields.Str()
    acr_account_sku = fields.Str()

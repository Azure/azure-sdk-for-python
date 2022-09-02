# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, validate

from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta

VALID_STORAGE_ACCOUNT_TYPES = [
    "Standard_LRS",
    "Standard_GRS",
    "Standard_RAGRS",
    "Standard_ZRS",
    # cspell:disable-next-line
    "Standard_GZRS",
    # cspell:disable-next-line
    "Standard_RAGZRS",
    "Premium_LRS",
    "Premium_ZRS",
]


class NewStorageAccountSchema(metaclass=PatchedSchemaMeta):
    storage_account_behind_vnet = fields.Bool()
    storage_account_has_hns_enabled = fields.Bool()
    storage_account_location = fields.Str()
    storage_account_name = fields.Str()
    storage_account_resource_group_name = fields.Str()
    storage_account_type = fields.Str(validate=validate.OneOf(VALID_STORAGE_ACCOUNT_TYPES))

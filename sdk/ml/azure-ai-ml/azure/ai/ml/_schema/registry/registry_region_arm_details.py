# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta

from .acr_details import AcrDetailsSchema
from .storage_account_details import StorageAccountDetailsSchema


class RegistryRegionArmDetailsSchema(metaclass=PatchedSchemaMeta):
    acr_details = fields.List(NestedField(AcrDetailsSchema))
    location = fields.Str()
    storage_account_details = fields.List(NestedField(StorageAccountDetailsSchema))

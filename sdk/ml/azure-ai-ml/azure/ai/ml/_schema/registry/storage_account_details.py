# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta

from .new_storage_account_schema import NewStorageAccountSchema


class StorageAccountDetailsSchema(metaclass=PatchedSchemaMeta):
    # todo add validation based on format listed in line 317 of machineLearningServices-Registries.json once that's verified.
    existing_storage_account = fields.Str()  # arm_resource_id
    new_storage_account = NestedField(NewStorageAccountSchema)

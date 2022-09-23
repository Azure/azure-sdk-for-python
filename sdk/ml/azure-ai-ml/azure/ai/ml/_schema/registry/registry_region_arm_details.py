# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import NestedField, UnionField, DumpableStringField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta

from .system_created_storage_account import SystemCreatedStorageAccountSchema
from .system_created_acr_account import SystemCreatedAcrAccountSchema
from .util import storage_account_validator, acr_format_validator


# Differs from the swagger def in that the acr_details can only be supplied as a
# single registry-wide instance, rather than a per-region list.
class RegistryRegionArmDetailsSchema(metaclass=PatchedSchemaMeta):
    acr_config = fields.List(
        UnionField([DumpableStringField(validate=acr_format_validator), NestedField(SystemCreatedAcrAccountSchema)],
        dump_only=True, is_strict=True)
    )
    location = fields.Str()
    storage_config = fields.List(
        UnionField([DumpableStringField(validate=storage_account_validator), NestedField(SystemCreatedStorageAccountSchema)], is_strict=True)
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import RegistryRegionArmDetails

        data.pop("type", None)
        return RegistryRegionArmDetails(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities import RegistryRegionArmDetails

        if not isinstance(data, RegistryRegionArmDetails):
            raise ValidationError("Cannot dump non-RegistryRegionArmDetails object into RegistryRegionArmDetailsSchema")
        return data

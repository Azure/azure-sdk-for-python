# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import DumpableStringField, NestedField, UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._registry import StorageAccountType
from azure.ai.ml.entities._registry.registry_support_classes import SystemCreatedStorageAccount

from .system_created_acr_account import SystemCreatedAcrAccountSchema
from .system_created_storage_account import SystemCreatedStorageAccountSchema
from .util import acr_format_validator, storage_account_validator


# Differs from the swagger def in that the acr_details can only be supplied as a
# single registry-wide instance, rather than a per-region list.
class RegistryRegionArmDetailsSchema(metaclass=PatchedSchemaMeta):
    acr_config = fields.List(
        UnionField(
            [DumpableStringField(validate=acr_format_validator), NestedField(SystemCreatedAcrAccountSchema)],
            dump_only=True,
            is_strict=True,
        )
    )
    location = fields.Str()
    storage_config = UnionField(
        [
            NestedField(SystemCreatedStorageAccountSchema),
            fields.List(DumpableStringField(validate=storage_account_validator)),
        ],
        is_strict=True,
        load_default=SystemCreatedStorageAccount(
            storage_account_hns=False, storage_account_type=StorageAccountType.STANDARD_LRS
        ),
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

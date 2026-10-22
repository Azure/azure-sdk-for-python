# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import DumpableStringField, NestedField, UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._registry import StorageAccountType
from azure.ai.ml.entities._registry.registry_support_classes import SystemCreatedStorageAccount

from .system_created_storage_account import SystemCreatedStorageAccountSchema
from .util import storage_account_validator


# Differs from the swagger def in that the acr_details can only be supplied as a
# single registry-wide instance, rather than a per-region list.
@experimental
class RegistryRegionDetailsSchema(metaclass=PatchedSchemaMeta):
    # Commenting this out for the time being.
    # We do not want to surface the acr_config as a per-region configurable
    # field. Instead we want to simplify the UX and surface it as a non-list,
    # top-level value called 'container_registry'.
    # We don't even want to show the per-region acr accounts when displaying a
    # registry to the user, so this isn't even left as a dump-only field.
    """acr_config = fields.List(
        UnionField(
            [DumpableStringField(validate=acr_format_validator), NestedField(SystemCreatedAcrAccountSchema)],
            dump_only=True,
            is_strict=True,
        )
    )"""
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
        from azure.ai.ml.entities import RegistryRegionDetails

        data.pop("type", None)
        return RegistryRegionDetails(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities import RegistryRegionDetails

        if not isinstance(data, RegistryRegionDetails):
            raise ValidationError("Cannot dump non-RegistryRegionDetails object into RegistryRegionDetailsSchema")
        return data

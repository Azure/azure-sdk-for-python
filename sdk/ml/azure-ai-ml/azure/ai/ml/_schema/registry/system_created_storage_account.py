# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-self-use,unused-argument

from marshmallow import ValidationError, fields, post_load, pre_dump


from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._registry import StorageAccountType
from azure.ai.ml._utils._experimental import experimental

@experimental
class SystemCreatedStorageAccountSchema(metaclass=PatchedSchemaMeta):
    arm_resource_id = fields.Str(dump_only=True)
    storage_account_hns = fields.Bool()
    storage_account_type = StringTransformedEnum(
        allowed_values=[accountType.value for accountType in StorageAccountType], casing_transform=lambda x: x.lower()
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import SystemCreatedStorageAccount

        data.pop("type", None)
        return SystemCreatedStorageAccount(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities import SystemCreatedStorageAccount

        if not isinstance(data, SystemCreatedStorageAccount):
            raise ValidationError(
                "Cannot dump non-SystemCreatedStorageAccount object into SystemCreatedStorageAccountSchema"
            )
        return data

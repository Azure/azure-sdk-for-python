# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._registry import AcrAccountSku


@experimental
class SystemCreatedAcrAccountSchema(metaclass=PatchedSchemaMeta):
    arm_resource_id = fields.Str(dump_only=True)
    acr_account_sku = StringTransformedEnum(
        allowed_values=[sku.value for sku in AcrAccountSku], casing_transform=lambda x: x.lower()
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import SystemCreatedAcrAccount

        data.pop("type", None)
        return SystemCreatedAcrAccount(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.entities import SystemCreatedAcrAccount

        if not isinstance(data, SystemCreatedAcrAccount):
            raise ValidationError("Cannot dump non-SystemCreatedAcrAccount object into SystemCreatedAcrAccountSchema")
        return data

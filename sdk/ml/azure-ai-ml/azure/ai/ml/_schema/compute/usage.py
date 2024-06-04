# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._restclient.v2022_10_01_preview.models import UsageUnit
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake


class UsageNameSchema(metaclass=PatchedSchemaMeta):
    value = fields.Str()
    localized_value = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import UsageName

        return UsageName(**data)


class UsageSchema(metaclass=PatchedSchemaMeta):
    id = fields.Str()
    aml_workspace_location = fields.Str()
    type = fields.Str()
    unit = UnionField(
        [
            fields.Str(),
            StringTransformedEnum(
                allowed_values=UsageUnit.COUNT,
                casing_transform=camel_to_snake,
            ),
        ]
    )
    current_value = fields.Int()
    limit = fields.Int()
    name = NestedField(UsageNameSchema)

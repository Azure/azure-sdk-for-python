# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, validate, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class DataColumnSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(
        required=True,
        allow_none=False,
    )
    type = fields.Str(
        validate=validate.OneOf(["string", "integer", "long", "float", "double", "binary", "datetime", "boolean"]),
        required=True,
        allow_none=False,
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._feature_store_entity.data_column import DataColumn

        return DataColumn(**data)

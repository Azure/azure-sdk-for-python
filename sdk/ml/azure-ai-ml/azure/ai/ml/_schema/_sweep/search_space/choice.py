# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema._sweep.search_space.normal import NormalSchema, QNormalSchema
from azure.ai.ml._schema._sweep.search_space.randint import RandintSchema
from azure.ai.ml._schema._sweep.search_space.uniform import QUniformSchema, UniformSchema
from azure.ai.ml._schema.core.fields import (
    DumpableIntegerField,
    DumpableStringField,
    NestedField,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml.constants import SearchSpace


class ChoiceSchema(metaclass=PatchedSchemaMeta):
    values = fields.List(
        UnionField(
            [
                DumpableIntegerField(strict=True),
                DumpableStringField(),
                fields.Float(),
                fields.Dict(
                    keys=fields.Str(),
                    values=UnionField(
                        [
                            NestedField("ChoiceSchema"),
                            NestedField(NormalSchema()),
                            NestedField(QNormalSchema()),
                            NestedField(RandintSchema()),
                            NestedField(UniformSchema()),
                            NestedField(QUniformSchema()),
                            DumpableIntegerField(strict=True),
                            fields.Float(),
                            fields.Str(),
                        ]
                    ),
                ),
            ]
        )
    )
    type = StringTransformedEnum(required=True, allowed_values=SearchSpace.CHOICE)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.sweep import Choice

        return Choice(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml.sweep import Choice

        if not isinstance(data, Choice):
            raise ValidationError("Cannot dump non-Choice object into ChoiceSchema")
        return data

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.input_output_entry import (
    InputLiteralValueSchema,
    OutputSchema,
    DataInputSchema,
    ModelInputSchema,
    MLTableInputSchema,
)


def InputsField(**kwargs):
    return fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                # By default when strict is false, marshmallow downcasts float to int.
                # Setting it to true will throw a validation error and try the next types in list.
                # https://github.com/marshmallow-code/marshmallow/pull/755
                NestedField(DataInputSchema),
                NestedField(ModelInputSchema),
                NestedField(MLTableInputSchema),
                NestedField(InputLiteralValueSchema),
                UnionField(
                    [
                        fields.Int(strict=True),
                        fields.Str(),
                        fields.Float(),
                        fields.Bool(),
                    ],
                    is_strict=False,
                ),
                # This ordering of types for the values keyword is intentional. The ordering of types
                # determines what order schema values are matched and cast in. Changing the current ordering can
                # result in values being mis-cast such as 1.0 translating into True.
            ],
            metadata={"description": "Inputs to a job."},
            is_strict=True,
            **kwargs
        ),
    )


def OutputsField(**kwargs):
    return fields.Dict(
        keys=fields.Str(),
        values=NestedField(nested=OutputSchema, allow_none=True),
        metadata={"description": "Outputs of a job."},
        **kwargs
    )

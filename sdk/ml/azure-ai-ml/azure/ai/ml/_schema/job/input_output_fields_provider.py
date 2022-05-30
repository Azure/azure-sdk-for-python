# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema import NestedField, UnionField
from marshmallow import fields
from azure.ai.ml._schema.job.input_output_entry import (
    InputSchema,
    InputLiteralValueSchema,
    OutputSchema,
)


def InputsField(**kwargs):
    return UnionField(
        [
            NestedField(InputSchema),
            fields.Dict(
                keys=fields.Str(),
                values=UnionField(
                    [
                        # By default when strict is false, marshmallow downcasts float to int.
                        # Setting it to true will throw a validation error and try the next types in list.
                        # https://github.com/marshmallow-code/marshmallow/pull/755
                        NestedField(InputSchema),
                        NestedField(InputLiteralValueSchema),
                        fields.Int(strict=True),
                        fields.Str(),
                        fields.Bool(),
                        fields.Float(),
                    ],
                    metadata={"description": "Inputs to a job."},
                    **kwargs
                ),
            ),
        ]
    )


def OutputsField(**kwargs):
    return fields.Dict(
        keys=fields.Str(),
        values=NestedField(OutputSchema, allow_none=True),
        metadata={"description": "Outputs of a job."},
        **kwargs
    )

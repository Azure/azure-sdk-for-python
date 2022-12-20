# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, PrimitiveValueField, UnionField
from azure.ai.ml._schema.job.input_output_entry import (
    DataInputSchema,
    InputLiteralValueSchema,
    MLTableInputSchema,
    ModelInputSchema,
    OutputSchema,
)


def InputsField(**kwargs):
    return fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(DataInputSchema),
                NestedField(ModelInputSchema),
                NestedField(MLTableInputSchema),
                NestedField(InputLiteralValueSchema),
                PrimitiveValueField(is_strict=False),
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

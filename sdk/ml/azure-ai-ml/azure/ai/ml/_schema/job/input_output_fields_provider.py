# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import DumpableFloatField, DumpableIntegerField, NestedField, UnionField
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


def PrimitiveValueField(**kwargs):
    return UnionField(
        [
            # Note: order matters here - to make sure value parsed correctly.
            # By default when strict is false, marshmallow downcasts float to int.
            # Setting it to true will throw a validation error when loading a float to int.
            # https://github.com/marshmallow-code/marshmallow/pull/755
            # Use DumpableIntegerField to make sure there will be validation error when
            # loading/dumping a float to int.
            # note that this field can serialize bool instance but cannot deserialize bool instance.
            DumpableIntegerField(strict=True),
            # Use DumpableFloatField with strict of True to avoid '1'(str) serialized to 1.0(float)
            DumpableFloatField(strict=True),
            # put string schema after Int and Float to make sure they won't dump to string
            fields.Str(),
            # fields.Bool comes last since it'll parse anything non-falsy to True
            fields.Bool(),
        ],
        **kwargs,
    )

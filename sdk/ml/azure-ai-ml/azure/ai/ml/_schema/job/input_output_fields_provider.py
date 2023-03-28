# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema._utils.data_binding_expression import support_data_binding_expression_for_fields
from azure.ai.ml._schema.core.fields import NestedField, PrimitiveValueField, UnionField
from azure.ai.ml._schema.job.input_output_entry import (
    DataInputSchema,
    InputLiteralValueSchema,
    MLTableInputSchema,
    ModelInputSchema,
    OutputSchema,
)


def InputsField(*, support_databinding: bool = False, **kwargs):
    value_fields = [
        NestedField(DataInputSchema),
        NestedField(ModelInputSchema),
        NestedField(MLTableInputSchema),
        NestedField(InputLiteralValueSchema),
        PrimitiveValueField(is_strict=False),
        # This ordering of types for the values keyword is intentional. The ordering of types
        # determines what order schema values are matched and cast in. Changing the current ordering can
        # result in values being mis-cast such as 1.0 translating into True.
    ]

    # As is_strict is set to True, 1 and only 1 value field must be matched.
    # root level data-binding expression has already been covered by PrimitiveValueField;
    # If support_databinding is True, we should only add data-binding expression support for nested fields.
    if support_databinding:
        for field_obj in value_fields:
            if isinstance(field_obj, NestedField):
                support_data_binding_expression_for_fields(field_obj.schema)

    return fields.Dict(
        keys=fields.Str(),
        values=UnionField(value_fields, metadata={"description": "Inputs to a job."}, is_strict=True, **kwargs),
    )


def OutputsField(**kwargs):
    return fields.Dict(
        keys=fields.Str(),
        values=NestedField(nested=OutputSchema, allow_none=True),
        metadata={"description": "Outputs of a job."},
        **kwargs
    )

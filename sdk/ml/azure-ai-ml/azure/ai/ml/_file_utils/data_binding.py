# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Union
from marshmallow import fields, Schema
from azure.ai.ml._schema import NestedField, PathAwareSchema
from azure.ai.ml._schema.core.fields import DataBindingStr, UnionField


def _is_literal(field):
    return not isinstance(field, (NestedField, fields.List, fields.Dict, UnionField))


def _add_data_binding_to_field(field, attrs_to_skip, schema_stack):
    data_binding_field = DataBindingStr()
    if isinstance(field, UnionField):
        for field_obj in field.union_fields:
            if not _is_literal(field_obj):
                _add_data_binding_to_field(field_obj, attrs_to_skip, schema_stack=schema_stack)
        field.union_fields.insert(0, data_binding_field)
    elif isinstance(field, fields.Dict):
        # handle dict, dict value can be None
        if field.value_field is not None:
            field.value_field = _add_data_binding_to_field(field.value_field, attrs_to_skip, schema_stack=schema_stack)
    elif isinstance(field, fields.List):
        # handle list
        field.inner = _add_data_binding_to_field(field.inner, attrs_to_skip, schema_stack=schema_stack)
    elif isinstance(field, NestedField):
        # handle nested field
        support_data_binding_for_fields(field.schema, attrs_to_skip, schema_stack=schema_stack)
    else:
        # change basic fields to union
        field = UnionField(
            [data_binding_field, field],
            data_key=field.data_key,
            attribute=field.attribute,
            dump_only=field.dump_only,
            required=field.required,
        )
    return field


def support_data_binding_for_fields(schema: Union[PathAwareSchema, Schema], attrs_to_skip=None, schema_stack=None):
    """Update fields inside schema to support data binding string.
    Only first layer of recursive schema is supported now.
    """
    if hasattr(schema, "_data_binding_supported") and schema._data_binding_supported:
        return
    else:
        schema._data_binding_supported = True

    if attrs_to_skip is None:
        attrs_to_skip = []
    if schema_stack is None:
        schema_stack = []
    schema_type_name = type(schema).__name__
    if schema_type_name in schema_stack:
        return
    schema_stack.append(schema_type_name)
    for attr, field_obj in schema.load_fields.items():
        if attr not in attrs_to_skip:
            schema.load_fields[attr] = _add_data_binding_to_field(field_obj, attrs_to_skip, schema_stack=schema_stack)
    for attr, field_obj in schema.dump_fields.items():
        if attr not in attrs_to_skip:
            schema.dump_fields[attr] = _add_data_binding_to_field(field_obj, attrs_to_skip, schema_stack=schema_stack)
    schema_stack.pop()

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


def get_pipeline_response(pipeline_response, _, response_headers):
    return pipeline_response


def get_receipt_field_value(field):
    if field is None:
        return field

    # FIXME: find field value refactor
    value = field.value_array or field.value_date or field.value_integer or field.value_number \
            or field.value_object or field.value_phone_number or field.value_string or field.value_time

    return value

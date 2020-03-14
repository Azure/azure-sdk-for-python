# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import date, time


def get_pipeline_response(pipeline_response, _, response_headers):
    return pipeline_response


def get_receipt_field_value(field):
    if field is None:
        return field

    if field.value_time:
        hour, minutes, seconds = field.value_time.split(":")
        return time(int(hour), int(minutes), int(seconds))
    if field.value_date:
        year, month, day = field.value_date.split("-")
        return date(int(year), int(month), int(day))

    # FIXME: find field value refactor
    return field.value_integer or field.value_number or field.value_phone_number or field.value_string

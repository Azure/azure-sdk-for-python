# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import time
from azure.core.exceptions import HttpResponseError

POLLING_INTERVAL = 1


def get_pipeline_response(pipeline_response, _, response_headers):  # pylint: disable=unused-argument
    return pipeline_response


def get_field_scalar_value(field):
    field_type = field.type
    if field_type == "string":
        return field.value_string
    if field_type == "number":
        return field.value_number
    if field_type == "integer":
        return field.value_integer
    if field_type == "date":
        return field.value_date
    if field_type == "phoneNumber":
        return field.value_phone_number
    if field_type == "time":
        hour, minutes, seconds = field.value_time.split(":")
        return time(int(hour), int(minutes), int(seconds))


def get_content_type(form):
    """Source: https://en.wikipedia.org/wiki/Magic_number_(programming)#Magic_numbers_in_files
    """
    if len(form) > 3:
        if form[0] == 0x25 and form[1] == 0x50 and form[2] == 0x44 and form[3] == 0x46:
            return "application/pdf"
        if form[0] == 0xFF and form[1] == 0xD8 and form[-2] == 0xFF and form[-1] == 0xD9:
            return "image/jpeg"
        if form[0] == 0x89 and form[1] == 0x50 and form[2] == 0x4E and form[3] == 0x47:
            return "image/png"
        if form[0] == 0x49 and form[1] == 0x49 and form[2] == 0x2A and form[3] == 0x0:  # little-endian
            return "image/tiff"
        if form[0] == 0x4D and form[1] == 0x4D and form[2] == 0x0 and form[3] == 0x2A:  # big-endian
            return "image/tiff"
    raise HttpResponseError("Content type could not be auto-detected. Please pass the content_type keyword argument.")

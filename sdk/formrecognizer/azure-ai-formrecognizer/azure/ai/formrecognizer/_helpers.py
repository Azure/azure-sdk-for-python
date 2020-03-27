# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import time
POLLING_INTERVAL = 1


def get_field_scalar_value(field):  # pylint: disable=too-many-return-statements
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
        if field.value_time:
            hour, minutes, seconds = field.value_time.split(":")
            return time(int(hour), int(minutes), int(seconds))
        return field.value_time  # service recognized field as time but returned None for value because it wasn't valid
    return None


def get_content_type(form):
    """Source: https://en.wikipedia.org/wiki/Magic_number_(programming)#Magic_numbers_in_files
    """
    if len(form) > 3:
        if form[:4] == bytes([0x25, 0x50, 0x44, 0x46]):
            return "application/pdf"
        if form[:2] == bytes([0xFF, 0xD8]) and form[-2:] == bytes([0xFF, 0xD9]):
            return "image/jpeg"
        if form[:4] == bytes([0x89, 0x50, 0x4E, 0x47]):
            return "image/png"
        if form[:4] == bytes([0x49, 0x49, 0x2A, 0x0]):  # little-endian
            return "image/tiff"
        if form[:4] == bytes([0x4D, 0x4D, 0x0, 0x2A]):  # big-endian
            return "image/tiff"
    raise ValueError("Content type could not be auto-detected. Please pass the content_type keyword argument.")

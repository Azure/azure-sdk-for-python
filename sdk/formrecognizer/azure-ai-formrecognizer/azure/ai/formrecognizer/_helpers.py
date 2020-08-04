# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import re
import six
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.pipeline.transport import HttpTransport
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)
import azure.ai.formrecognizer._models as models

POLLING_INTERVAL = 5
COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"


error_map = {
    404: ResourceNotFoundError,
    409: ResourceExistsError,
    401: ClientAuthenticationError
}


def get_bounding_box(field):
    return [
        models.Point(x=field.bounding_box[0], y=field.bounding_box[1]),
        models.Point(x=field.bounding_box[2], y=field.bounding_box[3]),
        models.Point(x=field.bounding_box[4], y=field.bounding_box[5]),
        models.Point(x=field.bounding_box[6], y=field.bounding_box[7])
    ] if field.bounding_box else None


def adjust_value_type(value_type):
    if value_type == "array":
        value_type = "list"
    if value_type == "number":
        value_type = "float"
    if value_type == "object":
        value_type = "dictionary"
    return value_type


def adjust_confidence(score):
    """Adjust confidence when not returned.
    """
    if score is None:
        return 1.0
    return score


def adjust_text_angle(text_angle):
    """Adjust to (-180, 180]
    """
    if text_angle > 180:
        text_angle -= 360
    return text_angle


def get_elements(field, read_result):
    text_elements = []

    for item in field.elements:
        nums = [int(s) for s in re.findall(r"\d+", item)]
        read = nums[0]
        line = nums[1]
        if len(nums) == 3:
            word = nums[2]
            ocr_word = read_result[read].lines[line].words[word]
            extracted_word = models.FormWord._from_generated(ocr_word, page=read+1)  # pylint: disable=protected-access
            text_elements.append(extracted_word)
            continue
        ocr_line = read_result[read].lines[line]
        extracted_line = models.FormLine._from_generated(ocr_line, page=read+1)  # pylint: disable=protected-access
        text_elements.append(extracted_line)
    return text_elements


def get_field_value(field, value, read_result):  # pylint: disable=too-many-return-statements
    if value is None:
        return value
    if value.type == "string":
        return value.value_string
    if value.type == "number":
        return value.value_number
    if value.type == "integer":
        return value.value_integer
    if value.type == "date":
        return value.value_date
    if value.type == "phoneNumber":
        return value.value_phone_number
    if value.type == "time":
        return value.value_time
    if value.type == "array":
        return [
            models.FormField._from_generated(field, value, read_result)  # pylint: disable=protected-access
            for value in value.value_array
        ]
    if value.type == "object":
        return {
            key: models.FormField._from_generated(key, value, read_result)  # pylint: disable=protected-access
            for key, value in value.value_object.items()
        }
    return None


def get_authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name=COGNITIVE_KEY_HEADER, credential=credential
        )
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError("Unsupported credential: {}. Use an instance of AzureKeyCredential "
                        "or a token credential from azure.identity".format(type(credential)))

    return authentication_policy


def get_content_type(form):
    """Source: https://en.wikipedia.org/wiki/Magic_number_(programming)#Magic_numbers_in_files
    """

    if isinstance(form, six.binary_type):
        return check_beginning_bytes(form)

    if hasattr(form, "read") and hasattr(form, "seek"):
        beginning_bytes = form.read(4)
        form.seek(0)
        return check_beginning_bytes(beginning_bytes)

    raise ValueError("Content type could not be auto-detected because the stream was not readable/seekable. "
                     "Please pass the content_type keyword argument.")


def check_beginning_bytes(form):

    if len(form) > 3:
        if form[:4] == b"\x25\x50\x44\x46":
            return "application/pdf"
        if form[:2] == b"\xff\xd8":
            return "image/jpeg"
        if form[:4] == b"\x89\x50\x4E\x47":
            return "image/png"
        if form[:4] == b"\x49\x49\x2A\x00":  # little-endian
            return "image/tiff"
        if form[:4] == b"\x4D\x4D\x00\x2A":  # big-endian
            return "image/tiff"
    raise ValueError("Content type could not be auto-detected. Please pass the content_type keyword argument.")


class TransportWrapper(HttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
    """
    def __init__(self, transport):
        self._transport = transport

    def send(self, request, **kwargs):
        return self._transport.send(request, **kwargs)

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *args):  # pylint: disable=arguments-differ
        pass

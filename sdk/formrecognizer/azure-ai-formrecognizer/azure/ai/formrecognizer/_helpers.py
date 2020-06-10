# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError
)

POLLING_INTERVAL = 5
COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"


error_map = {
    404: ResourceNotFoundError,
    409: ResourceExistsError,
    401: ClientAuthenticationError
}


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

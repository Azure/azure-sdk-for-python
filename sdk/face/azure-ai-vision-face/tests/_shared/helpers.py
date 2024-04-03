# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .constants import (
    CONFIGURATION_NAME_FACE_API_ENDPOINT,
    CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY
)


def get_face_endpoint(**kwargs):
    return kwargs.pop(CONFIGURATION_NAME_FACE_API_ENDPOINT)


def get_account_key(**kwargs):
    return kwargs.pop(CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY)

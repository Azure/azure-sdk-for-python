# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError

class RequestEntityTooLargeError(HttpResponseError):
    """An error response with status code 413 - Request Entity Too Large"""

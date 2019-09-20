# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError

class AppConfigResourceReadOnlyError(HttpResponseError):
    """An error response with status code 409
    The key is read-only. To allow modification unlock it first."""


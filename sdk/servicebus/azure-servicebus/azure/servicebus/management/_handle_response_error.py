# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from contextlib import contextmanager

from azure.core.exceptions import HttpResponseError


@contextmanager
def _handle_response_error():
    try:
        yield
    except HttpResponseError as response_error:
        try:
            new_response_error = HttpResponseError(
                message=response_error.model.detail,
                response=response_error.response,
                model=response_error.model,
            )
        except AttributeError:
            new_response_error = response_error
        raise new_response_error

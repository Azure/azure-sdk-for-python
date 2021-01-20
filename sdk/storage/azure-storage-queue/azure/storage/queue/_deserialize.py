# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument

from azure.core.exceptions import ResourceExistsError

from ._shared.models import StorageErrorCode
from ._models import QueueProperties


def deserialize_metadata(response, obj, headers):
    raw_metadata = {k: v for k, v in response.http_response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}


def deserialize_queue_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    queue_properties = QueueProperties(
        metadata=metadata,
        **headers
    )
    return queue_properties


def deserialize_queue_creation(response, obj, headers):
    response = response.http_response
    if response.status_code == 204:
        error_code = StorageErrorCode.queue_already_exists
        error = ResourceExistsError(
            message="Queue already exists\nRequestId:{}\nTime:{}\nErrorCode:{}".format(
                headers['x-ms-request-id'],
                headers['Date'],
                error_code
            ),
            response=response)
        error.error_code = error_code
        error.additional_info = {}
        raise error
    return headers

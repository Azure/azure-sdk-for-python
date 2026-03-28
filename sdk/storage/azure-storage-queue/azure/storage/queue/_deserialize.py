# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=unused-argument

from typing import Any, Dict, TYPE_CHECKING

from azure.core.exceptions import ResourceExistsError
from ._models import QueueProperties
from ._shared.models import StorageErrorCode
from ._shared.response_handlers import deserialize_metadata

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse


def deserialize_queue_properties(response: "PipelineResponse", obj: Any, headers: Dict[str, Any]) -> QueueProperties:
    metadata = deserialize_metadata(response, obj, headers)
    queue_properties = QueueProperties(metadata=metadata, **headers)
    return queue_properties


def deserialize_queue_creation(response: "PipelineResponse", obj: Any, headers: Dict[str, Any]) -> Dict[str, Any]:
    response = response.http_response
    if response.status_code == 204:  # type: ignore [attr-defined]
        error_code = StorageErrorCode.queue_already_exists
        error = ResourceExistsError(
            message=(
                "Queue already exists\n"
                f"RequestId:{headers['x-ms-request-id']}\n"
                f"Time:{headers['Date']}\n"
                f"ErrorCode:{error_code}"
            ),
            response=response,  # type: ignore [arg-type]
        )
        error.error_code = error_code  # type: ignore [attr-defined]
        error.additional_info = {}  # type: ignore [attr-defined]
        raise error
    return headers

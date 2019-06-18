# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .models import QueueProperties


def deserialize_metadata(response, obj, headers):
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}

def deserialize_queue_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    queue_properties = QueueProperties(
        metadata=metadata,
        **headers
    )
    return queue_properties
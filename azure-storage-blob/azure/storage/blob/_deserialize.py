# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .models import BlobProperties


def deserialize_metadata(response):
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta")}
    if not raw_metadata:
        return None
    return {k.lstrip("x-ms-"): v for k, v in raw_metadata.items()}


def deserialize_blob_properties(response, obj, headers):
    metadata = deserialize_metadata(response)
    blob_properties = BlobProperties(
        metadata=metadata,
        **headers
    )
    return blob_properties

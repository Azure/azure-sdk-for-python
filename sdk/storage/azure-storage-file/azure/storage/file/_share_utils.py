# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .models import ShareProperties


def deserialize_metadata(response, obj, headers):
    raw_metadata = {k: v for k, v in response.headers.items() if k.startswith("x-ms-meta-")}
    return {k[10:]: v for k, v in raw_metadata.items()}

def deserialize_share_properties(response, obj, headers):
    metadata = deserialize_metadata(response, obj, headers)
    share_properties = ShareProperties(
        metadata=metadata,
        **headers
    )
    return share_properties
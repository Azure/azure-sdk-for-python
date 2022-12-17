# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)


from .batch.batch_endpoint import BatchEndpointSchema
from .online.online_endpoint import KubernetesOnlineEndpointSchema, ManagedOnlineEndpointSchema

__all__ = [
    "BatchEndpointSchema",
    "KubernetesOnlineEndpointSchema",
    "ManagedOnlineEndpointSchema",
]

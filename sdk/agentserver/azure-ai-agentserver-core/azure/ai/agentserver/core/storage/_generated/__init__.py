# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Request/response model classes generated from the Foundry storage TypeSpec contract.

The contract is published in ``Azure/azure-rest-api-specs`` (specification for
Foundry storage); until it is merged there, these models are generated locally
and vendored into this package. Do not import from this package directly outside
``storage/``; the public, documented names are re-exported (with SDK-friendly
aliases matching earlier releases where they differ from the generated/spec
names) from ``azure.ai.agentserver.core.storage``.
"""

from ._models import (
    ApiError,
    ApiErrorResponse,
    CreateItemRequest,
    CreateStateStoreRequest,
    DeletedStateStore,
    DeletedStateStoreItem,
    ListResponseStateStore,
    ListResponseStateStoreItemKey,
    PutItemRequest,
    StateStore,
    StateStoreItem,
    StateStoreItemRef,
    StateStoreItemKey,
    UpdateStateStoreRequest,
)

__all__ = [
    "ApiError",
    "ApiErrorResponse",
    "CreateItemRequest",
    "CreateStateStoreRequest",
    "DeletedStateStore",
    "DeletedStateStoreItem",
    "ListResponseStateStore",
    "ListResponseStateStoreItemKey",
    "PutItemRequest",
    "StateStore",
    "StateStoreItem",
    "StateStoreItemRef",
    "StateStoreItemKey",
    "UpdateStateStoreRequest",
]

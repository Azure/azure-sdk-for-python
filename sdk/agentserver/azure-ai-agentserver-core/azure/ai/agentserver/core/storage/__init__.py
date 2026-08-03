# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Durable state-store client for AgentServer."""

from azure.ai.agentserver.core._experimental import experimental

from ._client import FOUNDRY_TOKEN_SCOPE, FoundryStorageClient
from ._endpoint import FoundryStorageEndpoint
from ._errors import (
    FoundryStorageApiError,
    FoundryStorageBadRequestError,
    FoundryStorageConflictError,
    FoundryStorageError,
    FoundryStorageNotFoundError,
    FoundryStoragePreconditionError,
)
from ._state import DEFAULT_ITEM_TTL_SECONDS, FoundryStateStore
from ._state_serializer import (
    DeletedStateStore,
    DeletedStateStoreItem,
    JSONObject,
    JSONValue,
    StateStoreItemKeyPage,
    Order,
    StateStore,
    StateStoreItem,
    StateStoreItemRef,
    StateStoreItemKey,
)

FoundryStateStore = experimental(FoundryStateStore)
FoundryStorageClient = experimental(FoundryStorageClient)
FoundryStorageEndpoint = experimental(FoundryStorageEndpoint)
FoundryStorageError = experimental(FoundryStorageError)
FoundryStorageApiError = experimental(FoundryStorageApiError)
FoundryStorageBadRequestError = experimental(FoundryStorageBadRequestError)
FoundryStorageConflictError = experimental(FoundryStorageConflictError)
FoundryStorageNotFoundError = experimental(FoundryStorageNotFoundError)
FoundryStoragePreconditionError = experimental(FoundryStoragePreconditionError)

__all__ = [
    "DEFAULT_ITEM_TTL_SECONDS",
    "DeletedStateStore",
    "DeletedStateStoreItem",
    "FOUNDRY_TOKEN_SCOPE",
    "FoundryStateStore",
    "FoundryStorageApiError",
    "FoundryStorageBadRequestError",
    "FoundryStorageConflictError",
    "FoundryStorageClient",
    "FoundryStorageEndpoint",
    "FoundryStorageError",
    "FoundryStorageNotFoundError",
    "FoundryStoragePreconditionError",
    "JSONObject",
    "JSONValue",
    "StateStoreItemKeyPage",
    "Order",
    "StateStore",
    "StateStoreItem",
    "StateStoreItemRef",
    "StateStoreItemKey",
]

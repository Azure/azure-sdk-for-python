# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Durable state-store client for AgentServer."""

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

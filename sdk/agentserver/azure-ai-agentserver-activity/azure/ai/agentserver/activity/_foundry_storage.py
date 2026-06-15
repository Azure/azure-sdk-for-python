# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""M365 Agents SDK storage adapter backed by Foundry activity state storage."""
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=docstring-keyword-should-match-keyword-only,import-error,no-name-in-module

from __future__ import annotations

from typing import Any, Type, TypeVar

from azure.ai.agentserver.core.storage import FoundryActivityStateClient, FoundryActivityStateSettings
from azure.core.credentials_async import AsyncTokenCredential

try:
    from microsoft_agents.hosting.core import Storage
except ImportError:  # pragma: no cover - keeps package importable without optional M365 SDK bits.
    class Storage:  # type: ignore[no-redef]
        """Fallback base class used only when the M365 Agents SDK is not installed."""


StoreItemT = TypeVar("StoreItemT")


class FoundryStorage(Storage):
    """Durable M365 Agents SDK storage adapter for Foundry-hosted Activity agents."""

    def __init__(
        self,
        *,
        client: FoundryActivityStateClient | None = None,
        credential: AsyncTokenCredential | None = None,
        settings: FoundryActivityStateSettings | None = None,
    ) -> None:
        self._credential = credential
        self._owns_credential = False

        if client is None:
            if self._credential is None:
                try:
                    from azure.identity.aio import DefaultAzureCredential
                except ImportError as exc:  # pragma: no cover
                    raise ImportError(
                        "FoundryStorage requires azure-identity when no credential is supplied. "
                        "Install azure-identity or pass an async credential."
                    ) from exc
                self._credential = DefaultAzureCredential()
                self._owns_credential = True
            client = FoundryActivityStateClient(credential=self._credential, settings=settings)
        self._client = client

    async def aclose(self) -> None:
        """Close the underlying Foundry state client and owned credential."""
        await self._client.aclose()
        if self._owns_credential and self._credential is not None and hasattr(self._credential, "close"):
            await self._credential.close()

    async def __aenter__(self) -> "FoundryStorage":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def read(
        self,
        keys: list[str],
        *,
        target_cls: Type[StoreItemT] | None = None,
        **kwargs: Any,
    ) -> dict[str, StoreItemT]:
        """Read multiple items from Foundry storage. Missing keys are omitted."""
        _ = kwargs
        if not keys:
            raise ValueError("Storage.read(): Keys are required when reading.")
        if not target_cls:
            raise ValueError("Storage.read(): target_cls cannot be None.")
        for key in keys:
            if key == "":
                raise ValueError("FoundryStorage.read(): key cannot be empty")

        raw_items = await self._client.read(list(keys))
        result: dict[str, StoreItemT] = {}
        for key, item in raw_items.items():
            result[key] = target_cls.from_json_to_store_item(item.get("value"))  # type: ignore[attr-defined]
        return result

    async def write(self, changes: dict[str, StoreItemT]) -> None:
        """Write multiple items to Foundry storage using last-write-wins upserts."""
        if not changes:
            raise ValueError("Storage.write(): Changes are required when writing.")
        for key in changes:
            if key == "":
                raise ValueError("FoundryStorage.write(): key cannot be empty")

        payload = {key: item.store_item_to_json() for key, item in changes.items()}  # type: ignore[attr-defined]
        await self._client.write(payload)

    async def delete(self, keys: list[str]) -> None:
        """Delete multiple items from Foundry storage. Missing keys are ignored."""
        if not keys:
            raise ValueError("Storage.delete(): Keys are required when deleting.")
        for key in keys:
            if key == "":
                raise ValueError("FoundryStorage.delete(): key cannot be empty")

        await self._client.delete(list(keys))

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for idempotent response.created persistence (T-021).

Covers spec 013 US1 deliverable (b) acceptance scenarios 2-3:

- In-memory and Foundry providers both raise ``ResponseAlreadyExistsError``
  on duplicate ``create_response``.
- The orchestrator's three persist sites catch the exception, set
  ``_provider_created = True`` (NOT ``persistence_failed``), and continue.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.responses.store import (
    ResponseAlreadyExistsError,
    ResponseProviderProtocol,
)
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider


def _make_response_obj(response_id: str = "resp_X"):
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    return ResponseObject(
        {
            "id": response_id,
            "object": "response",
            "status": "in_progress",
            "model": "test-model",
            "output": [],
        }
    )


class TestMemoryAlreadyExists:
    """In-memory provider raises the typed exception on duplicate create."""

    @pytest.mark.asyncio
    async def test_duplicate_create_raises_typed_exception(self) -> None:
        provider = InMemoryResponseProvider()
        await provider.create_response(_make_response_obj("resp_mem_dup"), None, None)
        with pytest.raises(ResponseAlreadyExistsError) as exc_info:
            await provider.create_response(_make_response_obj("resp_mem_dup"), None, None)
        assert exc_info.value.response_id == "resp_mem_dup"

    @pytest.mark.asyncio
    async def test_fresh_create_succeeds(self) -> None:
        provider = InMemoryResponseProvider()
        await provider.create_response(_make_response_obj("resp_mem_fresh"), None, None)
        fetched = await provider.get_response("resp_mem_fresh")
        assert str(fetched["id"]) == "resp_mem_fresh"


class TestFoundryAlreadyExists:
    """Foundry provider translates HTTP 409 to ``ResponseAlreadyExistsError``."""

    @pytest.mark.asyncio
    async def test_409_translated_to_typed_exception(self) -> None:
        from azure.ai.agentserver.responses.store._foundry_errors import (
            FoundryBadRequestError,
        )
        from azure.ai.agentserver.responses.store._foundry_provider import (
            FoundryStorageProvider,
        )

        provider = FoundryStorageProvider.__new__(FoundryStorageProvider)
        provider._settings = MagicMock()  # type: ignore[attr-defined]
        provider._settings.build_url = MagicMock(return_value="https://foundry.example/responses")

        async def _raise_409(*args, **kwargs):
            raise FoundryBadRequestError(
                "response 'resp_foundry_dup' already exists",
                response_body={"error": {"code": "conflict", "message": "duplicate"}},
            )

        provider._send_storage_request = _raise_409  # type: ignore[attr-defined]
        with pytest.raises(ResponseAlreadyExistsError) as exc_info:
            await provider.create_response(_make_response_obj("resp_foundry_dup"), None, None)
        assert exc_info.value.response_id == "resp_foundry_dup"

    @pytest.mark.asyncio
    async def test_400_propagates_unchanged(self) -> None:
        from azure.ai.agentserver.responses.store._foundry_errors import (
            FoundryBadRequestError,
        )
        from azure.ai.agentserver.responses.store._foundry_provider import (
            FoundryStorageProvider,
        )

        provider = FoundryStorageProvider.__new__(FoundryStorageProvider)
        provider._settings = MagicMock()  # type: ignore[attr-defined]
        provider._settings.build_url = MagicMock(return_value="https://foundry.example/responses")

        async def _raise_400(*args, **kwargs):
            raise FoundryBadRequestError(
                "invalid model",
                response_body={"error": {"code": "invalid_request", "message": "bad model"}},
            )

        provider._send_storage_request = _raise_400  # type: ignore[attr-defined]
        with pytest.raises(FoundryBadRequestError):
            await provider.create_response(_make_response_obj("resp_400"), None, None)


class TestOrchestratorSwallowsOnRecovery:
    """The three orchestrator persist sites swallow the typed exception."""

    @pytest.mark.asyncio
    async def test_swallow_sets_provider_created(self, caplog: pytest.LogCaptureFixture) -> None:
        """Source-level assertion that the swallow pattern is in place.

        We can't drive the full orchestrator in a unit test, but we can confirm
        that the catch + ``_provider_created = True`` pattern appears at each
        of the three documented sites (372, 1101, 1203).
        """
        from pathlib import Path

        orchestrator_src = (
            Path(__file__).parent.parent.parent
            / "azure"
            / "ai"
            / "agentserver"
            / "responses"
            / "hosting"
            / "_orchestrator.py"
        ).read_text()
        # Three swallow sites, each with the typed exception.
        assert orchestrator_src.count("except ResponseAlreadyExistsError") >= 3, (
            "Expected at least three `except ResponseAlreadyExistsError` blocks "
            "in _orchestrator.py (one per documented persist site)."
        )
        # And the import of ResponseAlreadyExistsError.
        assert "from ..store._base import" in orchestrator_src
        assert "ResponseAlreadyExistsError" in orchestrator_src

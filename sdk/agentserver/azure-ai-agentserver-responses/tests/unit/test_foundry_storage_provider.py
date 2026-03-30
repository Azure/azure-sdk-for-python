# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for FoundryStorageProvider — validates HTTP request construction and
response deserialization by mocking httpx.AsyncClient responses."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from azure.ai.agentserver.responses.store._foundry_errors import (
    FoundryApiError,
    FoundryBadRequestError,
    FoundryResourceNotFoundError,
)
from azure.ai.agentserver.responses.store._foundry_provider import FoundryStorageProvider
from azure.ai.agentserver.responses.store._foundry_settings import FoundryStorageSettings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_URL = "https://foundry.example.com/storage/"
_SETTINGS = FoundryStorageSettings(storage_base_url=_BASE_URL)

_RESPONSE_DICT: dict[str, Any] = {
    "id": "resp_abc123",
    "object": "response",
    "status": "completed",
    "output": [],
    "model": "gpt-4o",
    "created_at": 1710000000,
}

_INPUT_ITEM_DICT: dict[str, Any] = {
    "id": "item_001",
    "type": "message",
    "role": "user",
    "content": [{"type": "input_text", "text": "hello"}],
}

_OUTPUT_ITEM_DICT: dict[str, Any] = {
    "id": "item_out_001",
    "type": "message",
    "role": "assistant",
    "status": "completed",
    "content": [{"type": "output_text", "text": "hi", "annotations": []}],
}


def _make_credential(token: str = "tok_test") -> Any:
    """Return a mock async credential that always yields *token*."""
    token_obj = MagicMock()
    token_obj.token = token
    cred = AsyncMock()
    cred.get_token = AsyncMock(return_value=token_obj)
    return cred


def _make_response(status_code: int, body: Any) -> httpx.Response:
    """Build a real :class:`httpx.Response` with the given *status_code* and JSON *body*."""
    content = json.dumps(body).encode("utf-8")
    return httpx.Response(status_code=status_code, content=content)


def _make_client(response: httpx.Response) -> MagicMock:
    """Return an httpx.AsyncClient mock whose HTTP methods always return *response*."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.post = AsyncMock(return_value=response)
    client.get = AsyncMock(return_value=response)
    client.delete = AsyncMock(return_value=response)
    return client


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def credential() -> Any:
    return _make_credential()


@pytest.fixture()
def settings() -> FoundryStorageSettings:
    return _SETTINGS


# ===========================================================================
# create_response_async
# ===========================================================================

@pytest.mark.asyncio
async def test_create_response_async__posts_to_responses_endpoint(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.create_response_async(response, None, None)

    call_args = client.post.call_args
    called_url: str = call_args[0][0]
    assert called_url.startswith(f"{_BASE_URL}responses")
    assert "api-version=v1" in called_url


@pytest.mark.asyncio
async def test_create_response_async__sends_correct_envelope(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.create_response_async(response, [MagicMock(as_dict=lambda: _INPUT_ITEM_DICT)], ["prev_item_1"])

    body_bytes: bytes = client.post.call_args.kwargs["content"]
    payload = json.loads(body_bytes.decode("utf-8"))
    assert payload["response"]["id"] == "resp_abc123"
    assert len(payload["input_items"]) == 1
    assert payload["history_item_ids"] == ["prev_item_1"]


@pytest.mark.asyncio
async def test_create_response_async__sends_bearer_token(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    await provider.create_response_async(ResponseObject(_RESPONSE_DICT), None, None)

    headers: dict[str, str] = client.post.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer tok_test"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_create_response_async__raises_foundry_api_error_on_500(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(500, {"error": {"message": "server fault"}}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    with pytest.raises(FoundryApiError) as exc_info:
        await provider.create_response_async(ResponseObject(_RESPONSE_DICT), None, None)

    assert exc_info.value.status_code == 500
    assert "server fault" in exc_info.value.message


# ===========================================================================
# get_response_async
# ===========================================================================

@pytest.mark.asyncio
async def test_get_response_async__gets_correct_url(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, _RESPONSE_DICT))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_response_async("resp_abc123")

    called_url: str = client.get.call_args[0][0]
    assert "responses/resp_abc123" in called_url
    assert "api-version=v1" in called_url


@pytest.mark.asyncio
async def test_get_response_async__returns_deserialized_response(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, _RESPONSE_DICT))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    result = await provider.get_response_async("resp_abc123")

    assert result["id"] == "resp_abc123"
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_get_response_async__raises_not_found_on_404(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(404, {"error": {"message": "not found"}}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    with pytest.raises(FoundryResourceNotFoundError) as exc_info:
        await provider.get_response_async("missing_id")

    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_response_async__url_encodes_special_characters(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, _RESPONSE_DICT))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_response_async("id with spaces/slash")

    called_url: str = client.get.call_args[0][0]
    assert " " not in called_url
    assert "id%20with%20spaces%2Fslash" in called_url


# ===========================================================================
# update_response_async
# ===========================================================================

@pytest.mark.asyncio
async def test_update_response_async__posts_to_response_id_url(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.update_response_async(response)

    called_url: str = client.post.call_args[0][0]
    assert "responses/resp_abc123" in called_url


@pytest.mark.asyncio
async def test_update_response_async__sends_serialized_response_body(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.update_response_async(response)

    body_bytes: bytes = client.post.call_args.kwargs["content"]
    payload = json.loads(body_bytes.decode("utf-8"))
    assert payload["id"] == "resp_abc123"


@pytest.mark.asyncio
async def test_update_response_async__raises_bad_request_on_409(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(409, {"error": {"message": "conflict"}}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    with pytest.raises(FoundryBadRequestError) as exc_info:
        await provider.update_response_async(ResponseObject(_RESPONSE_DICT))

    assert "conflict" in exc_info.value.message


# ===========================================================================
# delete_response_async
# ===========================================================================

@pytest.mark.asyncio
async def test_delete_response_async__sends_delete_to_response_url(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.delete_response_async("resp_abc123")

    called_url: str = client.delete.call_args[0][0]
    assert "responses/resp_abc123" in called_url
    assert "api-version=v1" in called_url


@pytest.mark.asyncio
async def test_delete_response_async__raises_not_found_on_404(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(404, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    with pytest.raises(FoundryResourceNotFoundError):
        await provider.delete_response_async("ghost_id")


# ===========================================================================
# get_input_items_async
# ===========================================================================

@pytest.mark.asyncio
async def test_get_input_items_async__default_params_in_url(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {"data": [_OUTPUT_ITEM_DICT], "object": "list"}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_input_items_async("resp_abc123")

    called_url: str = client.get.call_args[0][0]
    assert "responses/resp_abc123/input_items" in called_url
    assert "limit=20" in called_url
    assert "order=desc" in called_url


@pytest.mark.asyncio
async def test_get_input_items_async__ascending_sets_order_asc(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {"data": []}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_input_items_async("resp_abc123", ascending=True, limit=5)

    called_url: str = client.get.call_args[0][0]
    assert "order=asc" in called_url
    assert "limit=5" in called_url


@pytest.mark.asyncio
async def test_get_input_items_async__cursor_params_appended(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {"data": []}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_input_items_async("resp_abc123", after="item_cursor_1", before="item_cursor_2")

    called_url: str = client.get.call_args[0][0]
    assert "after=item_cursor_1" in called_url
    assert "before=item_cursor_2" in called_url


@pytest.mark.asyncio
async def test_get_input_items_async__returns_deserialized_items(credential: Any, settings: FoundryStorageSettings) -> None:
    paged_body = {"data": [_OUTPUT_ITEM_DICT], "object": "list"}
    client = _make_client(_make_response(200, paged_body))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    items = await provider.get_input_items_async("resp_abc123")

    assert len(items) == 1
    assert items[0]["id"] == "item_out_001"
    assert items[0]["type"] == "message"


@pytest.mark.asyncio
async def test_get_input_items_async__empty_data_returns_empty_list(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {"data": [], "object": "list"}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    items = await provider.get_input_items_async("resp_abc123")

    assert items == []


@pytest.mark.asyncio
async def test_get_input_items_async__cursor_params_omitted_when_none(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, {"data": []}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_input_items_async("resp_abc123", after=None, before=None)

    called_url: str = client.get.call_args[0][0]
    assert "after=" not in called_url
    assert "before=" not in called_url


# ===========================================================================
# get_items_async
# ===========================================================================

@pytest.mark.asyncio
async def test_get_items_async__posts_to_batch_retrieve_endpoint(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, [_OUTPUT_ITEM_DICT, None]))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_items_async(["item_out_001", "missing_id"])

    called_url: str = client.post.call_args[0][0]
    assert "items/batch/retrieve" in called_url
    assert "api-version=v1" in called_url


@pytest.mark.asyncio
async def test_get_items_async__sends_item_ids_in_body(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, [_OUTPUT_ITEM_DICT]))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_items_async(["item_out_001"])

    body_bytes: bytes = client.post.call_args.kwargs["content"]
    payload = json.loads(body_bytes.decode("utf-8"))
    assert payload["item_ids"] == ["item_out_001"]


@pytest.mark.asyncio
async def test_get_items_async__returns_none_for_missing_items(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, [_OUTPUT_ITEM_DICT, None]))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    items = await provider.get_items_async(["item_out_001", "missing_id"])

    assert len(items) == 2
    assert items[0]["id"] == "item_out_001"
    assert items[1] is None


@pytest.mark.asyncio
async def test_get_items_async__preserves_input_order(credential: Any, settings: FoundryStorageSettings) -> None:
    item_a = {**_OUTPUT_ITEM_DICT, "id": "item_a"}
    item_b = {**_OUTPUT_ITEM_DICT, "id": "item_b"}
    client = _make_client(_make_response(200, [item_b, item_a]))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    items = await provider.get_items_async(["id_b", "id_a"])

    assert items[0]["id"] == "item_b"
    assert items[1]["id"] == "item_a"


# ===========================================================================
# get_history_item_ids_async
# ===========================================================================

@pytest.mark.asyncio
async def test_get_history_item_ids_async__gets_to_history_endpoint(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, ["item_h1", "item_h2"]))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_history_item_ids_async(None, None, limit=10)

    called_url: str = client.get.call_args[0][0]
    assert "history/item_ids" in called_url
    assert "api-version=v1" in called_url
    assert "limit=10" in called_url


@pytest.mark.asyncio
async def test_get_history_item_ids_async__returns_list_of_strings(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, ["item_h1", "item_h2"]))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    ids = await provider.get_history_item_ids_async(None, None, limit=10)

    assert ids == ["item_h1", "item_h2"]


@pytest.mark.asyncio
async def test_get_history_item_ids_async__appends_previous_response_id(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, ["item_h1"]))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_history_item_ids_async("prev_resp_99", None, limit=5)

    called_url: str = client.get.call_args[0][0]
    assert "previous_response_id=prev_resp_99" in called_url


@pytest.mark.asyncio
async def test_get_history_item_ids_async__appends_conversation_id(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, []))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_history_item_ids_async(None, "conv_42", limit=3)

    called_url: str = client.get.call_args[0][0]
    assert "conversation_id=conv_42" in called_url


@pytest.mark.asyncio
async def test_get_history_item_ids_async__omits_optional_params_when_none(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(200, []))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    await provider.get_history_item_ids_async(None, None, limit=10)

    called_url: str = client.get.call_args[0][0]
    assert "previous_response_id" not in called_url
    assert "conversation_id" not in called_url


# ===========================================================================
# Error mapping
# ===========================================================================

@pytest.mark.asyncio
async def test_error_mapping__400_raises_bad_request(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(400, {"error": {"message": "invalid input"}}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    with pytest.raises(FoundryBadRequestError) as exc_info:
        await provider.get_response_async("any_id")

    assert "invalid input" in exc_info.value.message


@pytest.mark.asyncio
async def test_error_mapping__generic_status_raises_foundry_api_error(credential: Any, settings: FoundryStorageSettings) -> None:
    client = _make_client(_make_response(503, {}))
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    with pytest.raises(FoundryApiError) as exc_info:
        await provider.get_response_async("any_id")

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_error_mapping__error_message_falls_back_for_non_json_body(credential: Any, settings: FoundryStorageSettings) -> None:
    raw = httpx.Response(status_code=502, content=b"<html>Bad Gateway</html>")
    client = AsyncMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(return_value=raw)
    provider = FoundryStorageProvider(credential, settings=settings, http_client=client)

    with pytest.raises(FoundryApiError) as exc_info:
        await provider.get_response_async("any_id")

    assert "502" in exc_info.value.message


# ===========================================================================
# HTTP client lifecycle
# ===========================================================================

@pytest.mark.asyncio
async def test_aclose__closes_owned_client() -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    provider = FoundryStorageProvider(_make_credential(), settings=_SETTINGS, http_client=mock_client)
    # When the client is supplied explicitly, the provider does NOT own it
    # and should NOT close it.
    await provider.aclose()
    mock_client.aclose.assert_not_called()


@pytest.mark.asyncio
async def test_aclose__does_not_close_externally_provided_client() -> None:
    """Provider should close the client it created internally."""
    internal = AsyncMock()
    with patch("azure.ai.agentserver.responses.store._foundry_provider.httpx.AsyncClient") as MockClient:
        MockClient.return_value = internal

        provider = FoundryStorageProvider(_make_credential(), settings=_SETTINGS)
        await provider.aclose()

        internal.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_context_manager__closes_internal_client_on_exit() -> None:
    internal = AsyncMock()
    with patch("azure.ai.agentserver.responses.store._foundry_provider.httpx.AsyncClient") as MockClient:
        MockClient.return_value = internal

        async with FoundryStorageProvider(_make_credential(), settings=_SETTINGS):
            pass

        internal.aclose.assert_awaited_once()


# ===========================================================================
# FoundryStorageSettings
# ===========================================================================

def test_settings__from_env__reads_foundry_project_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://myproject.foundry.azure.com")
    settings = FoundryStorageSettings.from_env()
    assert settings.storage_base_url == "https://myproject.foundry.azure.com/storage/"


def test_settings__from_env__strips_trailing_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://myproject.foundry.azure.com/")
    settings = FoundryStorageSettings.from_env()
    assert settings.storage_base_url == "https://myproject.foundry.azure.com/storage/"


def test_settings__from_env__raises_if_env_var_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)
    with pytest.raises(EnvironmentError, match="FOUNDRY_PROJECT_ENDPOINT"):
        FoundryStorageSettings.from_env()


def test_settings__from_env__raises_if_not_absolute_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "just-a-hostname")
    with pytest.raises(ValueError, match="FOUNDRY_PROJECT_ENDPOINT"):
        FoundryStorageSettings.from_env()


def test_settings__build_url__includes_api_version() -> None:
    url = _SETTINGS.build_url("responses/abc")
    assert url == f"{_BASE_URL}responses/abc?api-version=v1"


def test_settings__build_url__appends_extra_params_encoded() -> None:
    url = _SETTINGS.build_url("responses", limit="10", order="asc")
    assert "limit=10" in url
    assert "order=asc" in url


def test_settings__build_url__url_encodes_extra_param_values() -> None:
    url = _SETTINGS.build_url("history/item_ids", conversation_id="conv id/1")
    assert "conversation_id=conv%20id%2F1" in url

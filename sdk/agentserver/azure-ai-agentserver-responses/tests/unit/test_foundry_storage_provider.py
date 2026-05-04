# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for FoundryStorageProvider — validates HTTP request construction and
response deserialization by mocking AsyncPipelineClient responses."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.responses._response_context import IsolationContext
from azure.ai.agentserver.responses.store._foundry_errors import (
    FoundryApiError,
    FoundryBadRequestError,
    FoundryResourceNotFoundError,
)
from azure.ai.agentserver.responses._platform_headers import (
    CHAT_ISOLATION_KEY as _CHAT_ISOLATION_HEADER,
    USER_ISOLATION_KEY as _USER_ISOLATION_HEADER,
)
from azure.ai.agentserver.responses.store._foundry_provider import (
    FoundryStorageProvider,
)
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


def _make_response(status_code: int, body: Any) -> MagicMock:
    """Build a mock azure.core.rest.HttpResponse with the given *status_code* and JSON *body*."""
    content = json.dumps(body).encode("utf-8")
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = MagicMock(return_value=content.decode("utf-8"))
    return resp


def _make_provider(credential: Any, settings: FoundryStorageSettings, response: MagicMock) -> FoundryStorageProvider:
    """Create a FoundryStorageProvider with a mocked pipeline client."""
    provider = FoundryStorageProvider.__new__(FoundryStorageProvider)
    provider._settings = settings
    mock_client = AsyncMock()
    mock_client.send_request = AsyncMock(return_value=response)
    mock_client.close = AsyncMock()
    provider._client = mock_client
    return provider


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
# create_response
# ===========================================================================


@pytest.mark.asyncio
async def test_create_response__posts_to_responses_endpoint(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.create_response(response, None, None)

    request = provider._client.send_request.call_args[0][0]
    assert request.method == "POST"
    assert request.url.startswith(f"{_BASE_URL}responses")
    assert "api-version=v1" in request.url


@pytest.mark.asyncio
async def test_create_response__sends_correct_envelope(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.create_response(response, [MagicMock(as_dict=lambda: _INPUT_ITEM_DICT)], ["prev_item_1"])

    request = provider._client.send_request.call_args[0][0]
    payload = json.loads(request.content.decode("utf-8"))
    assert payload["response"]["id"] == "resp_abc123"
    assert len(payload["input_items"]) == 1
    assert payload["history_item_ids"] == ["prev_item_1"]


@pytest.mark.asyncio
async def test_create_response__raises_foundry_api_error_on_500(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(500, {"error": {"message": "server fault"}}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    with pytest.raises(FoundryApiError) as exc_info:
        await provider.create_response(ResponseObject(_RESPONSE_DICT), None, None)

    assert "server fault" in exc_info.value.message


# ===========================================================================
# get_response
# ===========================================================================


@pytest.mark.asyncio
async def test_get_response__gets_correct_url(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, _RESPONSE_DICT))

    await provider.get_response("resp_abc123")

    request = provider._client.send_request.call_args[0][0]
    assert request.method == "GET"
    assert "responses/resp_abc123" in request.url
    assert "api-version=v1" in request.url


@pytest.mark.asyncio
async def test_get_response__returns_deserialized_response(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, _RESPONSE_DICT))

    result = await provider.get_response("resp_abc123")

    assert result["id"] == "resp_abc123"
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_get_response__raises_not_found_on_404(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(404, {"error": {"message": "not found"}}))

    with pytest.raises(FoundryResourceNotFoundError) as exc_info:
        await provider.get_response("missing_id")

    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_response__url_encodes_special_characters(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, _RESPONSE_DICT))

    await provider.get_response("id with spaces/path")

    request = provider._client.send_request.call_args[0][0]
    assert " " not in request.url
    assert "id%20with%20spaces%2Fpath" in request.url


# ===========================================================================
# update_response
# ===========================================================================


@pytest.mark.asyncio
async def test_update_response__posts_to_response_id_url(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.update_response(response)

    request = provider._client.send_request.call_args[0][0]
    assert request.method == "POST"
    assert "responses/resp_abc123" in request.url


@pytest.mark.asyncio
async def test_update_response__sends_serialized_response_body(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    response = ResponseObject(_RESPONSE_DICT)
    await provider.update_response(response)

    request = provider._client.send_request.call_args[0][0]
    payload = json.loads(request.content.decode("utf-8"))
    assert payload["id"] == "resp_abc123"


@pytest.mark.asyncio
async def test_update_response__raises_bad_request_on_409(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(409, {"error": {"message": "conflict"}}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    with pytest.raises(FoundryBadRequestError) as exc_info:
        await provider.update_response(ResponseObject(_RESPONSE_DICT))

    assert "conflict" in exc_info.value.message


# ===========================================================================
# delete_response
# ===========================================================================


@pytest.mark.asyncio
async def test_delete_response__sends_delete_to_response_url(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))

    await provider.delete_response("resp_abc123")

    request = provider._client.send_request.call_args[0][0]
    assert request.method == "DELETE"
    assert "responses/resp_abc123" in request.url
    assert "api-version=v1" in request.url


@pytest.mark.asyncio
async def test_delete_response__raises_not_found_on_404(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(404, {}))

    with pytest.raises(FoundryResourceNotFoundError):
        await provider.delete_response("ghost_id")


# ===========================================================================
# get_input_items
# ===========================================================================


@pytest.mark.asyncio
async def test_get_input_items__default_params_in_url(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(
        credential, settings, _make_response(200, {"data": [_OUTPUT_ITEM_DICT], "object": "list"})
    )

    await provider.get_input_items("resp_abc123")

    request = provider._client.send_request.call_args[0][0]
    assert "responses/resp_abc123/input_items" in request.url
    assert "limit=20" in request.url
    assert "order=desc" in request.url


@pytest.mark.asyncio
async def test_get_input_items__ascending_sets_order_asc(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {"data": []}))

    await provider.get_input_items("resp_abc123", ascending=True, limit=5)

    request = provider._client.send_request.call_args[0][0]
    assert "order=asc" in request.url
    assert "limit=5" in request.url


@pytest.mark.asyncio
async def test_get_input_items__cursor_params_appended(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {"data": []}))

    await provider.get_input_items("resp_abc123", after="item_cursor_1", before="item_cursor_2")

    request = provider._client.send_request.call_args[0][0]
    assert "after=item_cursor_1" in request.url
    assert "before=item_cursor_2" in request.url


@pytest.mark.asyncio
async def test_get_input_items__returns_deserialized_items(credential: Any, settings: FoundryStorageSettings) -> None:
    paged_body = {"data": [_OUTPUT_ITEM_DICT], "object": "list"}
    provider = _make_provider(credential, settings, _make_response(200, paged_body))

    items = await provider.get_input_items("resp_abc123")

    assert len(items) == 1
    assert items[0]["id"] == "item_out_001"
    assert items[0]["type"] == "message"


@pytest.mark.asyncio
async def test_get_input_items__empty_data_returns_empty_list(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {"data": [], "object": "list"}))

    items = await provider.get_input_items("resp_abc123")

    assert items == []


@pytest.mark.asyncio
async def test_get_input_items__cursor_params_omitted_when_none(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {"data": []}))

    await provider.get_input_items("resp_abc123", after=None, before=None)

    request = provider._client.send_request.call_args[0][0]
    assert "after=" not in request.url
    assert "before=" not in request.url


# ===========================================================================
# get_items
# ===========================================================================


@pytest.mark.asyncio
async def test_get_items__posts_to_batch_retrieve_endpoint(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, [_OUTPUT_ITEM_DICT, None]))

    await provider.get_items(["item_out_001", "missing_id"])

    request = provider._client.send_request.call_args[0][0]
    assert request.method == "POST"
    assert "items/batch/retrieve" in request.url
    assert "api-version=v1" in request.url


@pytest.mark.asyncio
async def test_get_items__sends_item_ids_in_body(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, [_OUTPUT_ITEM_DICT]))

    await provider.get_items(["item_out_001"])

    request = provider._client.send_request.call_args[0][0]
    payload = json.loads(request.content.decode("utf-8"))
    assert payload["item_ids"] == ["item_out_001"]


@pytest.mark.asyncio
async def test_get_items__returns_none_for_missing_items(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, [_OUTPUT_ITEM_DICT, None]))

    items = await provider.get_items(["item_out_001", "missing_id"])

    assert len(items) == 2
    assert items[0]["id"] == "item_out_001"
    assert items[1] is None


@pytest.mark.asyncio
async def test_get_items__preserves_input_order(credential: Any, settings: FoundryStorageSettings) -> None:
    item_a = {**_OUTPUT_ITEM_DICT, "id": "item_a"}
    item_b = {**_OUTPUT_ITEM_DICT, "id": "item_b"}
    provider = _make_provider(credential, settings, _make_response(200, [item_b, item_a]))

    items = await provider.get_items(["id_b", "id_a"])

    assert items[0]["id"] == "item_b"
    assert items[1]["id"] == "item_a"


# ===========================================================================
# get_history_item_ids
# ===========================================================================


@pytest.mark.asyncio
async def test_get_history_item_ids__gets_to_history_endpoint(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(200, ["item_h1", "item_h2"]))

    await provider.get_history_item_ids(None, None, limit=10)

    request = provider._client.send_request.call_args[0][0]
    assert request.method == "GET"
    assert "history/item_ids" in request.url
    assert "api-version=v1" in request.url
    assert "limit=10" in request.url


@pytest.mark.asyncio
async def test_get_history_item_ids__returns_list_of_strings(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, ["item_h1", "item_h2"]))

    ids = await provider.get_history_item_ids(None, None, limit=10)

    assert ids == ["item_h1", "item_h2"]


@pytest.mark.asyncio
async def test_get_history_item_ids__appends_previous_response_id(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(200, ["item_h1"]))

    await provider.get_history_item_ids("prev_resp_99", None, limit=5)

    request = provider._client.send_request.call_args[0][0]
    assert "previous_response_id=prev_resp_99" in request.url


@pytest.mark.asyncio
async def test_get_history_item_ids__appends_conversation_id(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, []))

    await provider.get_history_item_ids(None, "conv_42", limit=3)

    request = provider._client.send_request.call_args[0][0]
    assert "conversation_id=conv_42" in request.url


@pytest.mark.asyncio
async def test_get_history_item_ids__omits_optional_params_when_none(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(200, []))

    await provider.get_history_item_ids(None, None, limit=10)

    request = provider._client.send_request.call_args[0][0]
    assert "previous_response_id" not in request.url
    assert "conversation_id" not in request.url


# ===========================================================================
# Isolation headers (S-018)
# ===========================================================================


@pytest.mark.asyncio
async def test_create_response__sends_isolation_headers(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    isolation = IsolationContext(user_key="u_key_1", chat_key="c_key_1")
    await provider.create_response(ResponseObject(_RESPONSE_DICT), None, None, isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_key_1"
    assert request.headers[_CHAT_ISOLATION_HEADER] == "c_key_1"


@pytest.mark.asyncio
async def test_get_response__sends_isolation_headers(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, _RESPONSE_DICT))

    isolation = IsolationContext(user_key="u_key_2", chat_key="c_key_2")
    await provider.get_response("resp_abc123", isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_key_2"
    assert request.headers[_CHAT_ISOLATION_HEADER] == "c_key_2"


@pytest.mark.asyncio
async def test_update_response__sends_isolation_headers(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))
    from azure.ai.agentserver.responses.models._generated import ResponseObject

    isolation = IsolationContext(user_key="u_key_3", chat_key="c_key_3")
    await provider.update_response(ResponseObject(_RESPONSE_DICT), isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_key_3"
    assert request.headers[_CHAT_ISOLATION_HEADER] == "c_key_3"


@pytest.mark.asyncio
async def test_delete_response__sends_isolation_headers(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {}))

    isolation = IsolationContext(user_key="u_key_4", chat_key="c_key_4")
    await provider.delete_response("resp_abc123", isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_key_4"
    assert request.headers[_CHAT_ISOLATION_HEADER] == "c_key_4"


@pytest.mark.asyncio
async def test_get_input_items__sends_isolation_headers(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, {"data": []}))

    isolation = IsolationContext(user_key="u_key_5", chat_key="c_key_5")
    await provider.get_input_items("resp_abc123", isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_key_5"
    assert request.headers[_CHAT_ISOLATION_HEADER] == "c_key_5"


@pytest.mark.asyncio
async def test_get_items__sends_isolation_headers(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, [_OUTPUT_ITEM_DICT]))

    isolation = IsolationContext(user_key="u_key_6", chat_key="c_key_6")
    await provider.get_items(["item_out_001"], isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_key_6"
    assert request.headers[_CHAT_ISOLATION_HEADER] == "c_key_6"


@pytest.mark.asyncio
async def test_get_history_item_ids__sends_isolation_headers(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(200, []))

    isolation = IsolationContext(user_key="u_key_7", chat_key="c_key_7")
    await provider.get_history_item_ids(None, None, limit=10, isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_key_7"
    assert request.headers[_CHAT_ISOLATION_HEADER] == "c_key_7"


@pytest.mark.asyncio
async def test_isolation_headers__omitted_when_none(credential: Any, settings: FoundryStorageSettings) -> None:
    """When isolation=None (default), no isolation headers are sent."""
    provider = _make_provider(credential, settings, _make_response(200, _RESPONSE_DICT))

    await provider.get_response("resp_abc123")

    request = provider._client.send_request.call_args[0][0]
    assert _USER_ISOLATION_HEADER not in request.headers
    assert _CHAT_ISOLATION_HEADER not in request.headers


@pytest.mark.asyncio
async def test_isolation_headers__partial_keys_only_sends_present(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    """When only user_key is set, only user header is added."""
    provider = _make_provider(credential, settings, _make_response(200, _RESPONSE_DICT))

    isolation = IsolationContext(user_key="u_only")
    await provider.get_response("resp_abc123", isolation=isolation)

    request = provider._client.send_request.call_args[0][0]
    assert request.headers[_USER_ISOLATION_HEADER] == "u_only"
    assert _CHAT_ISOLATION_HEADER not in request.headers


# ===========================================================================
# Error mapping
# ===========================================================================


@pytest.mark.asyncio
async def test_error_mapping__400_raises_bad_request(credential: Any, settings: FoundryStorageSettings) -> None:
    provider = _make_provider(credential, settings, _make_response(400, {"error": {"message": "invalid input"}}))

    with pytest.raises(FoundryBadRequestError) as exc_info:
        await provider.get_response("any_id")

    assert "invalid input" in exc_info.value.message


@pytest.mark.asyncio
async def test_error_mapping__generic_status_raises_foundry_api_error(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    provider = _make_provider(credential, settings, _make_response(503, {}))

    with pytest.raises(FoundryApiError) as exc_info:
        await provider.get_response("any_id")

    assert "503" in exc_info.value.message


@pytest.mark.asyncio
async def test_error_mapping__error_message_falls_back_for_non_json_body(
    credential: Any, settings: FoundryStorageSettings
) -> None:
    raw = MagicMock()
    raw.status_code = 502
    raw.text = MagicMock(return_value="<html>Bad Gateway</html>")
    provider = _make_provider(credential, settings, raw)

    with pytest.raises(FoundryApiError) as exc_info:
        await provider.get_response("any_id")

    assert "502" in exc_info.value.message


# ===========================================================================
# HTTP client lifecycle
# ===========================================================================


@pytest.mark.asyncio
async def test_aclose__closes_pipeline_client() -> None:
    provider = _make_provider(_make_credential(), _SETTINGS, _make_response(200, {}))
    await provider.aclose()
    provider._client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_context_manager__closes_client_on_exit() -> None:
    provider = _make_provider(_make_credential(), _SETTINGS, _make_response(200, {}))
    async with provider:
        pass
    provider._client.close.assert_awaited_once()


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
    with pytest.raises(ValueError, match="valid absolute URL"):
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

"""Contract tests for GET /responses/{response_id}/input_items behavior."""

from __future__ import annotations

from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

from azure.ai.agentserver.responses._hosting import map_responses_server


class _NoopResponseHandler:
    """Minimal handler used to wire the hosting surface in contract tests."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            if False:  # pragma: no cover - required to keep async-generator shape.
                yield None

        return _events()


def _build_client() -> TestClient:
    app = Starlette()
    map_responses_server(app, _NoopResponseHandler())
    return TestClient(app)


def _message_input(item_id: str, text: str) -> dict[str, Any]:
    return {
        "id": item_id,
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": text}],
    }


def _create_response(
    client: TestClient,
    *,
    input_items: list[dict[str, Any]] | None,
    store: bool = True,
    background: bool = False,
    previous_response_id: str | None = None,
) -> str:
    payload: dict[str, Any] = {
        "model": "gpt-4o-mini",
        "stream": False,
        "store": store,
        "background": background,
        "input": input_items if input_items is not None else [],
    }
    if previous_response_id is not None:
        payload["previous_response_id"] = previous_response_id

    create_response = client.post("/responses", json=payload)
    assert create_response.status_code == 200
    response_id = create_response.json().get("id")
    assert isinstance(response_id, str)
    return response_id


def _assert_error_envelope(response: Any, expected_status: int) -> dict[str, Any]:
    assert response.status_code == expected_status
    try:
        payload = response.json()
    except Exception as exc:  # pragma: no cover - defensive diagnostics for routing regressions.
        raise AssertionError(
            f"Expected JSON error envelope with status {expected_status}, got non-JSON body: {response.text!r}"
        ) from exc
    assert isinstance(payload.get("error"), dict)
    assert "message" in payload["error"]
    assert "type" in payload["error"]
    assert "param" in payload["error"]
    assert "code" in payload["error"]
    return payload


def test_input_items_returns_200_with_items_and_paged_fields() -> None:
    client = _build_client()

    response_id = _create_response(
        client,
        input_items=[
            _message_input("msg_001", "one"),
            _message_input("msg_002", "two"),
            _message_input("msg_003", "three"),
        ],
    )

    response = client.get(f"/responses/{response_id}/input_items")
    assert response.status_code == 200
    payload = response.json()

    assert payload.get("object") == "list"
    assert isinstance(payload.get("data"), list)
    assert len(payload["data"]) == 3
    assert payload["data"][0].get("id") == "msg_003"
    assert payload["data"][2].get("id") == "msg_001"
    assert payload.get("first_id") == "msg_003"
    assert payload.get("last_id") == "msg_001"
    assert payload.get("has_more") is False


def test_input_items_returns_200_with_empty_data() -> None:
    client = _build_client()

    response_id = _create_response(client, input_items=[])

    response = client.get(f"/responses/{response_id}/input_items")
    assert response.status_code == 200
    payload = response.json()

    assert payload.get("object") == "list"
    assert payload.get("data") == []
    assert payload.get("has_more") is False


def test_input_items_returns_400_for_invalid_limit() -> None:
    client = _build_client()

    response_id = _create_response(client, input_items=[_message_input("msg_001", "one")])

    low_limit = client.get(f"/responses/{response_id}/input_items?limit=0")
    low_payload = _assert_error_envelope(low_limit, 400)
    assert low_payload["error"].get("type") == "invalid_request_error"

    high_limit = client.get(f"/responses/{response_id}/input_items?limit=101")
    high_payload = _assert_error_envelope(high_limit, 400)
    assert high_payload["error"].get("type") == "invalid_request_error"


def test_input_items_returns_400_for_invalid_order() -> None:
    client = _build_client()

    response_id = _create_response(client, input_items=[_message_input("msg_001", "one")])

    response = client.get(f"/responses/{response_id}/input_items?order=invalid")
    payload = _assert_error_envelope(response, 400)
    assert payload["error"].get("type") == "invalid_request_error"


def test_input_items_returns_400_for_deleted_response() -> None:
    client = _build_client()

    response_id = _create_response(client, input_items=[_message_input("msg_001", "one")])

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200

    response = client.get(f"/responses/{response_id}/input_items")
    payload = _assert_error_envelope(response, 400)
    assert payload["error"].get("type") == "invalid_request_error"
    assert "deleted" in (payload["error"].get("message") or "").lower()


def test_input_items_returns_404_for_missing_or_non_stored_response() -> None:
    client = _build_client()

    missing_response = client.get("/responses/resp_does_not_exist/input_items")
    missing_payload = _assert_error_envelope(missing_response, 404)
    assert missing_payload["error"].get("type") == "invalid_request_error"

    non_stored_id = _create_response(
        client,
        input_items=[_message_input("msg_001", "one")],
        store=False,
    )
    non_stored_response = client.get(f"/responses/{non_stored_id}/input_items")
    non_stored_payload = _assert_error_envelope(non_stored_response, 404)
    assert non_stored_payload["error"].get("type") == "invalid_request_error"


def test_input_items_default_limit_is_20_and_has_more_when_truncated() -> None:
    client = _build_client()

    input_items = [_message_input(f"msg_{index:03d}", f"item-{index:03d}") for index in range(1, 26)]
    response_id = _create_response(client, input_items=input_items)

    response = client.get(f"/responses/{response_id}/input_items")
    assert response.status_code == 200
    payload = response.json()

    assert payload.get("object") == "list"
    assert isinstance(payload.get("data"), list)
    assert len(payload["data"]) == 20
    assert payload.get("has_more") is True
    assert payload.get("first_id") == "msg_025"
    assert payload.get("last_id") == "msg_006"


def test_input_items_supports_order_and_cursor_pagination() -> None:
    client = _build_client()

    response_id = _create_response(
        client,
        input_items=[
            _message_input("msg_001", "one"),
            _message_input("msg_002", "two"),
            _message_input("msg_003", "three"),
            _message_input("msg_004", "four"),
        ],
    )

    asc_response = client.get(f"/responses/{response_id}/input_items?order=asc&limit=2")
    assert asc_response.status_code == 200
    asc_payload = asc_response.json()
    assert [item.get("id") for item in asc_payload.get("data", [])] == ["msg_001", "msg_002"]
    assert asc_payload.get("first_id") == "msg_001"
    assert asc_payload.get("last_id") == "msg_002"
    assert asc_payload.get("has_more") is True

    after_response = client.get(f"/responses/{response_id}/input_items?order=asc&after=msg_002")
    assert after_response.status_code == 200
    after_payload = after_response.json()
    assert [item.get("id") for item in after_payload.get("data", [])] == ["msg_003", "msg_004"]

    before_response = client.get(f"/responses/{response_id}/input_items?order=asc&before=msg_004")
    assert before_response.status_code == 200
    before_payload = before_response.json()
    assert [item.get("id") for item in before_payload.get("data", [])] == ["msg_001", "msg_002", "msg_003"]


def test_input_items_returns_history_plus_current_input_in_desc_order() -> None:
    client = _build_client()

    first_response_id = _create_response(
        client,
        input_items=[
            _message_input("msg_hist_001", "history-1"),
            _message_input("msg_hist_002", "history-2"),
        ],
    )

    second_response_id = _create_response(
        client,
        input_items=[_message_input("msg_curr_001", "current-1")],
        previous_response_id=first_response_id,
    )

    response = client.get(f"/responses/{second_response_id}/input_items?order=desc")
    assert response.status_code == 200
    payload = response.json()

    assert [item.get("id") for item in payload.get("data", [])] == [
        "msg_curr_001",
        "msg_hist_002",
        "msg_hist_001",
    ]
    assert payload.get("first_id") == "msg_curr_001"
    assert payload.get("last_id") == "msg_hist_001"
    assert payload.get("has_more") is False

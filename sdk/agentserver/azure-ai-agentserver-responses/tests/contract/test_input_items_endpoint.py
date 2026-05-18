# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for GET /responses/{response_id}/input_items behavior."""

from __future__ import annotations

from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire the hosting surface in contract tests."""

    async def _events():
        if False:  # pragma: no cover - required to keep async-generator shape.
            yield None

    return _events()


def _build_client() -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(_noop_response_handler)
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
    # Items are converted to OutputItem with generated IDs (msg_ prefix)
    for item in payload["data"]:
        assert item.get("id", "").startswith("msg_")
        assert item.get("type") == "message"
    assert payload.get("first_id") is not None
    assert payload.get("last_id") is not None
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
    assert low_payload["error"].get("code") == "invalid_request_error"

    high_limit = client.get(f"/responses/{response_id}/input_items?limit=101")
    high_payload = _assert_error_envelope(high_limit, 400)
    assert high_payload["error"].get("type") == "invalid_request_error"
    assert high_payload["error"].get("code") == "invalid_request_error"


def test_input_items_returns_400_for_invalid_order() -> None:
    client = _build_client()

    response_id = _create_response(client, input_items=[_message_input("msg_001", "one")])

    response = client.get(f"/responses/{response_id}/input_items?order=invalid")
    payload = _assert_error_envelope(response, 400)
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("code") == "invalid_request_error"


def test_input_items_returns_404_for_deleted_response() -> None:
    client = _build_client()

    response_id = _create_response(client, input_items=[_message_input("msg_001", "one")])

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200

    response = client.get(f"/responses/{response_id}/input_items")
    payload = _assert_error_envelope(response, 404)
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("code") == "invalid_request_error"


def test_input_items_returns_404_for_missing_or_non_stored_response() -> None:
    from azure.ai.agentserver.responses._id_generator import IdGenerator

    client = _build_client()
    unknown_id = IdGenerator.new_response_id()

    missing_response = client.get(f"/responses/{unknown_id}/input_items")
    missing_payload = _assert_error_envelope(missing_response, 404)
    assert missing_payload["error"].get("type") == "invalid_request_error"
    assert missing_payload["error"].get("code") == "invalid_request_error"

    non_stored_id = _create_response(
        client,
        input_items=[_message_input("msg_001", "one")],
        store=False,
    )
    non_stored_response = client.get(f"/responses/{non_stored_id}/input_items")
    non_stored_payload = _assert_error_envelope(non_stored_response, 404)
    assert non_stored_payload["error"].get("type") == "invalid_request_error"
    assert non_stored_payload["error"].get("code") == "invalid_request_error"


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
    # first_id and last_id should be valid generated msg_ IDs
    assert payload.get("first_id", "").startswith("msg_")
    assert payload.get("last_id", "").startswith("msg_")


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

    # Ascending order, limit=2
    asc_response = client.get(f"/responses/{response_id}/input_items?order=asc&limit=2")
    assert asc_response.status_code == 200
    asc_payload = asc_response.json()
    assert len(asc_payload.get("data", [])) == 2
    assert asc_payload.get("has_more") is True
    _first_id = asc_payload["data"][0].get("id")  # noqa: F841
    second_id = asc_payload["data"][1].get("id")

    # Cursor-based: after second item should return items 3 & 4
    after_response = client.get(f"/responses/{response_id}/input_items?order=asc&after={second_id}")
    assert after_response.status_code == 200
    after_payload = after_response.json()
    assert len(after_payload.get("data", [])) == 2

    # Cursor-based: before last of all items should return first 3
    all_asc = client.get(f"/responses/{response_id}/input_items?order=asc")
    all_ids = [item.get("id") for item in all_asc.json().get("data", [])]
    before_response = client.get(f"/responses/{response_id}/input_items?order=asc&before={all_ids[-1]}")
    assert before_response.status_code == 200
    before_payload = before_response.json()
    assert len(before_payload.get("data", [])) == 3


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

    # Should have 3 items: 2 from history + 1 current.
    # Items have generated IDs; verify count and structure.
    assert len(payload.get("data", [])) == 3
    for item in payload["data"]:
        assert item.get("id", "").startswith("msg_")
        assert item.get("type") == "message"
    assert payload.get("has_more") is False


# ---------------------------------------------------------------------------
# Task 6.1 — input_items sourced from parsed model
# ---------------------------------------------------------------------------


def test_input_items_string_input_treated_as_message() -> None:
    """T1: string input is expanded to an ItemMessage and converted to OutputItemMessage."""
    client = _build_client()

    # Send a create request where 'input' is a plain string, not a list.
    create_response = client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "stream": False, "store": True, "input": "hello"},
    )
    assert create_response.status_code == 200
    response_id = create_response.json().get("id")
    assert isinstance(response_id, str)

    response = client.get(f"/responses/{response_id}/input_items")
    assert response.status_code == 200
    payload = response.json()
    # String input is expanded to a single ItemMessage → OutputItemMessage
    assert len(payload.get("data", [])) == 1
    assert payload["data"][0].get("type") == "message"
    assert payload["data"][0].get("role") == "user"


def test_input_items_list_input_preserved() -> None:
    """T2: list input items are preserved and retrievable via GET /input_items."""
    client = _build_client()

    item = {"id": "msg_x01", "type": "message", "role": "user", "content": [{"type": "input_text", "text": "hi"}]}
    response_id = _create_response(client, input_items=[item])

    response = client.get(f"/responses/{response_id}/input_items?order=asc")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload.get("data", [])) == 1
    # ID is generated (not preserved from input), but type and content are
    assert payload["data"][0].get("id", "").startswith("msg_")
    assert payload["data"][0].get("type") == "message"
    assert payload["data"][0].get("role") == "user"


def test_previous_response_id_propagated() -> None:
    """T3: previous_response_id is propagated so input_items chain walk works."""
    client = _build_client()

    parent_id = _create_response(
        client,
        input_items=[_message_input("msg_parent_001", "parent-item")],
    )
    child_id = _create_response(
        client,
        input_items=[_message_input("msg_child_001", "child-item")],
        previous_response_id=parent_id,
    )

    response = client.get(f"/responses/{child_id}/input_items?order=asc")
    assert response.status_code == 200
    payload = response.json()
    # Both parent and child items appear (2 total), all with generated msg_ IDs
    assert len(payload.get("data", [])) == 2
    for item in payload["data"]:
        assert item.get("id", "").startswith("msg_")
        assert item.get("type") == "message"


def test_empty_previous_response_id_handled() -> None:
    """T4: an empty string for previous_response_id should not raise; treated as absent."""
    client = _build_client()

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "stream": False,
            "store": True,
            "input": [],
            "previous_response_id": "",
        },
    )
    # The server should accept the request (empty string treated as absent).
    assert create_response.status_code == 200
    response_id = create_response.json().get("id")
    assert isinstance(response_id, str)

    response = client.get(f"/responses/{response_id}/input_items")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Task 6.2 — provider/runtime_state branch alignment + pagination edge cases
# ---------------------------------------------------------------------------


def test_input_items_in_flight_fallback_to_runtime() -> None:
    """T3: background response stores input_items that are retrievable via GET.

    Uses a fast handler so the TestClient doesn't block.  After the background
    response completes, input items are available from either the provider or
    the runtime_state fallback.
    """
    from typing import Any as _Any

    def _fast_handler(request: _Any, context: _Any, cancellation_signal: _Any):
        async def _events():
            yield {"type": "response.created", "response": {"status": "in_progress", "output": []}}

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_fast_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    item = _message_input("inflight_msg_001", "in-flight-content")
    payload: Any = {
        "model": "gpt-4o-mini",
        "stream": False,
        "store": True,
        "background": True,
        "input": [item],
    }
    create_response = client.post("/responses", json=payload)
    assert create_response.status_code == 200
    response_id = create_response.json().get("id")
    assert isinstance(response_id, str)

    # GET /input_items — items are returned from either runtime_state or provider
    items_response = client.get(f"/responses/{response_id}/input_items")
    assert items_response.status_code == 200
    items_payload = items_response.json()
    assert items_payload.get("object") == "list"
    assert len(items_payload.get("data", [])) == 1
    assert items_payload["data"][0].get("id", "").startswith("msg_")
    assert items_payload["data"][0].get("type") == "message"


def test_input_items_limit_boundary_1() -> None:
    """T4: limit=1 returns exactly one item."""
    client = _build_client()

    response_id = _create_response(
        client,
        input_items=[
            _message_input("msg_a", "a"),
            _message_input("msg_b", "b"),
        ],
    )

    response = client.get(f"/responses/{response_id}/input_items?limit=1")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload.get("data", [])) == 1
    assert payload.get("has_more") is True


def test_input_items_limit_boundary_100() -> None:
    """T5: limit=100 returns at most 100 items."""
    client = _build_client()

    input_items = [_message_input(f"msg_{i:03d}", f"item-{i}") for i in range(1, 51)]
    response_id = _create_response(client, input_items=input_items)

    response = client.get(f"/responses/{response_id}/input_items?order=asc&limit=100")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload.get("data", [])) == 50
    assert payload.get("has_more") is False

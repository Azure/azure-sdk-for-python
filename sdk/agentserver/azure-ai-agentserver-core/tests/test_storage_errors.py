# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for storage error mapping (raise_for_storage_error)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from azure.ai.agentserver.core._platform_headers import PLATFORM_ERROR_TAG
from azure.ai.agentserver.core.storage import (
    FoundryStorageApiError,
    FoundryStorageBadRequestError,
    FoundryStorageConflictError,
    FoundryStorageError,
    FoundryStorageNotFoundError,
    FoundryStoragePreconditionError,
)
from azure.ai.agentserver.core.storage._errors import raise_for_storage_error


class _FakeResponse:
    def __init__(self, status_code: int, body: Any, *, headers: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self.headers: dict[str, str] = {} if headers is None else headers
        self._body = "" if body is None else json.dumps(body)

    def text(self) -> str:
        return self._body


def test_2xx_does_not_raise() -> None:
    raise_for_storage_error(_FakeResponse(204, None))


def test_404_maps_to_not_found() -> None:
    with pytest.raises(FoundryStorageNotFoundError) as exc:
        raise_for_storage_error(_FakeResponse(404, {"error": {"message": "nope"}}))
    assert exc.value.message == "nope"
    assert exc.value.status_code == 404


def test_400_maps_to_bad_request_and_param() -> None:
    with pytest.raises(FoundryStorageBadRequestError) as exc:
        raise_for_storage_error(_FakeResponse(400, {"error": {"message": "bad", "param": "item_ttl_seconds"}}))
    assert exc.value.param == "item_ttl_seconds"


def test_409_maps_to_bad_request() -> None:
    with pytest.raises(FoundryStorageBadRequestError) as exc:
        raise_for_storage_error(_FakeResponse(409, {"error": {"message": "duplicate"}}))
    assert isinstance(exc.value, FoundryStorageConflictError)
    assert exc.value.status_code == 409


def test_412_maps_to_precondition_with_current_etag() -> None:
    with pytest.raises(FoundryStoragePreconditionError) as exc:
        raise_for_storage_error(
            _FakeResponse(412, {"error": {"message": "etag"}}, headers={"ETag": '"0x8DD"'})
        )
    assert exc.value.current_etag == '"0x8DD"'


def test_412_without_current_etag_defaults_to_none() -> None:
    with pytest.raises(FoundryStoragePreconditionError) as exc:
        raise_for_storage_error(_FakeResponse(412, {"error": {"message": "etag"}}))
    assert exc.value.current_etag is None


def test_500_maps_to_api_error_and_tagged_platform() -> None:
    with pytest.raises(FoundryStorageApiError) as exc:
        raise_for_storage_error(_FakeResponse(500, {"error": {"message": "boom"}}))
    assert getattr(exc.value, PLATFORM_ERROR_TAG) is True


def test_non_json_body_uses_fallback_message() -> None:
    resp = _FakeResponse(503, None)
    resp._body = "<html>not json</html>"
    with pytest.raises(FoundryStorageApiError) as exc:
        raise_for_storage_error(resp)
    assert "HTTP 503" in exc.value.message
    assert exc.value.response_body is None


def test_error_hierarchy_is_catchable_as_base() -> None:
    with pytest.raises(FoundryStorageError):
        raise_for_storage_error(_FakeResponse(404, {"error": {"message": "x"}}))

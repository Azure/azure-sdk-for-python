# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for storage pipeline policies (URL masking, UA policy)."""

from __future__ import annotations

from unittest.mock import MagicMock

from azure.ai.agentserver.core.storage._policies import (
    ServerVersionUserAgentPolicy,
    _mask_storage_url,
)


def test_mask_keeps_only_storage_path_and_api_version() -> None:
    url = "https://proj.example.com/api/projects/secret/storage/state_stores/abc/items:keys?api-version=v1&after=it_1"
    masked = _mask_storage_url(url)
    assert masked == "***/storage/state_stores/*/items:keys?api-version=v1"
    assert "secret" not in masked
    assert "after=it_1" not in masked
    assert "abc" not in masked


def test_mask_without_storage_segment_is_fully_redacted() -> None:
    assert _mask_storage_url("https://proj.example.com/other/path") == "(redacted)"


def test_mask_empty_url_is_redacted() -> None:
    assert _mask_storage_url("") == "(redacted)"


def test_mask_malformed_url_is_redacted() -> None:
    assert _mask_storage_url(None) == "(redacted)"  # type: ignore[arg-type]  # defensive branch


def test_user_agent_policy_evaluates_callback_per_request() -> None:
    versions = iter(["ua-1", "ua-2"])
    policy = ServerVersionUserAgentPolicy(lambda: next(versions))

    req1 = MagicMock()
    req1.http_request.headers = {}
    policy.on_request(req1)
    assert req1.http_request.headers["User-Agent"] == "ua-1"

    req2 = MagicMock()
    req2.http_request.headers = {}
    policy.on_request(req2)
    assert req2.http_request.headers["User-Agent"] == "ua-2"

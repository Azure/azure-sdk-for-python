# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for _sanitize_id edge cases."""

import uuid

import pytest

from azure.ai.agentserver.activity._activity import _sanitize_id


def test_valid_alphanumeric_id():
    assert _sanitize_id("abc123") == "abc123"


def test_valid_id_with_special_chars():
    assert _sanitize_id("my-agent_v1.0:beta") == "my-agent_v1.0:beta"


def test_empty_string_returns_uuid():
    result = _sanitize_id("")
    uuid.UUID(result)  # should not raise


def test_whitespace_only_returns_uuid():
    result = _sanitize_id("   ")
    uuid.UUID(result)


def test_exactly_256_chars_is_valid():
    value = "a" * 256
    assert _sanitize_id(value) == value


def test_257_chars_returns_uuid():
    value = "a" * 257
    result = _sanitize_id(value)
    assert result != value
    uuid.UUID(result)


def test_spaces_return_uuid():
    result = _sanitize_id("id with spaces")
    uuid.UUID(result)


def test_html_returns_uuid():
    result = _sanitize_id("<script>alert(1)</script>")
    assert "<script>" not in result
    uuid.UUID(result)


def test_newline_returns_uuid():
    result = _sanitize_id("id\r\ninjection")
    uuid.UUID(result)


def test_slash_returns_uuid():
    result = _sanitize_id("path/traversal")
    uuid.UUID(result)

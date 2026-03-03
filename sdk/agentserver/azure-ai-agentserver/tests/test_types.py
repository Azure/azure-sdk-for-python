# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for InvokeRequest dataclass."""
import pytest

from azure.ai.agentserver import InvokeRequest


class TestInvokeRequest:
    """Tests for the InvokeRequest dataclass."""

    def test_invoke_request_fields(self):
        """InvokeRequest has body, headers, invocation_id fields."""
        req = InvokeRequest(body=b"test", headers={"k": "v"}, invocation_id="abc")
        assert hasattr(req, "body")
        assert hasattr(req, "headers")
        assert hasattr(req, "invocation_id")

    def test_invoke_request_body_is_bytes(self):
        """body field accepts and stores bytes."""
        req = InvokeRequest(body=b"hello", headers={}, invocation_id="id")
        assert isinstance(req.body, bytes)
        assert req.body == b"hello"

    def test_invoke_request_headers_is_dict(self):
        """headers field is dict[str, str]."""
        headers = {"Content-Type": "application/json", "X-Custom": "val"}
        req = InvokeRequest(body=b"", headers=headers, invocation_id="id")
        assert isinstance(req.headers, dict)
        assert req.headers == headers

    def test_invoke_request_invocation_id_is_str(self):
        """invocation_id is a string."""
        req = InvokeRequest(body=b"", headers={}, invocation_id="test-id-123")
        assert isinstance(req.invocation_id, str)
        assert req.invocation_id == "test-id-123"

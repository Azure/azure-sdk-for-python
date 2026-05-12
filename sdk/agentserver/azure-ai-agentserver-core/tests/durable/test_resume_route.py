# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the resume HTTP route."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette

from azure.ai.agentserver.core.durable._resume_route import create_resume_route


def _build_test_app() -> Starlette:
    """Create a minimal Starlette app with the resume route."""
    return Starlette(routes=[create_resume_route()])


class TestResumeRoute:
    """Tests for POST /tasks/resume."""

    def test_missing_body_returns_400(self) -> None:
        """Request without body returns 400."""
        app = _build_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/tasks/resume", content=b"not json")
        assert resp.status_code == 400

    def test_missing_task_id_returns_400(self) -> None:
        """Request without task_id returns 400."""
        app = _build_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/tasks/resume", json={})
        assert resp.status_code == 400

    def test_non_string_task_id_returns_400(self) -> None:
        """Request with non-string task_id returns 400."""
        app = _build_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/tasks/resume", json={"task_id": 123})
        assert resp.status_code == 400

    @patch("azure.ai.agentserver.core.durable._manager.get_task_manager")
    def test_successful_resume_returns_202(self, mock_get: AsyncMock) -> None:
        """Successful resume returns 202 with empty body."""
        mock_manager = AsyncMock()
        mock_manager.handle_resume = AsyncMock()
        mock_get.return_value = mock_manager

        app = _build_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/tasks/resume", json={"task_id": "task-123"})
        assert resp.status_code == 202
        assert resp.content == b""

    @patch("azure.ai.agentserver.core.durable._manager.get_task_manager")
    def test_not_found_returns_404(self, mock_get: AsyncMock) -> None:
        """Resume of nonexistent task returns 404."""
        mock_manager = AsyncMock()
        mock_manager.handle_resume = AsyncMock(side_effect=ValueError("Task 'xyz' not found"))
        mock_get.return_value = mock_manager

        app = _build_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/tasks/resume", json={"task_id": "xyz"})
        assert resp.status_code == 404

    @patch("azure.ai.agentserver.core.durable._manager.get_task_manager")
    def test_conflict_returns_409(self, mock_get: AsyncMock) -> None:
        """Resume of task not in 'suspended' state returns 409."""
        mock_manager = AsyncMock()
        mock_manager.handle_resume = AsyncMock(side_effect=ValueError("Task is 'in_progress', not 'suspended'"))
        mock_get.return_value = mock_manager

        app = _build_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/tasks/resume", json={"task_id": "task-123"})
        assert resp.status_code == 409

    @patch(
        "azure.ai.agentserver.core.durable._manager.get_task_manager",
        side_effect=RuntimeError("No manager"),
    )
    def test_no_manager_returns_503(self, mock_get: AsyncMock) -> None:
        """When no manager is configured, returns 503."""
        app = _build_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/tasks/resume", json={"task_id": "task-123"})
        assert resp.status_code == 503

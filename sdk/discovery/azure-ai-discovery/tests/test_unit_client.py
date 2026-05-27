# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Unit tests for azure-ai-discovery clients.

These tests verify client configuration without making HTTP calls.
"""
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.discovery import WorkspaceClient, BookshelfClient


class TestWorkspaceClientUnit:
    """Unit tests for Workspace client initialization."""

    def test_client_initialization(self):
        """Test that client can be initialized with endpoint and credential."""
        # Create client with fake endpoint (won't make HTTP calls)
        client = WorkspaceClient(
            endpoint="https://fake-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify client is created
        assert client is not None

    def test_client_has_expected_operations(self):
        """Test that client exposes expected operation groups."""
        client = WorkspaceClient(
            endpoint="https://fake-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify operation groups exist
        assert hasattr(client, "conversations")
        assert hasattr(client, "tasks")
        assert hasattr(client, "investigations")
        assert hasattr(client, "tools")

    def test_client_endpoint_validation(self):
        """Test that client accepts valid endpoint URLs."""
        # Valid HTTPS endpoint
        client = WorkspaceClient(
            endpoint="https://my-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )
        assert client is not None


class TestBookshelfClientUnit:
    """Unit tests for Bookshelf client initialization."""

    def test_client_initialization(self):
        """Test that client can be initialized with endpoint and credential."""
        # Create client with fake endpoint (won't make HTTP calls)
        client = BookshelfClient(
            endpoint="https://fake-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify client is created
        assert client is not None

    def test_client_has_expected_operations(self):
        """Test that client exposes expected operation groups."""
        client = BookshelfClient(
            endpoint="https://fake-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify operation groups exist
        assert hasattr(client, "knowledge_bases")
        assert hasattr(client, "knowledge_base_versions")

    def test_client_endpoint_validation(self):
        """Test that client accepts valid endpoint URLs."""
        # Valid HTTPS endpoint
        client = BookshelfClient(
            endpoint="https://my-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )
        assert client is not None


class TestExplicitTransportKwarg:
    """Verify that ``transport`` is exposed as an explicit keyword-only parameter
    on every client constructor (sync + async, Workspace + Bookshelf).

    Required by the Azure SDK for Python design guideline:
    https://azure.github.io/azure-sdk/python_design.html#python-client-constructor-transport-argument
    """

    @pytest.mark.parametrize(
        "client_cls_path",
        [
            "azure.ai.discovery.WorkspaceClient",
            "azure.ai.discovery.BookshelfClient",
            "azure.ai.discovery.aio.WorkspaceClient",
            "azure.ai.discovery.aio.BookshelfClient",
        ],
    )
    def test_transport_is_explicit_kw_only(self, client_cls_path):
        """``transport`` must be an explicit keyword-only parameter."""
        import importlib
        import inspect

        module_path, _, class_name = client_cls_path.rpartition(".")
        client_cls = getattr(importlib.import_module(module_path), class_name)

        params = inspect.signature(client_cls.__init__).parameters
        assert "transport" in params, f"{client_cls_path}.__init__ must expose ``transport`` as an explicit parameter"
        assert (
            params["transport"].kind == inspect.Parameter.KEYWORD_ONLY
        ), f"{client_cls_path}.__init__ ``transport`` must be keyword-only"
        assert params["transport"].default is None, f"{client_cls_path}.__init__ ``transport`` must default to None"

    @pytest.mark.parametrize(
        "client_cls_path",
        [
            "azure.ai.discovery.WorkspaceClient",
            "azure.ai.discovery.BookshelfClient",
            "azure.ai.discovery.aio.WorkspaceClient",
            "azure.ai.discovery.aio.BookshelfClient",
        ],
    )
    def test_api_version_is_explicit_kw_only(self, client_cls_path):
        """``api_version`` must be an explicit keyword-only parameter.

        Required by the Azure SDK Python design guideline (pylint C4748):
        https://azure.github.io/azure-sdk/python_design.html#specifying-the-service-version
        """
        import importlib
        import inspect

        module_path, _, class_name = client_cls_path.rpartition(".")
        client_cls = getattr(importlib.import_module(module_path), class_name)

        params = inspect.signature(client_cls.__init__).parameters
        assert (
            "api_version" in params
        ), f"{client_cls_path}.__init__ must expose ``api_version`` as an explicit parameter"
        assert (
            params["api_version"].kind == inspect.Parameter.KEYWORD_ONLY
        ), f"{client_cls_path}.__init__ ``api_version`` must be keyword-only"
        assert params["api_version"].default is None, f"{client_cls_path}.__init__ ``api_version`` must default to None"

    def test_sync_clients_accept_transport_argument(self):
        """Sync clients should accept a ``transport`` instance without error."""
        from unittest.mock import MagicMock
        from azure.core.pipeline.transport import HttpTransport

        fake_transport = MagicMock(spec=HttpTransport)
        ws = WorkspaceClient(
            endpoint="https://fake-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
            transport=fake_transport,
        )
        assert ws is not None

        bs = BookshelfClient(
            endpoint="https://fake-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
            transport=fake_transport,
        )
        assert bs is not None

    def test_async_clients_accept_transport_argument(self):
        """Async clients should accept an ``AsyncHttpTransport`` instance without error."""
        from unittest.mock import MagicMock
        from azure.core.pipeline.transport import AsyncHttpTransport
        from azure.ai.discovery.aio import (
            WorkspaceClient as AsyncWorkspaceClient,
            BookshelfClient as AsyncBookshelfClient,
        )

        fake_transport = MagicMock(spec=AsyncHttpTransport)
        ws = AsyncWorkspaceClient(
            endpoint="https://fake-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
            transport=fake_transport,
        )
        assert ws is not None

        bs = AsyncBookshelfClient(
            endpoint="https://fake-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
            transport=fake_transport,
        )
        assert bs is not None

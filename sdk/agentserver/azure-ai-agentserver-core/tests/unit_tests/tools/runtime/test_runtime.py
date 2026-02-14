# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _runtime.py - testing public methods of DefaultFoundryToolRuntime."""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from azure.ai.agentserver.core.tools.runtime._runtime import (
    create_tool_runtime,
    DefaultFoundryToolRuntime,
    ThrowingFoundryToolRuntime,
)
from azure.ai.agentserver.core.tools.runtime._catalog import DefaultFoundryToolCatalog
from azure.ai.agentserver.core.tools.runtime._resolver import DefaultFoundryToolInvocationResolver
from azure.ai.agentserver.core.tools.runtime._user import ContextVarUserProvider


class TestDefaultFoundryToolRuntimeInit:
    """Tests for DefaultFoundryToolRuntime initialization."""

    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_init_creates_client_with_endpoint_and_credential(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test initialization creates client with correct endpoint and credential."""
        endpoint = "https://test-project.azure.com"
        mock_client_class.return_value = MagicMock()

        runtime = DefaultFoundryToolRuntime(
            project_endpoint=endpoint,
            credential=mock_credential
        )

        mock_client_class.assert_called_once_with(
            endpoint=endpoint,
            credential=mock_credential
        )
        assert runtime is not None

    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_init_uses_default_user_provider_when_none_provided(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test initialization uses ContextVarUserProvider when user_provider is None."""
        mock_client_class.return_value = MagicMock()

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        assert isinstance(runtime._user_provider, ContextVarUserProvider)

    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_init_uses_custom_user_provider(
        self,
        mock_client_class,
        mock_credential,
        mock_user_provider
    ):
        """Test initialization uses custom user provider when provided."""
        mock_client_class.return_value = MagicMock()

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential,
            user_provider=mock_user_provider
        )

        assert runtime._user_provider is mock_user_provider

    @patch.dict(os.environ, {"AGENT_NAME": "custom-agent"})
    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_init_reads_agent_name_from_environment(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test initialization reads agent name from environment variable."""
        mock_client_class.return_value = MagicMock()

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        assert runtime._agent_name == "custom-agent"

    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_init_uses_default_agent_name_when_env_not_set(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test initialization uses default agent name when env var is not set."""
        mock_client_class.return_value = MagicMock()

        # Ensure AGENT_NAME is not set
        env_copy = os.environ.copy()
        if "AGENT_NAME" in env_copy:
            del env_copy["AGENT_NAME"]

        with patch.dict(os.environ, env_copy, clear=True):
            runtime = DefaultFoundryToolRuntime(
                project_endpoint="https://test.azure.com",
                credential=mock_credential
            )

            assert runtime._agent_name == "$default"


class TestDefaultFoundryToolRuntimeCatalog:
    """Tests for DefaultFoundryToolRuntime.catalog property."""

    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_catalog_returns_default_catalog(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test catalog property returns DefaultFoundryToolCatalog."""
        mock_client_class.return_value = MagicMock()

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        assert isinstance(runtime.catalog, DefaultFoundryToolCatalog)


class TestDefaultFoundryToolRuntimeInvocation:
    """Tests for DefaultFoundryToolRuntime.invocation property."""

    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_invocation_returns_default_resolver(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test invocation property returns DefaultFoundryToolInvocationResolver."""
        mock_client_class.return_value = MagicMock()

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        assert isinstance(runtime.invocation, DefaultFoundryToolInvocationResolver)


class TestDefaultFoundryToolRuntimeInvoke:
    """Tests for DefaultFoundryToolRuntime.invoke method."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    async def test_invoke_resolves_and_invokes_tool(
        self,
        mock_client_class,
        mock_credential,
        sample_resolved_mcp_tool
    ):
        """Test invoke resolves the tool and calls the invoker."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        # Mock the invocation resolver
        mock_invoker = AsyncMock()
        mock_invoker.invoke = AsyncMock(return_value={"result": "success"})
        runtime._invocation.resolve = AsyncMock(return_value=mock_invoker)

        result = await runtime.invoke(sample_resolved_mcp_tool, {"input": "test"})

        assert result == {"result": "success"}
        runtime._invocation.resolve.assert_called_once_with(sample_resolved_mcp_tool)
        mock_invoker.invoke.assert_called_once_with({"input": "test"})

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    async def test_invoke_with_facade_dict(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test invoke works with facade dictionary."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        facade = {"type": "custom_tool", "config": "value"}

        # Mock the invocation resolver
        mock_invoker = AsyncMock()
        mock_invoker.invoke = AsyncMock(return_value={"output": "done"})
        runtime._invocation.resolve = AsyncMock(return_value=mock_invoker)

        result = await runtime.invoke(facade, {"param": "value"})

        assert result == {"output": "done"}
        runtime._invocation.resolve.assert_called_once_with(facade)


class TestDefaultFoundryToolRuntimeContextManager:
    """Tests for DefaultFoundryToolRuntime async context manager."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    async def test_aenter_returns_runtime_and_enters_client(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test __aenter__ enters client and returns runtime."""
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client_instance

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        async with runtime as r:
            assert r is runtime
            mock_client_instance.__aenter__.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    async def test_aexit_exits_client(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test __aexit__ exits client properly."""
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client_instance

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        async with runtime:
            pass

        mock_client_instance.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    async def test_aexit_called_on_exception(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test __aexit__ is called even when exception occurs."""
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client_instance

        runtime = DefaultFoundryToolRuntime(
            project_endpoint="https://test.azure.com",
            credential=mock_credential
        )

        with pytest.raises(ValueError):
            async with runtime:
                raise ValueError("Test error")

        mock_client_instance.__aexit__.assert_called_once()


class TestCreateToolRuntime:
    """Tests for create_tool_runtime factory function."""

    @patch("azure.ai.agentserver.core.tools.runtime._runtime.FoundryToolClient")
    def test_create_tool_runtime_returns_default_runtime_with_valid_params(
        self,
        mock_client_class,
        mock_credential
    ):
        """Test create_tool_runtime returns DefaultFoundryToolRuntime when both params are provided."""
        mock_client_class.return_value = MagicMock()
        endpoint = "https://test-project.azure.com"

        runtime = create_tool_runtime(project_endpoint=endpoint, credential=mock_credential)

        assert isinstance(runtime, DefaultFoundryToolRuntime)

    def test_create_tool_runtime_returns_throwing_runtime_when_endpoint_is_none(
        self,
        mock_credential
    ):
        """Test create_tool_runtime returns ThrowingFoundryToolRuntime when endpoint is None."""
        runtime = create_tool_runtime(project_endpoint=None, credential=mock_credential)

        assert isinstance(runtime, ThrowingFoundryToolRuntime)

    def test_create_tool_runtime_returns_throwing_runtime_when_credential_is_none(self):
        """Test create_tool_runtime returns ThrowingFoundryToolRuntime when credential is None."""
        runtime = create_tool_runtime(project_endpoint="https://test.azure.com", credential=None)

        assert isinstance(runtime, ThrowingFoundryToolRuntime)

    def test_create_tool_runtime_returns_throwing_runtime_when_both_are_none(self):
        """Test create_tool_runtime returns ThrowingFoundryToolRuntime when both params are None."""
        runtime = create_tool_runtime(project_endpoint=None, credential=None)

        assert isinstance(runtime, ThrowingFoundryToolRuntime)

    def test_create_tool_runtime_returns_throwing_runtime_when_endpoint_is_empty_string(
        self,
        mock_credential
    ):
        """Test create_tool_runtime returns ThrowingFoundryToolRuntime when endpoint is empty string."""
        runtime = create_tool_runtime(project_endpoint="", credential=mock_credential)

        assert isinstance(runtime, ThrowingFoundryToolRuntime)


class TestThrowingFoundryToolRuntime:
    """Tests for ThrowingFoundryToolRuntime."""

    def test_catalog_raises_runtime_error(self):
        """Test catalog property raises RuntimeError."""
        runtime = ThrowingFoundryToolRuntime()

        with pytest.raises(RuntimeError) as exc_info:
            _ = runtime.catalog

        assert "FoundryToolRuntime is not configured" in str(exc_info.value)
        assert "project endpoint and credential" in str(exc_info.value)

    def test_invocation_raises_runtime_error(self):
        """Test invocation property raises RuntimeError."""
        runtime = ThrowingFoundryToolRuntime()

        with pytest.raises(RuntimeError) as exc_info:
            _ = runtime.invocation

        assert "FoundryToolRuntime is not configured" in str(exc_info.value)
        assert "project endpoint and credential" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invoke_raises_runtime_error(self):
        """Test invoke method raises RuntimeError (via invocation property)."""
        runtime = ThrowingFoundryToolRuntime()

        with pytest.raises(RuntimeError) as exc_info:
            await runtime.invoke({"type": "test"}, {"arg": "value"})

        assert "FoundryToolRuntime is not configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        """Test __aenter__ returns the runtime instance."""
        runtime = ThrowingFoundryToolRuntime()

        async with runtime as r:
            assert r is runtime

    @pytest.mark.asyncio
    async def test_aexit_completes_successfully(self):
        """Test __aexit__ completes without error."""
        runtime = ThrowingFoundryToolRuntime()

        # Should not raise any exception
        async with runtime:
            pass

    @pytest.mark.asyncio
    async def test_context_manager_does_not_suppress_exceptions(self):
        """Test context manager does not suppress exceptions."""
        runtime = ThrowingFoundryToolRuntime()

        with pytest.raises(ValueError):
            async with runtime:
                raise ValueError("Test error")

    def test_error_message_is_class_variable(self):
        """Test _ERROR_MESSAGE is defined as a class variable."""
        assert hasattr(ThrowingFoundryToolRuntime, "_ERROR_MESSAGE")
        assert isinstance(ThrowingFoundryToolRuntime._ERROR_MESSAGE, str)


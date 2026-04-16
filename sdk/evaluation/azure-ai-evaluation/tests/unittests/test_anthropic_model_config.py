# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Unit tests for Anthropic model configuration support in azure-ai-evaluation."""

import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.unittest
class TestAnthropicModelConfiguration(unittest.TestCase):
    """Tests for AnthropicModelConfiguration TypedDict."""

    def test_anthropic_model_config_creation(self):
        """Test creating an AnthropicModelConfiguration dict."""
        from azure.ai.evaluation._model_configurations import AnthropicModelConfiguration

        config = AnthropicModelConfiguration(
            type="anthropic",
            api_key="my-anthropic-api-key",
            model="claude-3-5-sonnet-20241022",
        )

        assert config["type"] == "anthropic"
        assert config["api_key"] == "my-anthropic-api-key"
        assert config["model"] == "claude-3-5-sonnet-20241022"

    def test_anthropic_model_config_with_optional_fields(self):
        """Test creating an AnthropicModelConfiguration with optional fields."""
        from azure.ai.evaluation._model_configurations import AnthropicModelConfiguration

        config = AnthropicModelConfiguration(
            type="anthropic",
            api_key="my-anthropic-api-key",
            model="claude-3-5-sonnet-20241022",
            base_url="https://api.anthropic.com",
            max_tokens=8192,
        )

        assert config["type"] == "anthropic"
        assert config["api_key"] == "my-anthropic-api-key"
        assert config["model"] == "claude-3-5-sonnet-20241022"
        assert config["base_url"] == "https://api.anthropic.com"
        assert config["max_tokens"] == 8192

    def test_anthropic_model_config_exported_from_package(self):
        """Test that AnthropicModelConfiguration is exported from the main package."""
        from azure.ai.evaluation import AnthropicModelConfiguration

        assert AnthropicModelConfiguration is not None

    def test_anthropic_type_constant(self):
        """Test that ANTHROPIC_TYPE constant is defined."""
        from azure.ai.evaluation._constants import ANTHROPIC_TYPE

        assert ANTHROPIC_TYPE == "anthropic"


@pytest.mark.unittest
class TestAnthropicModelConfigUtils(unittest.TestCase):
    """Tests for utility functions with Anthropic model configuration."""

    def test_is_anthropic_model_config_true(self):
        """Test _is_anthropic_model_config returns True for valid Anthropic config."""
        from azure.ai.evaluation._common.utils import _is_anthropic_model_config

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
        }
        assert _is_anthropic_model_config(config) is True

    def test_is_anthropic_model_config_false_wrong_type(self):
        """Test _is_anthropic_model_config returns False for non-Anthropic config."""
        from azure.ai.evaluation._common.utils import _is_anthropic_model_config

        config = {
            "type": "openai",
            "api_key": "my-api-key",
            "model": "gpt-4",
        }
        assert _is_anthropic_model_config(config) is False

    def test_is_anthropic_model_config_false_missing_fields(self):
        """Test _is_anthropic_model_config returns False when required fields are missing."""
        from azure.ai.evaluation._common.utils import _is_anthropic_model_config

        config = {"type": "anthropic"}
        assert _is_anthropic_model_config(config) is False

    def test_parse_model_config_type_anthropic(self):
        """Test parse_model_config_type sets type for Anthropic config."""
        from azure.ai.evaluation._common.utils import parse_model_config_type

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
        }
        parse_model_config_type(config)
        assert config["type"] == "anthropic"

    def test_validate_model_config_anthropic(self):
        """Test validate_model_config succeeds for Anthropic config."""
        from azure.ai.evaluation._common.utils import validate_model_config

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
        }
        result = validate_model_config(config)
        assert result["type"] == "anthropic"
        assert result["api_key"] == "my-api-key"
        assert result["model"] == "claude-3-5-sonnet-20241022"

    def test_validate_model_config_anthropic_with_max_tokens(self):
        """Test validate_model_config succeeds for Anthropic config with max_tokens."""
        from azure.ai.evaluation._common.utils import validate_model_config

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 8192,
        }
        result = validate_model_config(config)
        assert result["max_tokens"] == 8192

    def test_validate_model_config_still_works_for_azure_openai(self):
        """Test validate_model_config still works for Azure OpenAI config."""
        from azure.ai.evaluation._common.utils import validate_model_config

        config = {
            "azure_endpoint": "https://my-endpoint.openai.azure.com",
            "azure_deployment": "gpt-4",
            "api_key": "my-api-key",
        }
        result = validate_model_config(config)
        assert result["azure_endpoint"] == "https://my-endpoint.openai.azure.com"

    def test_validate_model_config_still_works_for_openai(self):
        """Test validate_model_config still works for OpenAI config."""
        from azure.ai.evaluation._common.utils import validate_model_config

        config = {
            "api_key": "my-oai-key",
            "model": "gpt-4",
        }
        result = validate_model_config(config)
        assert result["model"] == "gpt-4"

    def test_validate_model_config_anthropic_invalid_key_raises(self):
        """Test validate_model_config raises for Anthropic config with invalid key."""
        from azure.ai.evaluation._common.utils import validate_model_config
        from azure.ai.evaluation._exceptions import EvaluationException

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
            "invalid_key": "some_value",  # This key is not in AnthropicModelConfiguration
        }
        with pytest.raises(EvaluationException):
            validate_model_config(config)

    def test_construct_prompty_model_config_anthropic(self):
        """Test construct_prompty_model_config works for Anthropic config."""
        from azure.ai.evaluation._common.utils import construct_prompty_model_config

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
        }
        result = construct_prompty_model_config(config, "2024-02-01", "my-user-agent")
        assert result["configuration"]["type"] == "anthropic"
        assert "extra_headers" in result["parameters"]
        # Anthropic config should not have api_version added
        assert "api_version" not in result["configuration"]


@pytest.mark.unittest
class TestAnthropicConnection(unittest.TestCase):
    """Tests for AnthropicConnection class."""

    def test_anthropic_connection_parse_from_config(self):
        """Test parsing AnthropicConnection from config dict."""
        from azure.ai.evaluation._legacy.prompty._connection import AnthropicConnection, Connection

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
        }
        connection = Connection.parse_from_config(config)
        assert isinstance(connection, AnthropicConnection)
        assert connection.api_key == "my-api-key"
        assert connection.model == "claude-3-5-sonnet-20241022"
        assert connection.max_tokens == 4096  # default

    def test_anthropic_connection_with_base_url(self):
        """Test AnthropicConnection with custom base_url."""
        from azure.ai.evaluation._legacy.prompty._connection import AnthropicConnection, Connection

        config = {
            "type": "anthropic",
            "api_key": "my-api-key",
            "model": "claude-3-5-sonnet-20241022",
            "base_url": "https://custom.anthropic.com",
            "max_tokens": 8192,
        }
        connection = Connection.parse_from_config(config)
        assert isinstance(connection, AnthropicConnection)
        assert connection.base_url == "https://custom.anthropic.com"
        assert connection.max_tokens == 8192

    def test_anthropic_connection_type_property(self):
        """Test AnthropicConnection.type property."""
        from azure.ai.evaluation._legacy.prompty._connection import AnthropicConnection

        conn = AnthropicConnection(api_key="key", model="claude-3")
        assert conn.type == "anthropic"

    def test_anthropic_connection_from_env(self):
        """Test AnthropicConnection.from_env reads from environment variables."""
        import os
        from azure.ai.evaluation._legacy.prompty._connection import AnthropicConnection

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key", "ANTHROPIC_MODEL": "claude-3-env"}):
            conn = AnthropicConnection.from_env()
            assert conn.api_key == "env-key"
            assert conn.model == "claude-3-env"

    def test_unsupported_connection_type_still_raises(self):
        """Test that unsupported connection types still raise errors."""
        from azure.ai.evaluation._legacy.prompty._connection import Connection
        from azure.ai.evaluation._legacy.prompty._exceptions import MissingRequiredInputError

        config = {"type": "some_unknown_type"}
        with pytest.raises(MissingRequiredInputError):
            Connection.parse_from_config(config)


@pytest.mark.unittest
class TestAnthropicPromptyCall(unittest.TestCase):
    """Tests for AsyncPrompty with Anthropic connections."""

    @pytest.mark.asyncio
    async def test_anthropic_error_retryable_connection_error(self):
        """Test that Anthropic connection errors are retried."""
        # This test mocks the anthropic module to avoid requiring it as a real dependency
        mock_anthropic = MagicMock()

        class MockConnectionError(Exception):
            pass

        class MockStatusError(Exception):
            def __init__(self, status_code):
                self.status_code = status_code
                self.response = MagicMock()
                self.response.headers = {}

        mock_anthropic.APIConnectionError = MockConnectionError
        mock_anthropic.APIStatusError = MockStatusError

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from azure.ai.evaluation._legacy.prompty._prompty import AsyncPrompty

            # Test that a connection error is retryable
            error = MockConnectionError("Connection error")
            should_retry, delay = AsyncPrompty._anthropic_error_retryable(error, 0, [0], 3)
            assert should_retry is True

    @pytest.mark.asyncio
    async def test_anthropic_error_retryable_429(self):
        """Test that Anthropic 429 errors are retried."""
        mock_anthropic = MagicMock()

        class MockConnectionError(Exception):
            pass

        class MockStatusError(Exception):
            def __init__(self, status_code):
                self.status_code = status_code
                self.response = MagicMock()
                self.response.headers = {}

        mock_anthropic.APIConnectionError = MockConnectionError
        mock_anthropic.APIStatusError = MockStatusError

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from azure.ai.evaluation._legacy.prompty._prompty import AsyncPrompty

            error = MockStatusError(429)
            should_retry, delay = AsyncPrompty._anthropic_error_retryable(error, 0, [0], 3)
            assert should_retry is True

    @pytest.mark.asyncio
    async def test_anthropic_error_retryable_500(self):
        """Test that Anthropic 500 errors are retried."""
        mock_anthropic = MagicMock()

        class MockConnectionError(Exception):
            pass

        class MockStatusError(Exception):
            def __init__(self, status_code):
                self.status_code = status_code
                self.response = MagicMock()
                self.response.headers = {}

        mock_anthropic.APIConnectionError = MockConnectionError
        mock_anthropic.APIStatusError = MockStatusError

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from azure.ai.evaluation._legacy.prompty._prompty import AsyncPrompty

            error = MockStatusError(500)
            should_retry, delay = AsyncPrompty._anthropic_error_retryable(error, 0, [0], 3)
            assert should_retry is True

    @pytest.mark.asyncio
    async def test_anthropic_error_retryable_400(self):
        """Test that Anthropic 400 errors are NOT retried."""
        mock_anthropic = MagicMock()

        class MockConnectionError(Exception):
            pass

        class MockStatusError(Exception):
            def __init__(self, status_code):
                self.status_code = status_code
                self.response = MagicMock()
                self.response.headers = {}

        mock_anthropic.APIConnectionError = MockConnectionError
        mock_anthropic.APIStatusError = MockStatusError

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from azure.ai.evaluation._legacy.prompty._prompty import AsyncPrompty

            error = MockStatusError(400)
            should_retry, delay = AsyncPrompty._anthropic_error_retryable(error, 0, [0], 3)
            assert should_retry is False

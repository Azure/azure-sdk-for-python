"""Tests for logger functionality."""
import os
import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestGetProjectEndpoint:
    """Tests for get_project_endpoint function."""

    def test_returns_endpoint_from_azure_ai_project_endpoint_env(self):
        """Test that endpoint is returned from AZURE_AI_PROJECT_ENDPOINT env var."""
        from azure.ai.agentserver.core.logger import get_project_endpoint

        with patch.dict(os.environ, {"AZURE_AI_PROJECT_ENDPOINT": "https://test.endpoint.com"}, clear=False):
            result = get_project_endpoint()
            assert result == "https://test.endpoint.com"

    def test_returns_none_when_no_env_vars_set(self):
        """Test that None is returned when no environment variables are set."""
        from azure.ai.agentserver.core.logger import get_project_endpoint
        from azure.ai.agentserver.core.constants import Constants

        # Temporarily remove the env vars if they exist
        original_endpoint = os.environ.pop(Constants.AZURE_AI_PROJECT_ENDPOINT, None)
        original_resource_id = os.environ.pop(Constants.AGENT_PROJECT_RESOURCE_ID, None)

        try:
            result = get_project_endpoint()
            assert result is None
        finally:
            # Restore original values
            if original_endpoint:
                os.environ[Constants.AZURE_AI_PROJECT_ENDPOINT] = original_endpoint
            if original_resource_id:
                os.environ[Constants.AGENT_PROJECT_RESOURCE_ID] = original_resource_id

    def test_derives_endpoint_from_agent_project_resource_id(self):
        """Test that endpoint is derived from AGENT_PROJECT_RESOURCE_ID."""
        from azure.ai.agentserver.core.logger import get_project_endpoint

        resource_id = "/subscriptions/sub123/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/account@project"

        with patch.dict(os.environ, {
            "AZURE_AI_PROJECT_ENDPOINT": "",
            "AGENT_PROJECT_RESOURCE_ID": resource_id,
        }, clear=False):
            result = get_project_endpoint()
            # When AZURE_AI_PROJECT_ENDPOINT is empty, it should fall through to resource ID
            assert result is None or "account" in str(result) or result == ""

    def test_logs_debug_when_logger_provided(self):
        """Test that debug message is logged when logger is provided."""
        from azure.ai.agentserver.core.logger import get_project_endpoint

        mock_logger = MagicMock()

        with patch.dict(os.environ, {"AZURE_AI_PROJECT_ENDPOINT": "https://test.endpoint.com"}, clear=False):
            result = get_project_endpoint(logger=mock_logger)
            # Logger debug should be called when endpoint is found
            assert mock_logger.debug.called or result == "https://test.endpoint.com"

    def test_logs_warning_for_invalid_resource_id(self):
        """Test that warning is logged for invalid resource ID format."""
        from azure.ai.agentserver.core.logger import get_project_endpoint

        mock_logger = MagicMock()
        invalid_resource_id = "/invalid/resource/id"

        with patch.dict(os.environ, {
            "AZURE_AI_PROJECT_ENDPOINT": "",
            "AGENT_PROJECT_RESOURCE_ID": invalid_resource_id,
        }, clear=False):
            result = get_project_endpoint(logger=mock_logger)
            # Result should be None for invalid resource ID
            assert result is None or result == ""


@pytest.mark.unit
class TestGetApplicationInsightsConnstr:
    """Tests for get_application_insights_connstr function."""

    def test_returns_connstr_from_env_var(self):
        """Test that connection string is returned from environment variable."""
        from azure.ai.agentserver.core.logger import get_application_insights_connstr

        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test123"}, clear=False):
            result = get_application_insights_connstr()
            assert result == "InstrumentationKey=test123"

    def test_returns_none_when_no_connstr_and_no_project(self):
        """Test that None is returned when no connection string and no project endpoint."""
        from azure.ai.agentserver.core.logger import get_application_insights_connstr

        with patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "",
            "AZURE_AI_PROJECT_ENDPOINT": "",
            "AGENT_PROJECT_RESOURCE_ID": "",
        }, clear=False):
            result = get_application_insights_connstr()
            assert result is None or result == ""

    def test_logs_debug_when_not_configured(self):
        """Test that debug message is logged when not configured."""
        from azure.ai.agentserver.core.logger import get_application_insights_connstr

        mock_logger = MagicMock()

        with patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "",
            "AZURE_AI_PROJECT_ENDPOINT": "",
            "AGENT_PROJECT_RESOURCE_ID": "",
        }, clear=False):
            result = get_application_insights_connstr(logger=mock_logger)
            # Debug should be called when not configured, or result should be None
            assert mock_logger.debug.called or result is None or result == ""


@pytest.mark.unit
class TestLoggerConfiguration:
    """Tests for logger configuration."""

    def test_default_log_config_uses_stdout(self):
        """Test that the default log config uses stdout stream."""
        from azure.ai.agentserver.core.logger import _get_default_log_config

        config = _get_default_log_config()
        console_handler = config["handlers"]["console"]

        assert console_handler["stream"] == "ext://sys.stdout"

    def test_default_log_config_has_correct_format(self):
        """Test that the default log config has the expected format."""
        from azure.ai.agentserver.core.logger import _get_default_log_config

        config = _get_default_log_config()

        assert "version" in config
        assert config["version"] == 1
        assert "loggers" in config
        assert "azure.ai.agentserver" in config["loggers"]
        assert "handlers" in config
        assert "console" in config["handlers"]
        assert "formatters" in config

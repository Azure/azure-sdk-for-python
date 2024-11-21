# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.ai.projects.telemetry.agents._ai_agents_instrumentor import _AIAgentsInstrumentorPreview
from azure.ai.projects.models import AgentsApiResponseFormatMode, AgentsApiResponseFormat


class TestAiAgentsInstrumentor:
    """Tests for AI agents instrumentor."""

    def test_convert_api_response_format_exception(self):
        """Test that the exception is raised if agent_api_response_to_str is given wrong type."""
        with pytest.raises(ValueError) as cm:
            _AIAgentsInstrumentorPreview.agent_api_response_to_str(42)
        assert "Unknown response format <class 'int'>" in cm.value.args[0]

    @pytest.mark.parametrize(
        "fmt,expected",
        [
            (None, None),
            ("neep", "neep"),
            (AgentsApiResponseFormatMode.AUTO, "auto"),
            (AgentsApiResponseFormat(type="test"), "test"),
        ],
    )
    def test_convert_api_response_format(self, fmt, expected):
        """Test conversion of AgentsApiResponseFormatOption to string"""
        actual = _AIAgentsInstrumentorPreview.agent_api_response_to_str(fmt)
        assert actual == expected

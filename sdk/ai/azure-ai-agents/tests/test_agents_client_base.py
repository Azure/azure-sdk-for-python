import sys
import logging
import functools
import json
import datetime
from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)
from devtools_testutils.azure_testcase import is_live
from azure.ai.agents.models import RunStepBrowserAutomationToolCall

agentClientPreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_agents",
    # TODO: uncomment this endpoint when re running with 1DP
    # azure_ai_agents_tests_project_endpoint="https://aiservices-id.services.ai.azure.com/api/projects/project-name",
    # TODO: remove this endpoint when re running with 1DP
    azure_ai_agents_tests_project_connection_string="https://Sanitized.api.azureml.ms/agents/v1.0/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/",
    azure_ai_agents_tests_project_endpoint="https://Sanitized.services.ai.azure.com/api/projects/00000",
    azure_ai_agents_tests_data_path="azureml://subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rg-resour-cegr-oupfoo1/workspaces/abcd-abcdabcdabcda-abcdefghijklm/datastores/workspaceblobstore/paths/LocalUpload/000000000000/product_info_1.md",
    azure_ai_agents_tests_storage_queue="https://foobar.queue.core.windows.net",
    azure_ai_agents_tests_search_index_name="sample_index",
    azure_ai_agents_tests_search_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.MachineLearningServices/workspaces/00000/connections/someindex",
    azure_ai_agents_tests_bing_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.CognitiveServices/accounts/00000/projects/00000/connections/00000",
    azure_ai_agents_tests_playwright_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.CognitiveServices/accounts/00000/projects/00000/connections/00000",
    azure_ai_agents_tests_deep_research_model="gpt-4o-deep-research",
    azure_ai_agents_tests_is_test_run="True",
)

# Set to True to enable SDK logging
LOGGING_ENABLED = True

if LOGGING_ENABLED:
    # Create a logger for the 'azure' SDK
    # See https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)  # INFO or DEBUG

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)


def fetch_current_datetime_live():
    """
    Get the current time as a JSON string.

    :return: Static time string so that test recordings work.
    :rtype: str
    """
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_json = json.dumps({"current_time": current_datetime})
    return time_json


def fetch_current_datetime_recordings():
    """
    Get the current time as a JSON string.

    :return: Static time string so that test recordings work.
    :rtype: str
    """
    time_json = json.dumps({"current_time": "2024-10-10 12:30:19"})
    return time_json


class TestAgentClientBase(AzureRecordedTestCase):
    """Base class for Agents Client tests. Please put all code common to sync and async tests here."""

    @classmethod
    def _sleep_time(cls, sleep: int = 1) -> int:
        """Return sleep or zero if we are running the recording."""
        return sleep if is_live() else 0

    @classmethod
    def _validate_run_step_browser_automation_tool_call(cls, tool_call: RunStepBrowserAutomationToolCall):
        assert tool_call.browser_automation.input
        assert tool_call.browser_automation.output
        assert len(tool_call.browser_automation.steps) > 1
        assert tool_call.browser_automation.steps[0].last_step_result
        assert tool_call.browser_automation.steps[0].current_state
        assert tool_call.browser_automation.steps[0].next_step
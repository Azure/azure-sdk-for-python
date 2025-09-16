# pylint: disable=line-too-long,useless-suppression
import sys
import logging
import functools
import json
import datetime
import os
import base64
from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
)
from devtools_testutils.azure_testcase import is_live
from azure.ai.agents.models import (
    MessageTextFileCitationDetails,
    MessageTextUrlCitationDetails,
    RunStepBrowserAutomationToolCall,
    ThreadMessage,
)

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
    azure_ai_agents_tests_bing_custom_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.CognitiveServices/accounts/00000/projects/00000/connections/00000",
    azure_ai_agents_tests_bing_configuration_name="sample_configuration",
    azure_ai_agents_tests_fabric_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.CognitiveServices/accounts/00000/projects/00000/connections/00000",
    azure_ai_agents_tests_sharepoint_connection_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/00000/providers/Microsoft.CognitiveServices/accounts/00000/projects/00000/connections/00000",
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


def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to a Base64-encoded string.

    :param image_path: The path to the image file (e.g. 'image_file.png')
    :return: A Base64-encoded string representing the image.
    :raises FileNotFoundError: If the provided file path does not exist.
    :raises OSError: If there's an error reading the file.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found at: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            file_data = image_file.read()
        return base64.b64encode(file_data).decode("utf-8")
    except Exception as exc:
        raise OSError(f"Error reading file '{image_path}'") from exc


class TestAgentClientBase(AzureRecordedTestCase):
    """Base class for Agents Client tests. Please put all code common to sync and async tests here."""

    @classmethod
    def _sleep_time(cls, sleep: int = 1) -> int:
        """Return sleep or zero if we are running the recording."""
        return sleep if is_live() else 0

    @classmethod
    def _has_url_annotation(cls, message: ThreadMessage, uri_annotation: MessageTextUrlCitationDetails) -> bool:
        """
        Return True if the message contains required URL annotation.

        :param message: The message to look for annotations.
        :param uri_annotation: The annotation to look for.
        :return:  True if the message contains the required URL annotation.
        :rtype: bool
        """
        url_annotations = message.url_citation_annotations
        if url_annotations:
            for url in url_annotations:
                if (
                    (uri_annotation.url == "*" and url.url_citation.url) or url.url_citation.url == uri_annotation.url
                ) and (
                    (uri_annotation.title == "*" and url.url_citation.title)
                    or url.url_citation.title == uri_annotation.title
                ):
                    return True
        return False

    @classmethod
    def _has_file_annotation(cls, message: ThreadMessage, file_annotation: MessageTextFileCitationDetails) -> bool:
        """
        Return True if the message contains required file annotation

        :param message: The message to look for annotations.
        :param file_annotation: The annotation to look for.
        :return: True if the message contains the required file annotation, otherwise False.
        :rtype: bool
        """
        file_annotations = message.file_citation_annotations
        if file_annotations:
            for fle in file_annotations:
                if fle.file_citation:
                    if fle.file_citation.file_id == file_annotation.file_citation.file_id:
                        return True
        return False

    @classmethod
    def _validate_run_step_browser_automation_tool_call(cls, tool_call: RunStepBrowserAutomationToolCall):
        assert tool_call.browser_automation.input
        assert tool_call.browser_automation.output
        assert len(tool_call.browser_automation.steps) > 1
        assert tool_call.browser_automation.steps[0].last_step_result
        assert tool_call.browser_automation.steps[0].current_state
        assert tool_call.browser_automation.steps[0].next_step

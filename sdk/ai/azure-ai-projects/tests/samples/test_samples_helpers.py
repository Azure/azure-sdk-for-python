# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""
from typing import Optional


agent_tools_instructions = """We just run Python code and captured a Python array of print statements.
Validating the printed content to determine if correct or not:
Respond false if any entries show:
- Error messages or exception text
- Empty or null results where data is expected
- Malformed or corrupted data
- Timeout or connection errors
- Warning messages indicating failures
- Failure to retrieve or process data
- Statements saying documents/information didn't provide relevant data
- Statements saying unable to find/retrieve information
- Asking the user to specify, clarify, or provide more details
- Suggesting to use other tools or sources
- Asking follow-up questions to complete the task
- Indicating lack of knowledge or missing information
- Responses that defer answering or redirect the question
Respond with true only if the result provides a complete, substantive answer with actual data/information.
Always respond with `reason` indicating the reason for the response."""


def get_sample_environment_variables_map(operation_group: Optional[str] = None) -> dict[str, str]:
    """Get the mapping of sample environment variables to test environment variables.

    Args:
        operation_group: Optional operation group name (e.g., "agents") to scope the endpoint variable.

    Returns:
        Dictionary mapping sample env var names to test env var names.
    """
    return {
        "AZURE_AI_PROJECT_ENDPOINT": (
            "azure_ai_projects_tests_project_endpoint"
            if operation_group is None
            else f"azure_ai_projects_tests_{operation_group}_project_endpoint"
        ),
        "AZURE_AI_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_model_deployment_name",
        "IMAGE_GENERATION_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_image_generation_model_deployment_name",
        "AI_SEARCH_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_ai_search_project_connection_id",
        "AI_SEARCH_INDEX_NAME": "azure_ai_projects_tests_ai_search_index_name",
        "AI_SEARCH_USER_INPUT": "azure_ai_projects_tests_ai_search_user_input",
        "SHAREPOINT_USER_INPUT": "azure_ai_projects_tests_sharepoint_user_input",
        "SHAREPOINT_PROJECT_CONNECTION_ID": "azure_ai_projects_tests_sharepoint_project_connection_id",
        "MEMORY_STORE_CHAT_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_memory_store_chat_model_deployment_name",
        "MEMORY_STORE_EMBEDDING_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_memory_store_embedding_model_deployment_name",
    }

# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""
from typing import Optional, Mapping, Any


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


def get_sample_environment_variables_map(env_kwargs: Mapping[str, Any]) -> dict[str, str]:
    # Map sample env-var names (uppercase) to the original kwargs key names so executors can pop them.
    mapping: dict[str, str] = {}
    for key in env_kwargs.keys():
        if isinstance(key, str):
            mapping[key.upper()] = key
    return mapping

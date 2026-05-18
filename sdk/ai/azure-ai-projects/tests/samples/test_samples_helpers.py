# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""

from typing import Mapping, Any
from llm_instructions import (
    agent_tools_instructions,
    agents_instructions,
    chat_completions_instructions,
    memories_instructions,
    resource_management_instructions,
)


def get_sample_env_vars(env_kwargs: Mapping[str, Any]) -> dict[str, str]:
    # Map sample env-var names (uppercase) to string values only.
    # Non-string values are filtered out to maintain type safety.
    mapping: dict[str, str] = {}
    for key, value in env_kwargs.items():
        if isinstance(key, str) and isinstance(value, str):
            mapping[key.upper()] = value
    return mapping

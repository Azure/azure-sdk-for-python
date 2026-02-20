# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared base code for sample tests - sync dependencies only."""
from typing import Optional, Mapping, Any


agent_tools_instructions = """We just ran Python code and captured a Python array of print statements.
Validate whether sample execution/output is correct for a tool-driven assistant workflow.

Prefer matched/substantive data in the final output when available.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Timeout/auth/connection/service errors that prevent normal completion.
- Malformed/corrupted output indicating broken processing.
- Tool invocation failures where the sample cannot proceed as designed.

Follow-up questions are allowed, but only as supplementary behavior.
If the output mainly asks follow-up questions without providing matched/substantive data, mark false.

Important distinction:
- Empty tool payloads by themselves (for example `[]` or `""`) can be valid and should not automatically fail.
- But if the assistant explicitly states tool failure/inability (for example "unable to retrieve ..."),
    treat that as a failure signal and mark `correct = false`.

Mark `correct = true` when execution succeeds and the output includes matched/substantive data,
even if it also asks follow-up questions.

Always include `reason` with a concise explanation tied to the observed print output."""


def get_sample_environment_variables_map(env_kwargs: Mapping[str, Any]) -> dict[str, str]:
    # Map sample env-var names (uppercase) to the original kwargs key names so executors can pop them.
    mapping: dict[str, str] = {}
    for key in env_kwargs.keys():
        if isinstance(key, str):
            mapping[key.upper()] = key
    return mapping

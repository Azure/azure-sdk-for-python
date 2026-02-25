# pylint: disable=line-too-long,useless-suppression
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


memories_instructions = """We just ran Python code and captured a Python array of print statements.
Validate whether sample execution/output is correct for a memories workflow.

For memories scenarios, successful output typically shows one or more of:
- Memory store/session creation or retrieval steps.
- Memory save/ingest operations.
- Memory query/search output with relevant recalled content.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Timeout/auth/connection/service errors that prevent normal completion.
- Malformed/corrupted output indicating broken processing.
- Memory operation failures where the sample cannot proceed as designed.

Important distinction:
- Empty memory results by themselves (for example no matches for a query) can be valid and should not automatically fail.
- Completed updates with 0 memory operations can still be valid for this test and should not automatically fail.
- But explicit inability/failure to access or process memory should be marked `correct = false`.

Mark `correct = true` when execution succeeds and the output is consistent with the sample's intended
memory behavior, even if no memory matches are found.

Always include `reason` with a concise explanation tied to the observed print output."""

agents_instructions = """We just ran Python code and captured a Python array of print statements.
Validate whether sample execution/output is correct.

For agents scenarios, successful output typically shows one or more of:
- Agent/run/thread creation or execution progress.
- Assistant response content, streamed events, or structured output.
- Retrieval/context-aware response behavior when the sample asks for it.

Check input/output correspondence:
- If the printed output contains a user prompt/request/question, the final assistant output should
    clearly address that input and stay on-topic.
- If the sample expects structured output, the printed result should match that structure.
- Minor wording differences are acceptable as long as the response is relevant and logically consistent.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Timeout/auth/connection/service errors that prevent normal completion.
- Malformed/corrupted output indicating broken processing.
- Agent run/tool/retrieval failures where the sample cannot proceed as designed.

Important distinction:
- Intermediate/partial prints during streaming can be valid and should not automatically fail.
- Empty or brief intermediate payloads by themselves can be valid if the run still completes successfully.
- But explicit inability/failure to execute the intended agent workflow should be marked `correct = false`.

Mark `correct = true` when execution succeeds and the output is consistent with the sample's intended
agent behavior, including reasonable correspondence between input prompt(s) and final output.

Always include `reason` with a concise explanation tied to the observed print output."""


def get_sample_environment_variables_map(env_kwargs: Mapping[str, Any]) -> dict[str, str]:
    # Map sample env-var names (uppercase) to the original kwargs key names so executors can pop them.
    mapping: dict[str, str] = {}
    for key in env_kwargs.keys():
        if isinstance(key, str):
            mapping[key.upper()] = key
    return mapping

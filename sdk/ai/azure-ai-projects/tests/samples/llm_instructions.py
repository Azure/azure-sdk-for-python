# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Centralized LLM validation instructions for sample execution.

This module is the single source of truth for:
- instruction strings used by sample validation
- mapping from sample folder -> instructions

The mapper is consumed by `sample_executor.py` to ensure all validation
uses consistent instructions based on sample path.
"""

from __future__ import annotations

from typing import Final

agent_tools_instructions: Final[str] = (
    """
We just ran Python code and captured print/log output in an attached log file (TXT).
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

Always include `reason` with a concise explanation tied to the observed print output.
""".strip()
)


memories_instructions: Final[str] = (
    """
We just ran Python code and captured print/log output in an attached log file (TXT).
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

Always include `reason` with a concise explanation tied to the observed print output.
""".strip()
)


agents_instructions: Final[str] = (
    """
We just ran Python code and captured print/log output in an attached log file (TXT).
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

Always include `reason` with a concise explanation tied to the observed print output.
""".strip()
)


chat_completions_instructions: Final[str] = (
    """
We just ran Python code and captured print/log output in an attached log file (TXT).
Validate whether sample execution/output is correct for Chat Completions scenarios.

Successful output typically shows one or more of:
- A user prompt and a corresponding assistant response.
- Reasonable, on-topic completion content.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Timeout/auth/connection/service errors that prevent normal completion.
- Malformed/corrupted output indicating broken processing.
- Output that clearly does not answer the prompt in the sample.

Mark `correct = true` when execution succeeds and the assistant output is coherent and
responds to the printed prompt, even if the exact wording varies.

Always include `reason` with a concise explanation tied to the observed print output.
""".strip()
)


resource_management_instructions: Final[str] = (
    """
We just ran Python code and captured print/log output in an attached log file (TXT).
Validate whether sample execution/output is correct for resource-management samples (for example
connections, files, and deployments).

Successful output typically shows one or more of:
- Create/get/list/update/delete operations completing as expected.
- Returned resource objects/IDs/names/versions or other meaningful operation results.
- Consistent progress from setup to cleanup where applicable.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Timeout/auth/connection/service errors that prevent normal completion.
- Malformed/corrupted output indicating broken processing.
- Operation failures where the sample cannot proceed as designed.

Important distinction:
- Empty list results by themselves can be valid and should not automatically fail.
- Cleanup/delete operations that report not found may still be acceptable if the sample otherwise succeeds.
- But explicit inability/failure for required core operations should be marked `correct = false`.

Mark `correct = true` when execution succeeds and output is consistent with the sample's intended
resource-management behavior.

Always include `reason` with a concise explanation tied to the observed print output.
""".strip()
)


fine_tuning_instructions: Final[str] = (
    """
We just ran Python code and captured print/log output in an attached log file (TXT).
Validate whether sample execution/output is correct for a fine-tuning workflow.

Successful output typically shows one or more of:
- Training/validation files prepared or uploaded successfully.
- Fine-tuning job creation with a returned job id/name.
- Job details/status output that indicates the request was accepted and processed.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Authentication/authorization/service errors that block job creation.
- File upload/read failures for required training/validation data.
- Fine-tuning job creation failures or malformed output that indicates broken processing.

Important distinction:
- Intermediate/transitional job states (for example queued/running) are valid and should not fail by themselves.
- The output does not need to show completed training unless the sample is explicitly designed to wait for completion.

Mark `correct = true` when execution succeeds and output is consistent with initiating/inspecting
the intended fine-tuning workflow.

Always include `reason` with a concise explanation tied to the observed print output.
""".strip()
)


evaluations_instructions: Final[str] = (
    """
We just ran Python code for an evaluation sample and captured print/log output in an attached log file (TXT).
Your job: determine if the sample code executed to completion WITHOUT throwing an unhandled exception.

Respond TRUE (correct=true) if:
- The output shows the evaluation was created and produced results (any results, including zeros)
- The sample ran to completion (no unhandled Python exceptions/tracebacks)
- Evaluation metric JSON with fields like "failed": 0, "error": null, "not_applicable": 0 is NORMAL
  successful output — these are counters, NOT errors
- Status messages like "in_progress", "Waiting for eval run" are normal polling behavior
- HTTP debug headers (x-stainless-read-timeout, x-ms-client-request-id, etc.) are normal and irrelevant
- "deleted": true/false in cleanup output is normal
- The absence of explicit "success" text is fine — no crash means success

Respond FALSE (correct=false) ONLY if:
- There is an actual Python traceback or unhandled exception
- There is an explicit error message like "Evaluation run failed" or "FAILED_EXECUTION"
- There is an actual timeout error or connection failure (NOT an HTTP header containing "timeout")
- The output shows corrupted or malformed data that prevented completion

Always respond with `reason` indicating the reason for the response.
""".strip()
)


hosted_agents_instructions: Final[str] = (
    """
We just ran Python code for a hosted-agent sample and captured print/log output in an attached log file (TXT).
Validate whether the sample executed correctly.

Successful output typically shows one or more of:
- Agent version/session/endpoint operations completing as expected.
- Skills/toolboxes/session-files operations succeeding.
- Responses output that is coherent and on-topic.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Timeout/auth/connection/service errors that prevent normal completion.
- Operation failures where the sample cannot proceed as designed.

Important distinction:
- Empty list outputs by themselves can be valid and should not automatically fail.
- Intermediate progress logs are valid if execution still completes.

Mark `correct = true` when execution succeeds and output is consistent with the sample's intended hosted-agent workflow.

Always include `reason` with a concise explanation tied to the observed print output.
""".strip()
)


# Folder (under samples/) -> instructions.
# Keys intentionally mirror the folder names used by sample test discovery.
# Use the most specific key possible (e.g. "agents/tools" should win over "agents").
INSTRUCTIONS_BY_FOLDER: Final[dict[str, str]] = {
    "agents/tools": agent_tools_instructions,
    "agents": agents_instructions,
    "hosted_agents": hosted_agents_instructions,
    "memories": memories_instructions,
    "connections": resource_management_instructions,
    "files": resource_management_instructions,
    "deployments": resource_management_instructions,
    "datasets": resource_management_instructions,
    "chat_completions": chat_completions_instructions,
    "finetuning": fine_tuning_instructions,
    "evaluations/agentic_evaluators": evaluations_instructions,
    "evaluations": evaluations_instructions,
}


def get_instructions_for_sample_path(sample_path: str) -> str:
    """Return the appropriate instruction string for a given sample path.

    The sample path may be absolute or relative and may use either '\\' or '/'.
    Matching is done against the path segment under the `samples/` directory.

    Falls back to resource_management_instructions when no folder match is found.
    """

    normalized = str(sample_path).replace("\\", "/")

    # Find the portion after /samples/
    marker = "/samples/"
    relative = normalized
    if marker in normalized:
        relative = normalized.split(marker, 1)[1]

    # Reduce to folder prefix (everything except filename)
    folder = "/".join([p for p in relative.split("/") if p][:-1])

    # Longest-prefix match on INSTRUCTIONS_BY_FOLDER keys.
    for key in sorted(INSTRUCTIONS_BY_FOLDER.keys(), key=len, reverse=True):
        if folder == key or folder.startswith(f"{key}/"):
            return INSTRUCTIONS_BY_FOLDER[key]

    return resource_management_instructions

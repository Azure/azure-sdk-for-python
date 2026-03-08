# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility to convert structured workflow trace JSON into LLM-readable text."""

import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

_WARN_PARSE_FAILED = "parse_failed: trace parsing failed, evaluation quality may be reduced"
_WARN_TRUNCATED = "truncated: some messages were truncated, evaluation quality may be reduced"
_SEPARATOR = "-" * 40

# Role label mapping
_ROLE_LABELS = {"user": "[User]", "assistant": "[Response]", "tool": ""}


def format_workflow_trace_for_eval(data: Dict) -> str:
    """Convert converter output dict into a human-readable text block for the LLM.

    Logs quality warnings directly rather than returning them.

    :param data: The converter output dict.
    :return: The formatted text.
    """
    if data.get("parse_failed"):
        logger.warning(_WARN_PARSE_FAILED)
        return _format_parse_failed(data)

    sections: List[str] = []
    has_truncation = False

    sections.append(_format_workflow_definition(data))

    user_query = _extract_user_query(data.get("invocations", []))
    if user_query:
        sections.append(f"[User Input]\n{user_query}")

    seen_sys_prompts: Dict[str, bool] = {}
    previous_output_texts: Set[str] = set()
    for inv in data.get("invocations", []):
        text, trunc, current_output_texts = _format_invocation(
            inv,
            seen_sys_prompts,
            previous_output_texts=previous_output_texts,
        )
        sections.append(text)
        previous_output_texts = previous_output_texts | current_output_texts
        if trunc:
            has_truncation = True

    sections.append(_format_completion(data.get("errors", [])))

    if has_truncation:
        logger.warning(_WARN_TRUNCATED)

    return ("\n\n" + _SEPARATOR + "\n\n").join(sections)


# ---------------------------------------------------------------------------
# Shared message formatting
# ---------------------------------------------------------------------------


def _format_parts(parts: List[Dict], indent: str = "  ") -> List[str]:
    """Format a message's parts into labeled lines. Handles text, tool_call, and tool_call_response."""
    lines = []
    for p in parts:
        ptype = p.get("type", "")
        if ptype == "text":
            content = p.get("content", "")
            if content:
                lines.append(f"{indent}{content}")
        elif ptype == "tool_call":
            name = p.get("name", "?")
            args = p.get("arguments", "")
            lines.append(f"{indent}[Tool Call] {name}({args})")
        elif ptype == "tool_call_response":
            resp = str(p.get("response", ""))[:1000]
            lines.append(f"{indent}[Tool Result] {resp}")
    return lines


def _format_messages(messages: List[Dict], indent: str = "  ", skip_system: bool = False) -> List[str]:
    """Format a list of messages with role labels and part formatting."""
    lines = []
    for msg in messages:
        role = msg.get("role", "")
        if skip_system and role == "system":
            continue
        parts = msg.get("parts", [])
        formatted = _format_parts(parts, indent)
        if not formatted:
            continue
        # Only show role label for text-bearing messages; skip for pure tool_call/tool_call_response
        has_text = any(p.get("type") == "text" for p in parts)
        if has_text:
            label = _ROLE_LABELS.get(role, f"[{role}]")
            if label:
                lines.append(f"{indent}{label}")
        lines.extend(formatted)
    return lines


def _normalize_text_for_dedup(content: str) -> str:
    return " ".join(str(content).split()).strip().lower()


def _normalize_tool_call_for_dedup(part: Dict) -> str:
    name = part.get("name", "")
    args = part.get("arguments", "")
    return _normalize_text_for_dedup(f"tool_call:{name}({args})")


def _normalize_tool_call_response_for_dedup(part: Dict) -> str:
    resp = str(part.get("response", ""))[:1000]
    return _normalize_text_for_dedup(f"tool_result:{resp}")


def _extract_normalized_output_parts(messages: List[Dict]) -> Set[str]:
    """Extract normalized representations of all output parts (text, tool_call, tool_call_response)."""
    normalized: Set[str] = set()
    for msg in messages:
        for part in msg.get("parts", []):
            ptype = part.get("type", "")
            if ptype == "text":
                value = _normalize_text_for_dedup(part.get("content", ""))
                if value:
                    normalized.add(value)
            elif ptype == "tool_call":
                value = _normalize_tool_call_for_dedup(part)
                if value:
                    normalized.add(value)
            elif ptype == "tool_call_response":
                value = _normalize_tool_call_response_for_dedup(part)
                if value:
                    normalized.add(value)
    return normalized


def _filter_messages_by_previous_output(
    messages: List[Dict], previous_output_texts: Set[str]
) -> Tuple[List[Dict], bool]:
    if not previous_output_texts:
        return messages, False

    filtered_messages: List[Dict] = []
    removed_any = False
    for msg in messages:
        role = msg.get("role", "")
        parts = msg.get("parts", [])
        filtered_parts = []
        for part in parts:
            ptype = part.get("type", "")
            normalized = None
            if ptype == "text" and role == "assistant":
                normalized = _normalize_text_for_dedup(part.get("content", ""))
            elif ptype == "tool_call":
                normalized = _normalize_tool_call_for_dedup(part)
            elif ptype == "tool_call_response":
                normalized = _normalize_tool_call_response_for_dedup(part)

            if normalized and normalized in previous_output_texts:
                removed_any = True
                continue
            filtered_parts.append(part)

        if filtered_parts:
            filtered_msg = dict(msg)
            filtered_msg["parts"] = filtered_parts
            filtered_messages.append(filtered_msg)
    return filtered_messages, removed_any


# ---------------------------------------------------------------------------
# Section formatters
# ---------------------------------------------------------------------------


def _format_parse_failed(data: Dict) -> str:
    lines = ["[PARSE FAILED - Raw Traces]"]
    for entry in data.get("raw_traces", []):
        target = entry.get("target", "")
        dims = entry.get("custom_dimensions", {})
        lines.append(f"  target: {target}")
        for k, v in dims.items():
            lines.append(f"    {k}: {str(v)[:500]}")
        lines.append("")
    return "\n".join(lines)


def _format_workflow_definition(data: Dict) -> str:
    topo = data.get("topology", {})
    executors: Dict[str, str] = {}
    for executor in topo.get("executors", []):
        if not isinstance(executor, dict):
            continue
        executor_id = executor.get("id")
        if not executor_id:
            continue
        executors[str(executor_id)] = str(executor.get("type", ""))

    lines = ["[Workflow Definition]"]
    if executors:
        lines.append("Executors: " + ", ".join(f"{eid} ({etype})" for eid, etype in executors.items()))
    edges = topo.get("edges", [])
    if edges:
        lines.append("Edges:")
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            lines.append(f"  {edge.get('source', '?')} -> {edge.get('target', '?')}")
    return "\n".join(lines)


def _extract_user_query(invocations: List[Dict]) -> str:
    if not invocations:
        return ""
    msgs = invocations[0].get("input_messages", {})
    if msgs.get("_truncated") and not msgs.get("value"):
        return msgs.get("_raw", "")[:2000]
    for msg in msgs.get("value", []):
        if msg.get("role") == "user":
            parts = msg.get("parts", [])
            texts = [p.get("content", "") for p in parts if p.get("type") == "text"]
            return " ".join(texts)
    return ""


def _format_invocation(
    inv: Dict,
    seen_sys_prompts: Dict[str, bool],
    *,
    previous_output_texts: Set[str],
) -> Tuple[str, bool, Set[str]]:
    agent = inv.get("agent_name", "Unknown")
    seq = inv.get("sequence", "?")
    had_truncation = False
    current_output_texts: Set[str] = set()

    lines = [f"[{agent} - Invocation {seq}]"]

    # System Prompt (deduplicate per agent)
    if agent not in seen_sys_prompts:
        sys_instr = inv.get("system_instructions", [])
        if sys_instr:
            lines.append("  [System Prompt]")
            lines.append(f"  {sys_instr[0][:2000]}")
        seen_sys_prompts[agent] = True
    else:
        lines.append("  [System Prompt: same as above]")

    # Conversation History (input messages)
    in_msgs = inv.get("input_messages", {})
    if in_msgs.get("_truncated") and not in_msgs.get("value"):
        lines.append("  [Conversation History] [TRUNCATED]")
        lines.append(f"  {in_msgs.get('_raw', '')[:4000]}")
        had_truncation = True
    else:
        input_value = in_msgs.get("value", [])
        removed_duplicate_assistant_text = False
        input_value, removed_duplicate_assistant_text = _filter_messages_by_previous_output(
            input_value, previous_output_texts
        )
        conv = _format_messages(input_value, skip_system=True)
        if conv:
            if removed_duplicate_assistant_text:
                lines.append("  [Conversation History: prior-agent context included]")
            else:
                lines.append("  [Conversation History]")
            lines.extend(conv)

    # Agent Response (output messages)
    lines.append(f"  {_SEPARATOR}")
    out_msgs = inv.get("output_messages", {})
    if out_msgs.get("_truncated") and not out_msgs.get("value"):
        lines.append(f"  [{agent} Response] [TRUNCATED]")
        lines.append(f"  {out_msgs.get('_raw', '')[:4000]}")
        had_truncation = True
    else:
        current_output_texts = _extract_normalized_output_parts(out_msgs.get("value", []))
        tool_lines = []
        output_lines = []
        for msg in out_msgs.get("value", []):
            for part in msg.get("parts", []):
                ptype = part.get("type", "")
                if ptype == "tool_call":
                    name = part.get("name", "?")
                    args = part.get("arguments", "")
                    tool_lines.append(f"  [Tool Call] {name}({args})")
                elif ptype == "tool_call_response":
                    resp = str(part.get("response", ""))[:1000]
                    tool_lines.append(f"  [Tool Result] {resp}")
                elif ptype == "text":
                    content = part.get("content", "")
                    if content:
                        output_lines.append(f"  {content}")
        if tool_lines or output_lines:
            lines.append(f"  [{agent} Response]")
            lines.extend(tool_lines)
            if output_lines:
                lines.append("  [Agent Output]")
                lines.extend(output_lines)

    return "\n".join(lines), had_truncation, current_output_texts


def _format_completion(errors: List[Dict]) -> str:
    if not errors:
        return "[Workflow Completion]\nSuccessful"
    lines = ["[Workflow Completion]"]
    for err in errors:
        lines.append(f"Error: {err.get('message', 'Unknown error')}")
    return "\n".join(lines)

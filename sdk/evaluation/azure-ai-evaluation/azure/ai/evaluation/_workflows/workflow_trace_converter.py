# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Workflow trace converter for multi-agent system traces.

Converts raw trace spans (from JSONL files or App Insights query results)
into a structured document suitable for LLM-based workflow evaluation.

Supports 6 workflow patterns: sequential, concurrent, magentic, group_chat,
handoff, and workflow_dag.

Usage:
    from workflow_trace_converter import convert_workflow_traces
    import json

    spans = []
    with open("trace.jsonl") as f:
        for line in f:
            spans.append(json.loads(line))
    result = convert_workflow_traces(spans)
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# App Insights truncation threshold (8KB)
_TRUNCATION_THRESHOLD = 8192

# Span target prefixes to keep
_RELEVANT_TARGET_PREFIXES = (
    "workflow.build",
    "workflow.run",
    "invoke_agent",
    "chat",
    "executor.process",
)


def convert_workflow_traces(spans: List[Dict]) -> Dict:
    """Convert raw trace spans into a structured workflow document.

    Args:
        spans: List of span dicts, each with keys like ``timestamp``,
            ``target``, ``custom_dimensions``, etc.

    Returns:
        Structured dict with workflow metadata, topology, agents,
        invocations, tool executions, token usage, and
        ``parse_failed`` flag.
    """
    try:
        return _wf_convert(spans)
    except Exception:
        logger.warning("Workflow trace conversion failed; attempting raw fallback.", exc_info=True)
        raw_traces = _wf_extract_raw_fallback(spans)
        if not raw_traces:
            raise ValueError(
                "Workflow trace conversion failed and no usable "
                "invoke_agent/chat/execute_tool spans with custom_dimensions found."
            )
        return {
            "parse_failed": True,
            "raw_traces": raw_traces,
        }


def _wf_convert(spans: List[Dict]) -> Dict:
    """Internal conversion logic."""
    relevant = _wf_filter_relevant_spans(spans)
    errors = _wf_extract_errors(spans)

    build_spans = [s for s in relevant if s.get("target") == "workflow.build"]
    run_spans = [s for s in relevant if s.get("target") == "workflow.run"]
    invoke_spans = [s for s in relevant if (s.get("target") or "").startswith("invoke_agent")]
    chat_spans = [s for s in relevant if (s.get("target") or "").startswith("chat")]
    executor_spans = [s for s in relevant if (s.get("target") or "").startswith("executor.process")]

    invoke_spans.sort(key=lambda s: s.get("timestamp", ""))
    chat_spans.sort(key=lambda s: s.get("timestamp", ""))
    executor_spans.sort(key=lambda s: s.get("timestamp", ""))

    run_span = max(run_spans, key=lambda s: s.get("timestamp", "")) if run_spans else None

    metadata = _wf_extract_workflow_metadata(build_spans, run_span)
    workflow_def = metadata.get("workflow_definition", {})

    topology = _wf_build_topology(workflow_def)
    agents = _wf_extract_agents(invoke_spans, chat_spans, executor_spans)
    invocations = _wf_extract_invocations(invoke_spans)

    return {
        "workflow_id": metadata.get("workflow_id"),
        "workflow_name": metadata.get("workflow_name"),
        "topology": topology,
        "agents": agents,
        "invocations": invocations,
        "errors": errors,
        "parse_failed": False,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_RAW_FALLBACK_PREFIXES = ("invoke_agent", "chat", "execute_tool")


def _wf_extract_raw_fallback(spans: Any) -> List[Dict]:
    if not isinstance(spans, list):
        return []
    result: List[Dict] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        target = span.get("target") or ""
        if not any(target.startswith(p) for p in _RAW_FALLBACK_PREFIXES):
            continue
        cd = span.get("custom_dimensions")
        if isinstance(cd, dict) and cd:
            result.append({"target": target, "custom_dimensions": cd})
    return result


def _wf_extract_errors(spans: List[Dict]) -> List[Dict]:
    errors = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        cd = span.get("custom_dimensions") or {}
        msg = cd.get("error.message")
        if msg:
            errors.append(
                {
                    "message": str(msg),
                    "span_id": span.get("span_id", ""),
                    "timestamp": span.get("timestamp", ""),
                }
            )
    return errors


def _wf_filter_relevant_spans(spans: List[Dict]) -> List[Dict]:
    result = []
    for span in spans:
        target = span.get("target") or ""
        if not target:
            continue
        if any(target.startswith(p) for p in _RELEVANT_TARGET_PREFIXES):
            result.append(span)
    return result


def _wf_safe_parse_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return text
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        if len(value) >= _TRUNCATION_THRESHOLD:
            return {"_raw": value, "_truncated": True}
        return value


def _wf_wrap(value: Any, default: Any = None) -> Dict:
    if isinstance(value, dict) and value.get("_truncated") is True:
        return value
    return {"value": value if value is not None else default, "_truncated": False}


def _wf_extract_workflow_metadata(
    build_spans: List[Dict],
    run_span: Optional[Dict],
) -> Dict:
    result: Dict[str, Any] = {
        "workflow_id": None,
        "workflow_name": None,
        "workflow_definition": {},
    }

    run_workflow_id = None
    if run_span:
        cd = run_span.get("custom_dimensions", {})
        run_workflow_id = cd.get("workflow.id")

    candidates: List[Dict[str, Any]] = []
    for build_span in build_spans:
        cd = build_span.get("custom_dimensions", {})
        workflow_id = cd.get("workflow.id")
        workflow_name = cd.get("workflow_builder.name") or cd.get("workflow.name")
        parsed_definition = _wf_safe_parse_json(cd.get("workflow.definition", ""))
        if not isinstance(parsed_definition, dict):
            parsed_definition = {}
        candidates.append(
            {
                "timestamp": build_span.get("timestamp", ""),
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "workflow_definition": parsed_definition,
            }
        )

    selected: Optional[Dict[str, Any]] = None
    if run_workflow_id:
        selected = next((c for c in candidates if c.get("workflow_id") == run_workflow_id), None)
    if selected is None and candidates:
        sorted_candidates = sorted(candidates, key=lambda c: c.get("timestamp", ""), reverse=True)
        selected = next((c for c in sorted_candidates if c.get("workflow_definition")), sorted_candidates[0])

    if selected:
        result["workflow_id"] = selected.get("workflow_id")
        result["workflow_name"] = selected.get("workflow_name")
        result["workflow_definition"] = selected.get("workflow_definition") or {}

    if run_span:
        cd = run_span.get("custom_dimensions", {})
        if not result["workflow_id"]:
            result["workflow_id"] = cd.get("workflow.id")
        if not result["workflow_name"]:
            result["workflow_name"] = cd.get("workflow.name")
    return result


def _wf_build_topology(workflow_definition: Dict) -> Dict:
    executors_dict = workflow_definition.get("executors", {})
    edge_groups = workflow_definition.get("edge_groups", [])

    executors = []
    for eid, einfo in executors_dict.items():
        etype = einfo.get("type", "")
        executors.append({"id": eid, "type": etype})

    edges = []
    for eg in edge_groups:
        eg_type = eg.get("type", "")
        if eg_type == "InternalEdgeGroup":
            continue
        eg_edges = eg.get("edges", [])
        if not eg_edges:
            continue
        if eg_type in ("FanOutEdgeGroup", "FanInEdgeGroup"):
            for e in eg_edges:
                edges.append(
                    {
                        "type": eg_type,
                        "source": e.get("source_id", ""),
                        "target": e.get("target_id", ""),
                    }
                )
        elif eg_type == "SwitchCaseEdgeGroup":
            for e in eg_edges:
                edge_entry: Dict[str, Any] = {
                    "type": eg_type,
                    "source": e.get("source_id", ""),
                    "target": e.get("target_id", ""),
                }
                cases = eg.get("cases")
                if cases:
                    edge_entry["cases"] = cases
                edges.append(edge_entry)
        else:
            for e in eg_edges:
                edges.append(
                    {
                        "type": eg_type,
                        "source": e.get("source_id", ""),
                        "target": e.get("target_id", ""),
                    }
                )

    return {
        "start_executor_id": workflow_definition.get("start_executor_id", ""),
        "executors": executors,
        "edges": edges,
    }


def _wf_extract_agents(
    invoke_agent_spans: List[Dict],
    chat_spans: List[Dict],
    executor_spans: List[Dict],
) -> Dict:
    agents: Dict[str, Dict] = {}
    for span in invoke_agent_spans:
        cd = span.get("custom_dimensions", {})
        agent_name = cd.get("gen_ai.agent.name", "")
        if not agent_name or agent_name in agents:
            continue
        sys_instr = _wf_safe_parse_json(cd.get("gen_ai.system_instructions"))
        tool_defs = _wf_safe_parse_json(cd.get("gen_ai.tool.definitions"))
        normalized_tools = _wf_normalize_tool_definitions(tool_defs)
        agents[agent_name] = {
            "agent_id": cd.get("gen_ai.agent.id", ""),
            "model": cd.get("gen_ai.request.model", ""),
            "system_instructions": _wf_extract_text_from_parts(sys_instr),
            "tool_definitions": normalized_tools,
        }
    _wf_merge_chat_span_data(agents, chat_spans, executor_spans)
    return agents


def _wf_merge_chat_span_data(
    agents: Dict[str, Dict],
    chat_spans: List[Dict],
    executor_spans: List[Dict],
) -> None:
    if not chat_spans or not agents:
        return
    tagged: List[tuple] = []
    for s in executor_spans:
        tagged.append(("exec", s))
    for s in chat_spans:
        tagged.append(("chat", s))
    tagged.sort(key=lambda x: x[1].get("timestamp", ""))

    current_agent_name: Optional[str] = None
    for kind, span in tagged:
        if kind == "exec":
            cd = span.get("custom_dimensions", {})
            executor_id = cd.get("executor.id", "")
            matched_agent = None
            for aname in agents:
                if executor_id == aname or executor_id.endswith("_" + aname) or executor_id.endswith(":" + aname):
                    matched_agent = aname
                    break
            current_agent_name = matched_agent
        elif kind == "chat" and current_agent_name:
            cd = span.get("custom_dimensions", {})
            agent = agents[current_agent_name]
            raw_tools = cd.get("gen_ai.tool.definitions")
            if raw_tools:
                parsed = _wf_safe_parse_json(raw_tools)
                chat_tools = _wf_normalize_tool_definitions(parsed)
                if chat_tools:
                    existing = {t.get("name") for t in agent["tool_definitions"]}
                    for tool in chat_tools:
                        name = tool.get("name")
                        if name and name not in existing:
                            agent["tool_definitions"].append(tool)
                            existing.add(name)


def _wf_extract_text_from_parts(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and value.get("_truncated"):
        return str(value.get("_raw", ""))
    if isinstance(value, list):
        texts = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("content") or item.get("text") or ""
                if text:
                    texts.append(text)
            elif isinstance(item, str):
                texts.append(item)
        return "\n".join(texts) if texts else ""
    return str(value) if value is not None else ""


def _wf_normalize_tool_definitions(tool_defs: Any) -> List[Dict]:
    if isinstance(tool_defs, dict) and tool_defs.get("_truncated"):
        return [tool_defs]
    if not isinstance(tool_defs, list):
        return []
    result = []
    for td in tool_defs:
        if not isinstance(td, dict):
            continue
        if "function" in td:
            func = td.get("function", {})
            result.append(
                {
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "parameters": func.get("parameters", {}),
                }
            )
        else:
            result.append(
                {
                    "name": td.get("name", ""),
                    "description": td.get("description", ""),
                    "parameters": td.get("parameters", {}),
                }
            )
    return result


def _wf_extract_invocations(invoke_agent_spans: List[Dict]) -> List[Dict]:
    invocations = []
    for seq, span in enumerate(invoke_agent_spans, start=1):
        cd = span.get("custom_dimensions", {})
        input_msgs = _wf_safe_parse_json(cd.get("gen_ai.input.messages"))
        output_msgs = _wf_safe_parse_json(cd.get("gen_ai.output.messages"))
        sys_instrs = _wf_extract_system_instructions_from_input(input_msgs)
        invocations.append(
            {
                "sequence": seq,
                "timestamp": span.get("timestamp", ""),
                "agent_name": cd.get("gen_ai.agent.name", ""),
                "agent_id": cd.get("gen_ai.agent.id", ""),
                "system_instructions": sys_instrs,
                "input_messages": _wf_wrap(input_msgs, []),
                "output_messages": _wf_wrap(output_msgs, []),
            }
        )
    return invocations


def _wf_extract_system_instructions_from_input(input_msgs: Any) -> List[str]:
    if not isinstance(input_msgs, list):
        return []
    result: List[str] = []
    for msg in input_msgs:
        if not isinstance(msg, dict) or msg.get("role") not in ("system", "developer"):
            continue
        parts = msg.get("parts", [])
        if not isinstance(parts, list):
            continue
        for part in parts:
            if isinstance(part, dict) and part.get("type") == "text":
                content = part.get("content", "")
                if content:
                    result.append(content)
    return result

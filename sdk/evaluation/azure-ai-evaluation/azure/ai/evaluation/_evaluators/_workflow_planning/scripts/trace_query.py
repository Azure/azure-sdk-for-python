# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Application Insights trace querying utilities for the bug-bash notebook.

Provides functions to:
- Build KQL queries for fetching workflow traces by trace ID
- Query Application Insights using ``LogsQueryClient``
- Process raw rows into the format expected by the trace converters
"""

import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

from .workflow_trace_converter import convert_workflow_traces

logger = logging.getLogger(__name__)

DEFAULT_LOOKBACK_HOURS = 24 * 7


def build_trace_query(trace_ids: List[str]) -> str:
    """Construct a KQL query that fetches ALL spans for the given trace IDs.

    Unlike the service version, this does NOT filter on ``invoke_agent`` —
    it returns all dependency spans so the workflow converter can see
    workflow.build, executor.process, chat, and other span types.
    """
    trace_ids_json = json.dumps(trace_ids)
    return f"""
let trace_ids = dynamic({trace_ids_json});
dependencies
| extend trace_id = operation_Id
| extend span_id = id
| where trace_id in (trace_ids)
| project timestamp, trace_id, span_id, target, duration, customDimensions
| summarize arg_max(timestamp, *) by trace_id, span_id"""


def build_full_workflow_query(trace_ids: List[str]) -> str:
    """Construct a KQL query that fetches ALL telemetry types (traces, dependencies, requests)
    for the given trace IDs — needed for full workflow reconstruction.
    """
    trace_ids_json = json.dumps(trace_ids)
    return f"""
let trace_ids = dynamic({trace_ids_json});
union traces, dependencies, requests
| where operation_Id in (trace_ids)
| summarize arg_max(timestamp, *) by operation_Id, id
| project
    timestamp,
    operation_Id,
    id,
    target,
    duration,
    customDimensions
| order by timestamp asc"""


def _normalize_dimension_value(value: Any) -> Any:
    """Convert Application Insights dynamic column values to JSON-compatible Python types."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return json.loads(stripped)
        except (json.JSONDecodeError, TypeError, ValueError):
            return value
    return value


def process_trace_rows(raw_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Process raw Application Insights data rows into intermediate format.

    Extracts fields from customDimensions and normalizes values.
    """
    rows = []
    for row_dict in raw_rows:
        custom_dimensions = _normalize_dimension_value(row_dict.get("customDimensions", {}))
        if not isinstance(custom_dimensions, dict):
            custom_dimensions = {}
        span_id = row_dict.get("span_id")
        tool_definitions = _normalize_dimension_value(custom_dimensions.get("gen_ai.tool.definitions"))
        rows.append(
            {
                "trace_id": row_dict.get("trace_id"),
                "span_id": span_id,
                "query": _normalize_dimension_value(custom_dimensions.get("gen_ai.input.messages")),
                "response": _normalize_dimension_value(custom_dimensions.get("gen_ai.output.messages")),
                "tool_definitions": tool_definitions,
                "agent_id": custom_dimensions.get("gen_ai.agent.id"),
                "agent_name": custom_dimensions.get("gen_ai.agent.name"),
                "conversation_id": custom_dimensions.get("gen_ai.conversation.id"),
            }
        )
    return rows


def process_workflow_trace_rows(raw_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Process raw App Insights rows into the span dict format expected by
    ``convert_workflow_traces``.
    """
    spans: List[Dict[str, object]] = []
    for row in raw_rows:
        custom_dims = _normalize_dimension_value(row.get("customDimensions", {}))
        if not isinstance(custom_dims, dict):
            custom_dims = {}
        spans.append({
            "timestamp": row.get("timestamp"),
            "operation_id": row.get("operation_Id", ""),
            "span_id": row.get("id", ""),
            "target": row.get("target", ""),
            "duration": row.get("duration", 0),
            "custom_dimensions": custom_dims,
        })
    return spans


def query_and_convert_workflow_traces(
    connection_string: str,
    trace_ids: List[str],
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
) -> Dict:
    """Query App Insights for workflow traces and convert to structured format.

    This is the main entry point for the notebook — it queries, processes,
    and converts traces in one call.

    Args:
        connection_string: The Application Insights connection string
            (NOT the resource ID — use the workspace ID from the connection string).
        trace_ids: List of trace IDs to fetch.
        lookback_hours: Hours to look back for traces.

    Returns:
        Structured workflow document from ``convert_workflow_traces``.
    """
    raw_rows = query_traces(connection_string, trace_ids, lookback_hours)
    spans = process_workflow_trace_rows(raw_rows)
    return convert_workflow_traces(spans)


def query_traces(
    workspace_id: str,
    trace_ids: List[str],
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
) -> List[Dict[str, object]]:
    """Query Application Insights for trace data.

    Args:
        workspace_id: The Log Analytics workspace ID
            (found in App Insights > Properties > Workspace ID, or from the
            connection string's InstrumentationKey).
        trace_ids: List of trace IDs to fetch.
        lookback_hours: Hours to look back for traces.

    Returns:
        List of raw row dicts from the query result.
    """
    credential = DefaultAzureCredential()
    client = LogsQueryClient(credential=credential)

    query = build_full_workflow_query(trace_ids)
    timespan = timedelta(hours=lookback_hours)

    logger.info("Querying App Insights workspace %s for %s trace IDs...", workspace_id, len(trace_ids))

    try:
        response = client.query_workspace(
            workspace_id=workspace_id,
            query=query,
            timespan=timespan,
        )

        if response.status != LogsQueryStatus.SUCCESS:
            raise RuntimeError("Application Insights query did not succeed.")

        if not response.tables:
            logger.warning("Query returned no tables.")
            return []

        table = response.tables[0]
        column_names = [col.name if hasattr(col, "name") else col for col in table.columns]

        raw_rows = [dict(zip(column_names, row)) for row in table.rows]
        logger.info("Query returned %s rows.", len(raw_rows))
        return raw_rows
    finally:
        client.close()

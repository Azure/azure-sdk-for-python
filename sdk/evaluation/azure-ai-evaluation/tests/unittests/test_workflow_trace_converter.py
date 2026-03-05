# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json

import pytest
from azure.ai.evaluation._evaluators._workflow_planning.scripts.workflow_trace_converter import convert_workflow_traces


def _build_span(timestamp: str, target: str, custom_dimensions: dict) -> dict:
    return {
        "timestamp": timestamp,
        "target": target,
        "custom_dimensions": custom_dimensions,
    }


def _workflow_definition(
    workflow_id: str, workflow_name: str, start_executor_id: str, executors: dict, edges: list
) -> str:
    return json.dumps(
        {
            "id": workflow_id,
            "name": workflow_name,
            "start_executor_id": start_executor_id,
            "max_iterations": 100,
            "executors": executors,
            "edge_groups": [
                {
                    "id": "SingleEdgeGroup/1",
                    "type": "SingleEdgeGroup",
                    "edges": edges,
                }
            ],
            "output_executors": [list(executors.keys())[-1]],
        }
    )


@pytest.mark.unittest
class TestWorkflowTraceConverter:
    def test_selects_build_span_matching_run_workflow_id(self):
        nested_id = "nested-workflow"
        root_id = "root-workflow"

        nested_def = _workflow_definition(
            workflow_id=nested_id,
            workflow_name="NestedWorkflow",
            start_executor_id="Evaluator",
            executors={
                "Evaluator": {"id": "Evaluator", "type": "AgentExecutor"},
                "agent_request_info_executor": {
                    "id": "agent_request_info_executor",
                    "type": "AgentRequestInfoExecutor",
                },
            },
            edges=[
                {"source_id": "Evaluator", "target_id": "agent_request_info_executor"},
                {"source_id": "agent_request_info_executor", "target_id": "Evaluator"},
            ],
        )

        root_def = _workflow_definition(
            workflow_id=root_id,
            workflow_name="RootWorkflow",
            start_executor_id="input-conversation",
            executors={
                "input-conversation": {"id": "input-conversation", "type": "_InputToConversation"},
                "ReqMaster": {"id": "ReqMaster", "type": "AgentExecutor"},
                "TalentScout": {"id": "TalentScout", "type": "AgentExecutor"},
                "Evaluator": {"id": "Evaluator", "type": "AgentApprovalExecutor"},
                "Scheduler": {"id": "Scheduler", "type": "AgentExecutor"},
                "end": {"id": "end", "type": "_EndWithConversation"},
            },
            edges=[
                {"source_id": "input-conversation", "target_id": "ReqMaster"},
                {"source_id": "ReqMaster", "target_id": "TalentScout"},
                {"source_id": "TalentScout", "target_id": "Evaluator"},
                {"source_id": "Evaluator", "target_id": "Scheduler"},
                {"source_id": "Scheduler", "target_id": "end"},
            ],
        )

        spans = [
            _build_span(
                "2026-03-05T10:00:00Z",
                "workflow.build",
                {
                    "workflow.id": nested_id,
                    "workflow_builder.name": "NestedWorkflow",
                    "workflow.definition": nested_def,
                },
            ),
            _build_span(
                "2026-03-05T10:00:01Z",
                "workflow.build",
                {
                    "workflow.id": root_id,
                    "workflow_builder.name": "RootWorkflow",
                    "workflow.definition": root_def,
                },
            ),
            _build_span(
                "2026-03-05T10:00:02Z",
                "workflow.run",
                {
                    "workflow.id": root_id,
                    "workflow.name": "RootWorkflow",
                },
            ),
        ]

        result = convert_workflow_traces(spans)

        assert result["workflow_id"] == root_id
        assert result["workflow_name"] == "RootWorkflow"
        assert result["topology"]["start_executor_id"] == "input-conversation"

    def test_falls_back_to_latest_parseable_build_when_run_id_missing(self):
        spans = [
            _build_span(
                "2026-03-05T10:00:00Z",
                "workflow.build",
                {
                    "workflow.id": "first",
                    "workflow_builder.name": "FirstWorkflow",
                    "workflow.definition": "{invalid-json",
                },
            ),
            _build_span(
                "2026-03-05T10:00:01Z",
                "workflow.build",
                {
                    "workflow.id": "second",
                    "workflow_builder.name": "SecondWorkflow",
                    "workflow.definition": _workflow_definition(
                        workflow_id="second",
                        workflow_name="SecondWorkflow",
                        start_executor_id="start",
                        executors={
                            "start": {"id": "start", "type": "_InputToConversation"},
                            "end": {"id": "end", "type": "_EndWithConversation"},
                        },
                        edges=[{"source_id": "start", "target_id": "end"}],
                    ),
                },
            ),
            _build_span(
                "2026-03-05T10:00:02Z",
                "workflow.run",
                {
                    "workflow.id": "unmatched",
                    "workflow.name": "Unmatched",
                },
            ),
        ]

        result = convert_workflow_traces(spans)

        assert result["workflow_id"] == "second"
        assert result["workflow_name"] == "SecondWorkflow"
        assert result["topology"]["start_executor_id"] == "start"

    def test_output_contract_stays_stable(self):
        spans = [
            _build_span(
                "2026-03-05T10:00:00Z",
                "workflow.build",
                {
                    "workflow.id": "wf",
                    "workflow_builder.name": "Workflow",
                    "workflow.definition": _workflow_definition(
                        workflow_id="wf",
                        workflow_name="Workflow",
                        start_executor_id="start",
                        executors={
                            "start": {"id": "start", "type": "_InputToConversation"},
                            "end": {"id": "end", "type": "_EndWithConversation"},
                        },
                        edges=[{"source_id": "start", "target_id": "end"}],
                    ),
                },
            ),
            _build_span(
                "2026-03-05T10:00:01Z",
                "workflow.run",
                {
                    "workflow.id": "wf",
                    "workflow.name": "Workflow",
                },
            ),
        ]

        result = convert_workflow_traces(spans)

        assert set(result.keys()) == {
            "parse_failed",
            "workflow_id",
            "workflow_name",
            "topology",
            "agents",
            "invocations",
            "errors",
        }
        assert result["parse_failed"] is False

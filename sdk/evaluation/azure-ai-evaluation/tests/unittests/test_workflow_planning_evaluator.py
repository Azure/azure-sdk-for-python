# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from unittest.mock import MagicMock, patch

import pytest
from azure.ai.evaluation._evaluators._workflow_planning import _WorkflowPlanningEvaluator
from azure.ai.evaluation._workflows._utils import format_workflow_trace_for_eval
from azure.ai.evaluation._exceptions import ErrorCategory, EvaluationException


def _build_trace_with_repeated_history(repeated_assistant_text: str, second_invocation_assistant_text: str = None):
    if second_invocation_assistant_text is None:
        second_invocation_assistant_text = repeated_assistant_text

    return {
        "topology": {
            "executors": [{"id": "planner", "type": "assistant"}],
            "edges": [{"source": "planner", "target": "planner"}],
            "max_iterations": 2,
        },
        "invocations": [
            {
                "agent_name": "Planner",
                "sequence": 1,
                "system_instructions": ["You are a planning agent."],
                "input_messages": {
                    "value": [
                        {"role": "user", "parts": [{"type": "text", "content": "Plan my workflow."}]},
                    ]
                },
                "output_messages": {
                    "value": [
                        {
                            "role": "assistant",
                            "parts": [{"type": "text", "content": repeated_assistant_text}],
                        }
                    ]
                },
            },
            {
                "agent_name": "Planner",
                "sequence": 2,
                "system_instructions": ["You are a planning agent."],
                "input_messages": {
                    "value": [
                        {
                            "role": "assistant",
                            "parts": [
                                {"type": "text", "content": second_invocation_assistant_text},
                                {
                                    "type": "tool_call",
                                    "tool_call_id": "call_search_docs",
                                    "name": "search_docs",
                                    "arguments": '{"topic":"dedup"}',
                                },
                                {
                                    "type": "tool_call_response",
                                    "tool_call_id": "call_search_docs",
                                    "response": "doc snippet from tool",
                                },
                            ],
                        },
                        {"role": "user", "parts": [{"type": "text", "content": "Please continue with the plan."}]},
                    ]
                },
                "output_messages": {
                    "value": [
                        {
                            "role": "assistant",
                            "parts": [{"type": "text", "content": "Here is the next step."}],
                        }
                    ]
                },
            },
        ],
        "errors": [],
    }


def _build_minimal_workflow_trace():
    return {
        "topology": {"executors": [{"id": "agent", "type": "assistant"}], "edges": []},
        "agents": {"agent": {"agent_id": "agent-1", "model": "test", "system_instructions": "", "tool_definitions": []}},
        "invocations": [
            {
                "agent_name": "Agent",
                "sequence": 1,
                "system_instructions": ["sys"],
                "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "hello"}]}]},
                "output_messages": {"value": [{"role": "assistant", "parts": [{"type": "text", "content": "world"}]}]},
            }
        ],
        "errors": [],
    }


@pytest.mark.unittest
class TestWorkflowPlanningFormatter:
    def test_formatter_handles_partial_topology_without_crashing(self):
        trace = {
            "topology": {
                "executors": [
                    {"type": "assistant"},
                    {},
                    "not-a-dict",
                    {"id": "planner", "type": "assistant"},
                ],
                "edges": [
                    "bad-edge",
                    {"source": "planner", "target": "planner"},
                ],
            },
            "invocations": [],
            "errors": [],
        }

        formatted = format_workflow_trace_for_eval(trace)

        assert "[Workflow Definition]" in formatted
        assert "planner (assistant)" in formatted
        assert "planner -> planner" in formatted

    def test_dedup_enabled_removes_repeated_assistant_text_only(self):
        repeated_text = "I already answered this exact sentence."
        workflow_trace = _build_trace_with_repeated_history(repeated_text)

        formatted = format_workflow_trace_for_eval(workflow_trace)
        invocation_two = formatted.split("[Planner - Invocation 2]", maxsplit=1)[1]

        assert repeated_text in formatted
        assert repeated_text not in invocation_two
        assert "[Conversation History: prior-agent context included]" in invocation_two
        assert "Please continue with the plan." in invocation_two
        assert "[TOOL_CALL]" in invocation_two or "[Tool Call]" in invocation_two
        assert "search_docs" in invocation_two
        assert "[TOOL_RESULT] doc snippet from tool" in invocation_two or "[Tool Result] doc snippet from tool" in invocation_two

    def test_dedup_enabled_without_duplicate_removal_keeps_default_history_label(self):
        repeated_text = "I already answered this exact sentence."
        workflow_trace = _build_trace_with_repeated_history(
            repeated_assistant_text=repeated_text,
            second_invocation_assistant_text="This is different assistant carryover content.",
        )

        formatted = format_workflow_trace_for_eval(workflow_trace)
        invocation_two = formatted.split("[Planner - Invocation 2]", maxsplit=1)[1]

        assert "[Conversation History: prior-agent context included]" not in invocation_two
        assert "[Conversation History]" in invocation_two

    def test_dedup_removes_repeated_user_prompt_blocks(self):
        repeated_prompt = "Below I will present you a request."
        trace = {
            "topology": {"executors": [{"id": "manager", "type": "assistant"}], "edges": []},
            "invocations": [
                {
                    "agent_name": "Manager",
                    "sequence": 1,
                    "system_instructions": ["manager sys"],
                    "input_messages": {
                        "value": [
                            {"role": "user", "parts": [{"type": "text", "content": repeated_prompt}]},
                            {"role": "user", "parts": [{"type": "text", "content": "Primary hiring request"}]},
                        ]
                    },
                    "output_messages": {
                        "value": [{"role": "assistant", "parts": [{"type": "text", "content": "Initial manager output"}]}]
                    },
                },
                {
                    "agent_name": "Manager",
                    "sequence": 2,
                    "system_instructions": ["manager sys"],
                    "input_messages": {
                        "value": [
                            {"role": "user", "parts": [{"type": "text", "content": repeated_prompt}]},
                            {"role": "user", "parts": [{"type": "text", "content": "Continue the workflow"}]},
                        ]
                    },
                    "output_messages": {
                        "value": [{"role": "assistant", "parts": [{"type": "text", "content": "Second manager output"}]}]
                    },
                },
            ],
            "errors": [],
        }

        formatted = format_workflow_trace_for_eval(trace)
        invocation_two = formatted.split("[Manager - Invocation 2]", maxsplit=1)[1]

        assert repeated_prompt not in invocation_two
        assert "Continue the workflow" in invocation_two

    def test_dedup_removes_tool_calls_and_results_from_prior_agent(self):
        """Tool calls and tool results produced by Agent A should be stripped from Agent B's input."""
        trace = {
            "topology": {
                "executors": [{"id": "agentA", "type": "assistant"}, {"id": "agentB", "type": "assistant"}],
                "edges": [{"source": "agentA", "target": "agentB"}],
            },
            "invocations": [
                {
                    "agent_name": "AgentA",
                    "sequence": 1,
                    "system_instructions": ["You are Agent A."],
                    "input_messages": {
                        "value": [
                            {"role": "user", "parts": [{"type": "text", "content": "Hello"}]},
                        ]
                    },
                    "output_messages": {
                        "value": [
                            {
                                "role": "assistant",
                                "parts": [
                                    {
                                        "type": "tool_call",
                                        "tool_call_id": "call_lookup",
                                        "name": "lookup",
                                        "arguments": '{"q":"info"}',
                                    },
                                ],
                            },
                            {
                                "role": "tool",
                                "parts": [
                                    {
                                        "type": "tool_call_response",
                                        "tool_call_id": "call_lookup",
                                        "response": "lookup result data",
                                    },
                                ],
                            },
                            {
                                "role": "assistant",
                                "parts": [{"type": "text", "content": "AgentA final answer"}],
                            },
                        ]
                    },
                },
                {
                    "agent_name": "AgentB",
                    "sequence": 2,
                    "system_instructions": ["You are Agent B."],
                    "input_messages": {
                        "value": [
                            {"role": "user", "parts": [{"type": "text", "content": "Hello"}]},
                            # Carried over from AgentA's output:
                            {
                                "role": "assistant",
                                "parts": [
                                    {
                                        "type": "tool_call",
                                        "tool_call_id": "call_lookup",
                                        "name": "lookup",
                                        "arguments": '{"q":"info"}',
                                    },
                                ],
                            },
                            {
                                "role": "tool",
                                "parts": [
                                    {
                                        "type": "tool_call_response",
                                        "tool_call_id": "call_lookup",
                                        "response": "lookup result data",
                                    },
                                ],
                            },
                            {
                                "role": "assistant",
                                "parts": [{"type": "text", "content": "AgentA final answer"}],
                            },
                            {"role": "user", "parts": [{"type": "text", "content": "Now do step 2"}]},
                        ]
                    },
                    "output_messages": {
                        "value": [
                            {
                                "role": "assistant",
                                "parts": [{"type": "text", "content": "AgentB result"}],
                            }
                        ]
                    },
                },
            ],
            "errors": [],
        }

        formatted = format_workflow_trace_for_eval(trace)
        invocation_two = formatted.split("[AgentB - Invocation 2]", maxsplit=1)[1]

        # AgentA's tool call, tool result, and text response should all be stripped
        assert "[TOOL_CALL] lookup" not in invocation_two
        assert "[Tool Call] lookup" not in invocation_two
        assert "[TOOL_RESULT] lookup result data" not in invocation_two
        assert "[Tool Result] lookup result data" not in invocation_two
        assert "AgentA final answer" not in invocation_two
        # AgentB's own content and user messages should remain
        assert "Now do step 2" in invocation_two
        assert "AgentB result" in invocation_two
        assert "[Conversation History: prior-agent context included]" in invocation_two

    def test_dedup_accumulates_across_multiple_invocations(self):
        """Outputs from invocation 1 should still be deduped in invocation 3's input."""
        trace = {
            "topology": {
                "executors": [
                    {"id": "a", "type": "assistant"},
                    {"id": "b", "type": "assistant"},
                    {"id": "c", "type": "assistant"},
                ],
                "edges": [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}],
            },
            "invocations": [
                {
                    "agent_name": "A",
                    "sequence": 1,
                    "system_instructions": ["Agent A"],
                    "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "start"}]}]},
                    "output_messages": {
                        "value": [
                            {"role": "assistant", "parts": [{"type": "text", "content": "A output"}]},
                        ]
                    },
                },
                {
                    "agent_name": "B",
                    "sequence": 2,
                    "system_instructions": ["Agent B"],
                    "input_messages": {
                        "value": [
                            {"role": "assistant", "parts": [{"type": "text", "content": "A output"}]},
                        ]
                    },
                    "output_messages": {
                        "value": [
                            {"role": "assistant", "parts": [{"type": "text", "content": "B output"}]},
                        ]
                    },
                },
                {
                    "agent_name": "C",
                    "sequence": 3,
                    "system_instructions": ["Agent C"],
                    "input_messages": {
                        "value": [
                            # Both prior agent outputs carried into C's input
                            {"role": "assistant", "parts": [{"type": "text", "content": "A output"}]},
                            {"role": "assistant", "parts": [{"type": "text", "content": "B output"}]},
                            {"role": "user", "parts": [{"type": "text", "content": "finish"}]},
                        ]
                    },
                    "output_messages": {
                        "value": [
                            {"role": "assistant", "parts": [{"type": "text", "content": "C output"}]},
                        ]
                    },
                },
            ],
            "errors": [],
        }

        formatted = format_workflow_trace_for_eval(trace)
        invocation_three = formatted.split("[C - Invocation 3]", maxsplit=1)[1]

        # Both A and B outputs should be stripped from C's input
        assert "A output" not in invocation_three
        assert "B output" not in invocation_three
        # C's own content and user messages should remain
        assert "finish" in invocation_three
        assert "C output" in invocation_three


@pytest.mark.unittest
class TestWorkflowPlanningEvaluator:
    def test_evaluator_calls_formatter(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(
            model_config=mock_model_config,
        )

        async def flow_side_effect(timeout, **kwargs):
            assert kwargs["workflow_trace"] == "formatted trace"
            return {"llm_output": {"success": True, "explanation": "ok", "details": {}}}

        evaluator._flow = MagicMock(side_effect=flow_side_effect)
        workflow_trace = _build_minimal_workflow_trace()

        with patch(
            "azure.ai.evaluation._evaluators._workflow_planning._workflow_planning.format_workflow_trace_for_eval",
            return_value="formatted trace",
        ) as mock_formatter:
            result = evaluator(workflow_trace=workflow_trace)

        assert result[_WorkflowPlanningEvaluator._RESULT_KEY] == 1
        mock_formatter.assert_called_once_with(workflow_trace)

    def test_non_empty_workflow_errors_raises_not_applicable(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock()

        workflow_trace = {
            "topology": {},
            "invocations": [],
            "errors": [{"message": "terminal failure"}],
        }

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(workflow_trace=workflow_trace)

        assert exc_info.value.category == ErrorCategory.NOT_APPLICABLE
        evaluator._flow.assert_not_called()

    def test_workflow_trace_none_raises_missing_field(self, mock_model_config):
        """When workflow_trace is None, _do_eval raises MISSING_FIELD with a clear message."""
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(workflow_trace=None)

        assert exc_info.value.category == ErrorCategory.MISSING_FIELD
        assert "workflow_trace must be provided" in str(exc_info.value)
        evaluator._flow.assert_not_called()

    def test_workflow_trace_invalid_json_string_raises_invalid_value(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(workflow_trace="{not valid json")

        assert exc_info.value.category == ErrorCategory.INVALID_VALUE
        evaluator._flow.assert_not_called()

    def test_workflow_trace_non_dict_type_raises_invalid_value(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock()

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(workflow_trace=[1, 2, 3])

        assert exc_info.value.category == ErrorCategory.INVALID_VALUE
        evaluator._flow.assert_not_called()

    def test_workflow_trace_valid_json_string_is_parsed(self, mock_model_config):
        """A valid JSON string should be parsed into a dict and processed."""
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)

        async def flow_side_effect(timeout, **kwargs):
            return {"llm_output": {"success": True, "explanation": "ok", "details": {}}}

        evaluator._flow = MagicMock(side_effect=flow_side_effect)
        import json

        trace_dict = _build_minimal_workflow_trace()

        result = evaluator(workflow_trace=json.dumps(trace_dict))
        assert result[_WorkflowPlanningEvaluator._RESULT_KEY] == 1

    def test_llm_returns_non_dict_output_raises_failed_execution(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)

        async def flow_side_effect(timeout, **kwargs):
            return {"llm_output": "unexpected string"}

        evaluator._flow = MagicMock(side_effect=flow_side_effect)
        workflow_trace = _build_minimal_workflow_trace()

        with patch(
            "azure.ai.evaluation._evaluators._workflow_planning._workflow_planning.format_workflow_trace_for_eval",
            return_value="formatted",
        ):
            with pytest.raises(EvaluationException) as exc_info:
                evaluator(workflow_trace=workflow_trace)

        assert exc_info.value.category == ErrorCategory.FAILED_EXECUTION

    def test_llm_returns_success_as_string_true(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)

        async def flow_side_effect(timeout, **kwargs):
            return {"llm_output": {"success": "true", "explanation": "ok", "details": {}}}

        evaluator._flow = MagicMock(side_effect=flow_side_effect)
        workflow_trace = _build_minimal_workflow_trace()

        with patch(
            "azure.ai.evaluation._evaluators._workflow_planning._workflow_planning.format_workflow_trace_for_eval",
            return_value="formatted",
        ):
            result = evaluator(workflow_trace=workflow_trace)

        assert result[_WorkflowPlanningEvaluator._RESULT_KEY] == 1
        assert result["workflow_planning_result"] == "pass"

    def test_llm_returns_success_as_string_false(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)

        async def flow_side_effect(timeout, **kwargs):
            return {"llm_output": {"success": "false", "explanation": "bad", "details": {}}}

        evaluator._flow = MagicMock(side_effect=flow_side_effect)
        workflow_trace = _build_minimal_workflow_trace()

        with patch(
            "azure.ai.evaluation._evaluators._workflow_planning._workflow_planning.format_workflow_trace_for_eval",
            return_value="formatted",
        ):
            result = evaluator(workflow_trace=workflow_trace)

        assert result[_WorkflowPlanningEvaluator._RESULT_KEY] == 0
        assert result["workflow_planning_result"] == "fail"

    def test_empty_workflow_trace_raises_missing_field(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock()

        workflow_trace = {"topology": {"executors": [], "edges": []}, "agents": {}, "invocations": [], "errors": []}

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(workflow_trace=workflow_trace)

        assert exc_info.value.category == ErrorCategory.MISSING_FIELD
        assert "No traces found" in str(exc_info.value)
        evaluator._flow.assert_not_called()

    def test_empty_invocations_raises_even_if_other_trace_sections_exist(self, mock_model_config):
        evaluator = _WorkflowPlanningEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock()

        workflow_trace = {
            "topology": {"executors": [{"id": "planner", "type": "assistant"}], "edges": []},
            "agents": {"planner": {"agent_id": "a1", "model": "m", "system_instructions": "sys", "tool_definitions": []}},
            "raw_traces": [{"target": "invoke_agent", "custom_dimensions": {"gen_ai.agent.name": "planner"}}],
            "invocations": [],
            "errors": [],
        }

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(workflow_trace=workflow_trace)

        assert exc_info.value.category == ErrorCategory.MISSING_FIELD
        assert "No traces found" in str(exc_info.value)
        evaluator._flow.assert_not_called()


@pytest.mark.unittest
class TestWorkflowPlanningFormatterEdgeCases:
    def test_parse_failed_trace_formats_raw_fallback(self):
        trace = {
            "parse_failed": True,
            "raw_traces": [
                {
                    "target": "invoke_agent chat",
                    "custom_dimensions": {"gen_ai.agent.name": "AgentX", "gen_ai.input.messages": "hello"},
                }
            ],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[PARSE FAILED - Raw Traces]" in formatted
        assert "invoke_agent chat" in formatted
        assert "AgentX" in formatted

    def test_truncated_input_messages(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": ["sys"],
                    "input_messages": {"_raw": "x" * 9000, "_truncated": True},
                    "output_messages": {
                        "value": [{"role": "assistant", "parts": [{"type": "text", "content": "reply"}]}]
                    },
                }
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[TRUNCATED]" in formatted
        assert "x" in formatted

    def test_truncated_output_messages(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": ["sys"],
                    "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "hi"}]}]},
                    "output_messages": {"_raw": "y" * 9000, "_truncated": True},
                }
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[Agent Response] [TRUNCATED]" in formatted

    def test_tool_call_with_no_tool_result(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": ["sys"],
                    "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "search"}]}]},
                    "output_messages": {
                        "value": [
                            {
                                "role": "assistant",
                                "parts": [
                                    {
                                        "type": "tool_call",
                                        "tool_call_id": "call_search",
                                        "name": "search",
                                        "arguments": '{"q":"test"}',
                                    },
                                    # No tool_call_response part
                                ],
                            }
                        ]
                    },
                }
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[TOOL_CALL]" in formatted or "[Tool Call]" in formatted
        assert "search(" in formatted
        assert "[TOOL_RESULT]" not in formatted
        assert "[Tool Result]" not in formatted

    def test_tool_call_with_id_field_is_supported(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": ["sys"],
                    "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "search"}]}]},
                    "output_messages": {
                        "value": [
                            {
                                "role": "assistant",
                                "parts": [
                                    {
                                        "type": "tool_call",
                                        "id": "call_search_by_id",
                                        "name": "search",
                                        "arguments": '{"q":"test"}',
                                    },
                                ],
                            }
                        ]
                    },
                }
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[TOOL_CALL]" in formatted or "[Tool Call]" in formatted
        assert "search(" in formatted

    def test_tool_role_part_level_id_is_supported(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": ["sys"],
                    "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "search"}]}]},
                    "output_messages": {
                        "value": [
                            {
                                "role": "assistant",
                                "parts": [
                                    {
                                        "type": "tool_call",
                                        "id": "call_score_candidate",
                                        "name": "score_candidate",
                                        "arguments": '{"candidate_id":"Frank Liu","job_id":"JOB-SWE-2025-001"}',
                                    },
                                ],
                            },
                            {
                                "role": "tool",
                                "parts": [
                                    {
                                        "type": "tool_call_response",
                                        "id": "call_score_candidate",
                                        "response": "Error: Candidate 'Frank Liu' not found.",
                                    }
                                ],
                            },
                        ]
                    },
                }
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[TOOL_CALL]" in formatted or "[Tool Call]" in formatted
        assert "score_candidate(" in formatted
        assert (
            "[TOOL_RESULT] Error: Candidate 'Frank Liu' not found." in formatted
            or "[Tool Result] Error: Candidate 'Frank Liu' not found." in formatted
        )

    def test_multiple_user_inputs_in_single_invocation(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": ["sys"],
                    "input_messages": {
                        "value": [
                            {"role": "user", "parts": [{"type": "text", "content": "first question"}]},
                            {"role": "assistant", "parts": [{"type": "text", "content": "intermediate"}]},
                            {"role": "user", "parts": [{"type": "text", "content": "follow up"}]},
                        ]
                    },
                    "output_messages": {
                        "value": [{"role": "assistant", "parts": [{"type": "text", "content": "final answer"}]}]
                    },
                }
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "first question" in formatted
        assert "follow up" in formatted
        assert "final answer" in formatted

    def test_empty_invocations_list(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[Workflow Definition]" in formatted
        assert "[Workflow Completion]" in formatted
        assert "Successful" in formatted

    def test_workflow_definition_formatting(self):
        trace = {
            "topology": {
                "executors": [
                    {"id": "planner", "type": "orchestrator"},
                    {"id": "researcher", "type": "assistant"},
                ],
                "edges": [{"source": "planner", "target": "researcher"}],
            },
            "invocations": [],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "planner (orchestrator)" in formatted
        assert "researcher (assistant)" in formatted
        assert "planner -> researcher" in formatted

    def test_errors_in_completion_section(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [],
            "errors": [{"message": "Agent timeout"}, {"message": "Connection lost"}],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "Error: Agent timeout" in formatted
        assert "Error: Connection lost" in formatted

    def test_system_prompt_dedup_across_same_agent(self):
        """System prompt should appear once for the first invocation of an agent,
        then '[System Prompt: same as above]' for subsequent invocations."""
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": ["You are helpful."],
                    "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "q1"}]}]},
                    "output_messages": {"value": [{"role": "assistant", "parts": [{"type": "text", "content": "a1"}]}]},
                },
                {
                    "agent_name": "Agent",
                    "sequence": 2,
                    "system_instructions": ["You are helpful."],
                    "input_messages": {"value": [{"role": "user", "parts": [{"type": "text", "content": "q2"}]}]},
                    "output_messages": {"value": [{"role": "assistant", "parts": [{"type": "text", "content": "a2"}]}]},
                },
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert formatted.count("You are helpful.") == 1
        assert "[System Prompt: same as above]" in formatted

    def test_user_query_extracted_from_first_invocation(self):
        trace = {
            "topology": {"executors": [], "edges": []},
            "invocations": [
                {
                    "agent_name": "Agent",
                    "sequence": 1,
                    "system_instructions": [],
                    "input_messages": {
                        "value": [{"role": "user", "parts": [{"type": "text", "content": "What is the weather?"}]}]
                    },
                    "output_messages": {
                        "value": [{"role": "assistant", "parts": [{"type": "text", "content": "sunny"}]}]
                    },
                }
            ],
            "errors": [],
        }
        formatted = format_workflow_trace_for_eval(trace)
        assert "[User Input]" in formatted
        assert "What is the weather?" in formatted
